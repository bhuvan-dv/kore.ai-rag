#!/usr/bin/env python3
"""
End-to-end automated evaluation harness for the Kore.ai RAG app.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import requests
from fastapi.testclient import TestClient

from extract_test_questions import parse_markdown_tables
from score_rag_responses import (
    LOW_CONFIDENCE_TEXT,
    classify_failure_type,
    detect_tools,
    evaluator_note,
    infer_actual_mode,
    is_unsupported_expected,
    quality_score,
    score_calibration,
    score_correctness,
    score_grounding,
    score_routing,
)


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
OUTPUT_DIR = ROOT / "evaluation_outputs"
DEFAULT_TEST_FILES = [
    ROOT / "PROJECT_EVALUATION_QUESTION_BANK.md",
    ROOT / "FP_FN_EVALUATION_PLAN.md",
]
DEFAULT_PORT = 5010


def load_tests(test_files: list[Path]) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    tests: list[dict[str, Any]] = []
    by_question: dict[str, list[str]] = defaultdict(list)

    for file_path in test_files:
        for item in parse_markdown_tables(file_path):
            record = {
                "source_file_of_test": str(file_path),
                "section": item.section,
                "test_id": item.test_id,
                "category": item.category,
                "question": item.question,
                "expected_confidence": item.expected_confidence,
                "expected_mode": item.expected_mode,
            }
            tests.append(record)
            by_question[item.question.strip()].append(item.test_id)

    return tests, by_question


def start_backend(port: int) -> tuple[subprocess.Popen[str] | None, str | None]:
    python_bin = BACKEND_DIR / ".venv" / "bin" / "python"
    if not python_bin.exists():
        return None, f"Missing backend interpreter at {python_bin}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log_path = OUTPUT_DIR / "backend_server.log"
    log_file = log_path.open("w", encoding="utf-8")
    cmd = [str(python_bin), "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)]
    env = os.environ.copy()
    # Force offline startup so a previously cached embedding model is used
    # instead of making metadata calls to Hugging Face during import.
    env.setdefault("HF_HUB_OFFLINE", "1")
    env.setdefault("TRANSFORMERS_OFFLINE", "1")
    proc = subprocess.Popen(
        cmd,
        cwd=BACKEND_DIR,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )

    health_url = f"http://127.0.0.1:{port}/api/health"
    for _ in range(60):
        if proc.poll() is not None:
            log_file.close()
            return None, f"Backend exited early. See {log_path}"
        try:
            resp = requests.get(health_url, timeout=3)
            if resp.ok:
                log_file.close()
                return proc, None
        except Exception:
            time.sleep(1)

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    log_file.close()
    return None, f"Backend did not become healthy on {health_url}. See {log_path}"


def stop_backend(proc: subprocess.Popen[str] | None) -> None:
    if proc is None:
        return
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def create_inprocess_client() -> tuple[TestClient | None, str | None]:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
    try:
        from main import app

        return TestClient(app), None
    except Exception as exc:
        return None, f"In-process FastAPI client failed to initialize: {exc}"


def query_app(client_or_url: Any, question: str, timeout: int = 120) -> dict[str, Any]:
    if isinstance(client_or_url, TestClient):
        resp = client_or_url.post("/api/query", json={"query": question, "top_k": 5})
    else:
        resp = requests.post(
            f"{client_or_url}/api/query",
            json={"query": question, "top_k": 5},
            timeout=timeout,
        )
    resp.raise_for_status()
    return resp.json()


def blocked_outputs(tests: list[dict[str, Any]], reason: str) -> list[dict[str, Any]]:
    rows = []
    for test in tests:
        rows.append(
            {
                **test,
                "raw_response": {"blocked_reason": reason},
                "answer": "",
                "confidence": None,
                "sources": [],
                "reasoning_trace": [],
                "tools_used": [],
                "correctness": "Error",
                "grounding": "None",
                "calibration": "Missing",
                "routing": "Unknown",
                "failure_type": "Backend Error",
                "quality_score": 0,
                "evaluator_note": f"Evaluation blocked: {reason}",
            }
        )
    return rows


def evaluate_single(test: dict[str, Any], raw_response: dict[str, Any]) -> dict[str, Any]:
    answer = raw_response.get("answer", "")
    confidence = raw_response.get("confidence")
    sources = raw_response.get("sources") or []
    reasoning_trace = raw_response.get("reasoning") or []
    tools_used = detect_tools(reasoning_trace)
    actual_mode = infer_actual_mode(reasoning_trace, tools_used)
    unsupported_expected = is_unsupported_expected(test)

    answer_text = (answer or "").lower()
    has_error = any(
        marker in answer_text
        for marker in [
            "[ollama error",
            "[groq error",
            "error generating answer",
            "connection error:",
        ]
    )

    grounding = score_grounding(test["question"], sources)
    calibration = score_calibration(unsupported_expected, confidence, answer, grounding)
    routing = score_routing(test.get("expected_mode", ""), actual_mode, reasoning_trace)
    correctness = score_correctness(unsupported_expected, answer, confidence, grounding, has_error)
    failure_type = classify_failure_type(
        unsupported_expected,
        correctness,
        grounding,
        calibration,
        routing,
        reasoning_trace,
        tools_used,
        test.get("expected_mode", ""),
        answer,
    )
    score = quality_score(correctness, grounding, calibration, routing, len(sources))

    return {
        **test,
        "raw_response": raw_response,
        "answer": answer,
        "confidence": confidence,
        "sources": sources,
        "reasoning_trace": reasoning_trace,
        "tools_used": tools_used,
        "correctness": correctness,
        "grounding": grounding,
        "calibration": calibration,
        "routing": routing,
        "failure_type": failure_type,
        "quality_score": score,
        "evaluator_note": evaluator_note(
            unsupported_expected,
            correctness,
            grounding,
            calibration,
            routing,
            failure_type,
            len(sources),
        ),
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "source_file_of_test",
        "test_id",
        "category",
        "question",
        "expected_confidence",
        "expected_mode",
        "answer",
        "confidence",
        "tools_used",
        "correctness",
        "grounding",
        "calibration",
        "routing",
        "failure_type",
        "quality_score",
        "evaluator_note",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            csv_row = {k: row.get(k) for k in fields}
            csv_row["tools_used"] = ", ".join(row.get("tools_used", []))
            writer.writerow(csv_row)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    correctness_counts = Counter(row["correctness"] for row in rows)
    failure_counts = Counter(row["failure_type"] for row in rows)
    category_scores: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        category_scores[row["category"]].append(row["quality_score"])

    category_averages = {
        cat: round(sum(scores) / len(scores), 2) for cat, scores in category_scores.items()
    }
    sorted_categories = sorted(category_averages.items(), key=lambda item: item[1], reverse=True)

    pass_count = sum(1 for row in rows if row["correctness"] in {"Correct", "Unsupported"})
    partial_count = correctness_counts.get("Partial", 0)
    fail_count = correctness_counts.get("Incorrect", 0)
    error_count = correctness_counts.get("Error", 0)
    fp_count = failure_counts.get("False Positive", 0) + failure_counts.get("Hallucination", 0)
    fn_count = failure_counts.get("False Negative", 0) + failure_counts.get("Weak Retrieval", 0)

    common_failure_themes = [name for name, count in failure_counts.most_common(10) if name != "None"]
    critical_issues = sorted(
        rows,
        key=lambda row: (row["quality_score"], row["failure_type"] != "None"),
    )[:10]

    avg_score = round(sum(row["quality_score"] for row in rows) / max(len(rows), 1), 2)
    if error_count > 0:
        verdict = "Blocked / not assignment-ready: backend or dependency failures prevented reliable evaluation."
    elif fp_count > fn_count and fp_count >= 10:
        verdict = "Not assignment-ready: overconfident unsupported answers are the dominant risk."
    elif fn_count > fp_count and fn_count >= 10:
        verdict = "Partially ready but recall-limited: the system misses too many answerable questions."
    elif avg_score >= 7 and fp_count < 10 and fn_count < 10:
        verdict = "Reasonably assignment-ready with caveats: core flow works, but evaluator follow-up will focus on edge-case grounding and calibration."
    else:
        verdict = "Mixed readiness: useful prototype, but evaluator-grade reliability is not yet stable."

    return {
        "total_test_count": len(rows),
        "pass_count": pass_count,
        "partial_count": partial_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "false_positive_count": fp_count,
        "false_negative_count": fn_count,
        "common_failure_themes": common_failure_themes,
        "best_categories": sorted_categories[:5],
        "worst_categories": sorted_categories[-5:],
        "top_10_critical_issues": critical_issues,
        "final_verdict": verdict,
    }


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# RAG Evaluation Summary",
        "",
        f"- Total test count: {summary['total_test_count']}",
        f"- Pass count: {summary['pass_count']}",
        f"- Partial count: {summary['partial_count']}",
        f"- Fail count: {summary['fail_count']}",
        f"- Error count: {summary['error_count']}",
        f"- False positive count: {summary['false_positive_count']}",
        f"- False negative count: {summary['false_negative_count']}",
        "",
        "## Common Failure Themes",
        "",
    ]
    for theme in summary["common_failure_themes"]:
        lines.append(f"- {theme}")

    lines.extend(["", "## Best Categories", ""])
    for category, score in summary["best_categories"]:
        lines.append(f"- {category}: {score}")

    lines.extend(["", "## Worst Categories", ""])
    for category, score in summary["worst_categories"]:
        lines.append(f"- {category}: {score}")

    lines.extend(["", "## Top 10 Critical Issues", ""])
    for row in summary["top_10_critical_issues"]:
        lines.append(
            f"- {row['test_id']} ({row['category']}): {row['failure_type']} | score={row['quality_score']} | {row['evaluator_note']}"
        )

    lines.extend(["", "## Final Verdict", "", summary["final_verdict"], ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_by_question_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# RAG Evaluation Results By Question", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['test_id']} - {row['question']}",
                "",
                f"- Source file: {row['source_file_of_test']}",
                f"- Category: {row['category']}",
                f"- Expected confidence: {row['expected_confidence']}",
                f"- Expected mode: {row['expected_mode']}",
                f"- Correctness: {row['correctness']}",
                f"- Grounding: {row['grounding']}",
                f"- Calibration: {row['calibration']}",
                f"- Routing: {row['routing']}",
                f"- Failure type: {row['failure_type']}",
                f"- Quality score: {row['quality_score']}",
                f"- Tools used: {', '.join(row['tools_used']) if row['tools_used'] else 'None'}",
                f"- Confidence: {row['confidence']}",
                f"- Evaluator note: {row['evaluator_note']}",
                "",
                "### Answer",
                "",
                row["answer"] or "_No answer_",
                "",
                "### Sources",
                "",
            ]
        )
        if row["sources"]:
            for src in row["sources"]:
                label = src.get("source_url") or src.get("source") or "unknown"
                lines.append(f"- {label}")
        else:
            lines.append("- None")
        lines.extend(["", "### Reasoning Trace", ""])
        if row["reasoning_trace"]:
            for step in row["reasoning_trace"]:
                lines.append(
                    f"- Step {step.get('step')}: {step.get('action')} | {step.get('description')} | tool={step.get('tool_used')}"
                )
        else:
            lines.append("- None")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_failure_analysis_md(path: Path, rows: list[dict[str, Any]]) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["failure_type"]].append(row)

    lines = ["# RAG Failure Analysis", ""]
    for failure_type, items in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        if failure_type == "None":
            continue
        lines.extend([f"## {failure_type}", ""])
        for row in items[:20]:
            lines.append(
                f"- {row['test_id']} ({row['category']}): score={row['quality_score']} | confidence={row['confidence']} | {row['evaluator_note']}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-file",
        action="append",
        dest="test_files",
        help="Markdown test bank to include. Can be passed multiple times.",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--base-url", help="Use an already-running backend instead of starting one")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    test_files = [Path(p) for p in args.test_files] if args.test_files else DEFAULT_TEST_FILES
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tests, _ = load_tests(test_files)
    response_cache: dict[str, dict[str, Any]] = {}

    proc: subprocess.Popen[str] | None = None
    blocked_reason: str | None = None
    client_or_url: Any = args.base_url

    if not client_or_url:
        client_or_url, blocked_reason = create_inprocess_client()

    if not client_or_url and not blocked_reason:
        proc, blocked_reason = start_backend(args.port)
        if blocked_reason is None:
            client_or_url = f"http://127.0.0.1:{args.port}"
    try:
        if blocked_reason:
            rows = blocked_outputs(tests, blocked_reason)
        else:
            rows: list[dict[str, Any]] = []
            for idx, test in enumerate(tests, start=1):
                question = test["question"].strip()
                print(f"[{idx}/{len(tests)}] {test['test_id']} :: {question}")
                if question not in response_cache:
                    try:
                        response_cache[question] = query_app(client_or_url, question, timeout=args.timeout)
                    except Exception as exc:
                        response_cache[question] = {
                            "answer": f"[Evaluation query error: {exc}]",
                            "confidence": None,
                            "sources": [],
                            "reasoning": [],
                            "query": question,
                        }
                rows.append(evaluate_single(test, response_cache[question]))

        detailed_json = OUTPUT_DIR / "rag_test_results_detailed.json"
        detailed_csv = OUTPUT_DIR / "rag_test_results_detailed.csv"
        summary_md = OUTPUT_DIR / "rag_test_results_summary.md"
        by_question_md = OUTPUT_DIR / "rag_test_results_by_question.md"
        failure_md = OUTPUT_DIR / "rag_failure_analysis.md"

        write_json(detailed_json, rows)
        write_csv(detailed_csv, rows)
        summary = summarize(rows)
        write_summary_md(summary_md, summary)
        write_by_question_md(by_question_md, rows)
        write_failure_analysis_md(failure_md, rows)

        print(f"Wrote {detailed_json}")
        print(f"Wrote {detailed_csv}")
        print(f"Wrote {summary_md}")
        print(f"Wrote {by_question_md}")
        print(f"Wrote {failure_md}")
    finally:
        stop_backend(proc)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
