#!/usr/bin/env python3
"""
Extract evaluator test cases from markdown tables.

Only tables with a "Test ID" column and a question column are considered tests.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


QUESTION_HEADERS = {"test question", "exact question", "question"}


@dataclass
class ExtractedTest:
    source_file_of_test: str
    section: str
    test_id: str
    category: str
    question: str
    expected_confidence: str
    expected_mode: str
    raw_row: dict


def normalize_mode(value: str) -> str:
    v = value.strip().lower()
    if v == "rag":
        return "Plain RAG"
    if v == "agent":
        return "Agentic RAG"
    if v == "tool":
        return "Tool"
    if v == "hybrid":
        return "Hybrid"
    if "plain rag" in v:
        return "Plain RAG"
    if "agentic" in v:
        return "Agentic RAG"
    if "tool" in v:
        return "Tool"
    if "hybrid" in v:
        return "Hybrid"
    return value.strip() or "Unknown"


def parse_markdown_tables(path: Path) -> list[ExtractedTest]:
    lines = path.read_text(encoding="utf-8").splitlines()
    results: list[ExtractedTest] = []
    current_section = "Uncategorized"
    i = 0

    while i < len(lines):
        line = lines[i]
        heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading_match:
            current_section = heading_match.group(2).strip()
            i += 1
            continue

        if not line.startswith("|"):
            i += 1
            continue

        if i + 1 >= len(lines) or not lines[i + 1].startswith("|"):
            i += 1
            continue

        header = [c.strip() for c in line.strip().strip("|").split("|")]
        divider = lines[i + 1]
        if "test id" not in [h.lower() for h in header] or not any(
            qh in [h.lower() for h in header] for qh in QUESTION_HEADERS
        ):
            i += 1
            continue

        rows: list[dict] = []
        j = i + 2
        while j < len(lines) and lines[j].startswith("|"):
            cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            if len(cells) == len(header):
                rows.append(dict(zip(header, cells)))
            j += 1

        for row in rows:
            lowered = {k.lower(): v for k, v in row.items()}
            question = ""
            for qh in QUESTION_HEADERS:
                if qh in lowered:
                    question = lowered[qh].strip().strip('"')
                    break

            category = row.get("Category", "").strip() or current_section
            expected_confidence = row.get("Expected confidence", "").strip() or "Unknown"
            expected_mode = row.get("Expected handling mode", "").strip() or row.get(
                "RAG / Agent / Tool / Hybrid", ""
            ).strip()

            results.append(
                ExtractedTest(
                    source_file_of_test=str(path),
                    section=current_section,
                    test_id=row.get("Test ID", "").strip(),
                    category=category,
                    question=question,
                    expected_confidence=expected_confidence,
                    expected_mode=normalize_mode(expected_mode),
                    raw_row=row,
                )
            )

        i = j

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Markdown files to parse")
    parser.add_argument("--output", help="Optional output JSON file")
    args = parser.parse_args()

    extracted: list[ExtractedTest] = []
    for file_name in args.files:
        extracted.extend(parse_markdown_tables(Path(file_name)))

    payload = [asdict(item) for item in extracted]
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
