#!/usr/bin/env python3
"""
Response scoring helpers for the evaluation harness.
"""

from __future__ import annotations

import math
import re
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with",
    "you",
    "your",
}

LOW_CONFIDENCE_TEXT = "i'm not confident in this answer"
LIMITATION_PHRASES = [
    "not enough information",
    "do not have enough information",
    "cannot determine",
    "can't determine",
    "not supported by the provided context",
    "not in the provided context",
    "based on the provided context",
    "available sources do not",
    "sources do not establish",
    "could not find",
]


def normalize_mode(value: str) -> str:
    v = (value or "").strip().lower()
    if v in {"rag", "plain rag"}:
        return "Plain RAG"
    if v in {"agent", "agentic rag"}:
        return "Agentic RAG"
    if v == "tool":
        return "Tool"
    if v == "hybrid":
        return "Hybrid"
    return "Unknown"


def is_unsupported_expected(test: dict[str, Any]) -> bool:
    category = (test.get("category") or "").lower()
    confidence = (test.get("expected_confidence") or "").lower()
    test_id = (test.get("test_id") or "").upper()
    if "false positive" in category:
        return True
    if test_id.endswith("B") and test_id.startswith("PAIR-"):
        return True
    if confidence == "low":
        return True
    return False


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", (text or "").lower())
        if token not in STOPWORDS
    }


def lexical_overlap(question: str, sources: list[dict[str, Any]]) -> float:
    q_tokens = tokenize(question)
    if not q_tokens or not sources:
        return 0.0

    combined = " ".join(
        " ".join(
            filter(
                None,
                [
                    src.get("content", ""),
                    src.get("source", ""),
                    src.get("source_url", ""),
                ],
            )
        )
        for src in sources
    )
    source_tokens = tokenize(combined)
    if not source_tokens:
        return 0.0
    return len(q_tokens & source_tokens) / max(len(q_tokens), 1)


def limitation_language(answer: str) -> bool:
    text = (answer or "").lower()
    return any(phrase in text for phrase in LIMITATION_PHRASES)


def detect_tools(reasoning_trace: list[dict[str, Any]]) -> list[str]:
    tools: list[str] = []
    for step in reasoning_trace or []:
        tool_value = (step.get("tool_used") or "").strip()
        if tool_value:
            parts = [p.strip() for p in tool_value.split(",")]
            tools.extend([p for p in parts if p and p not in tools])

        action = (step.get("action") or "").strip()
        if action in {"vector_search", "api_lookup", "structured_lookup"} and action not in tools:
            tools.append(action)
    return tools


def infer_actual_mode(reasoning_trace: list[dict[str, Any]], tools_used: list[str]) -> str:
    actions = {(step.get("action") or "").strip() for step in reasoning_trace or []}
    has_agentic = bool({"decompose_query", "multi_search"} & actions)
    has_tool = any(t in {"api_lookup", "structured_lookup"} for t in tools_used)
    has_vector = "vector_search" in tools_used or "vector_search" in actions

    if has_agentic and has_tool:
        return "Hybrid"
    if has_tool and has_vector:
        return "Hybrid"
    if has_agentic:
        return "Agentic RAG"
    if has_tool:
        return "Tool"
    if has_vector or reasoning_trace:
        return "Plain RAG"
    return "Unknown"


def score_grounding(question: str, sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "None"
    overlap = lexical_overlap(question, sources)
    url_count = sum(1 for s in sources if s.get("source_url"))
    if overlap >= 0.30 and url_count > 0:
        return "Strong"
    if overlap >= 0.15:
        return "Medium"
    if overlap > 0:
        return "Weak"
    return "None"


def score_calibration(
    unsupported_expected: bool,
    confidence: float | None,
    answer: str,
    grounding: str,
) -> str:
    if confidence is None:
        return "Missing"

    low_warning = LOW_CONFIDENCE_TEXT in (answer or "").lower()

    if unsupported_expected:
        if confidence >= 0.65 and not low_warning:
            return "Overconfident"
        return "Well-calibrated"

    if confidence < 0.65 or low_warning:
        return "Underconfident"
    if confidence >= 0.80 and grounding in {"Weak", "None"}:
        return "Overconfident"
    return "Well-calibrated"


def score_routing(expected_mode: str, actual_mode: str, reasoning_trace: list[dict[str, Any]]) -> str:
    expected = normalize_mode(expected_mode)
    actual = normalize_mode(actual_mode)
    if not reasoning_trace:
        return "Unknown"
    if expected == actual:
        return "Correct"
    if expected == "Hybrid" and actual in {"Agentic RAG", "Tool"}:
        return "Acceptable"
    if expected == "Agentic RAG" and actual == "Hybrid":
        return "Acceptable"
    if expected == "Plain RAG" and actual == "Agentic RAG":
        return "Acceptable"
    return "Wrong"


def score_correctness(
    unsupported_expected: bool,
    answer: str,
    confidence: float | None,
    grounding: str,
    has_error: bool,
) -> str:
    if has_error:
        return "Error"

    text = (answer or "").strip()
    low_warning = LOW_CONFIDENCE_TEXT in text.lower()
    limited = limitation_language(text)

    if unsupported_expected:
        if low_warning or limited or (confidence is not None and confidence < 0.65):
            return "Unsupported"
        return "Incorrect"

    if not text:
        return "Incorrect"
    if low_warning or (confidence is not None and confidence < 0.65):
        return "Partial"
    if grounding in {"Strong", "Medium"}:
        return "Correct"
    if grounding == "Weak":
        return "Partial"
    return "Incorrect"


def classify_failure_type(
    unsupported_expected: bool,
    correctness: str,
    grounding: str,
    calibration: str,
    routing: str,
    reasoning_trace: list[dict[str, Any]],
    tools_used: list[str],
    expected_mode: str,
    answer: str,
) -> str:
    text = (answer or "").lower()
    if correctness == "Error":
        return "Backend Error"
    if not reasoning_trace:
        return "Trace Missing"
    if routing == "Wrong" and normalize_mode(expected_mode) == "Tool":
        return "Tool Failure"
    if routing == "Wrong":
        return "Misclassification"
    if unsupported_expected and correctness == "Incorrect":
        if grounding in {"None", "Weak"}:
            return "Hallucination"
        if calibration == "Overconfident":
            return "Confidence Miscalibration"
        return "False Positive"
    if not unsupported_expected and correctness in {"Incorrect", "Partial"}:
        if grounding in {"None", "Weak"}:
            return "Weak Retrieval"
        if calibration == "Underconfident":
            return "False Negative"
    if grounding == "Weak":
        return "Citation Drift"
    if calibration != "Well-calibrated":
        return "Confidence Miscalibration"
    if "ollama error" in text or "groq error" in text:
        return "Backend Error"
    return "None"


def quality_score(
    correctness: str,
    grounding: str,
    calibration: str,
    routing: str,
    source_count: int,
) -> int:
    score = 10
    if correctness == "Error":
        return 0
    score += {
        "Correct": 0,
        "Unsupported": 0,
        "Partial": -3,
        "Incorrect": -6,
    }.get(correctness, -4)
    score += {
        "Strong": 0,
        "Medium": -1,
        "Weak": -3,
        "None": -5,
    }.get(grounding, -4)
    score += {
        "Well-calibrated": 0,
        "Missing": -2,
        "Underconfident": -2,
        "Overconfident": -4,
    }.get(calibration, -2)
    score += {
        "Correct": 0,
        "Acceptable": -1,
        "Unknown": -2,
        "Wrong": -3,
    }.get(routing, -2)
    if source_count == 0:
        score -= 2
    return max(0, min(10, score))


def evaluator_note(
    unsupported_expected: bool,
    correctness: str,
    grounding: str,
    calibration: str,
    routing: str,
    failure_type: str,
    source_count: int,
) -> str:
    expected_phrase = "unsupported" if unsupported_expected else "supported"
    return (
        f"Expected a {expected_phrase} outcome; got {correctness.lower()} with "
        f"{grounding.lower()} grounding, {calibration.lower()} calibration, "
        f"{routing.lower()} routing, {source_count} sources; primary issue: {failure_type.lower()}."
    )
