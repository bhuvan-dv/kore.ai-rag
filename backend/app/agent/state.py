"""
state.py — Agent State

Defines the data that flows through the LangGraph agent graph.
Every node (step) in the graph receives this state, reads what it
needs, and writes its results back.

Think of it as a shared clipboard:

    START  → state has: query
    classify → state now has: query, query_type
    search   → state now has: query, query_type, search_results
    generate → state now has: query, query_type, search_results, answer
    score    → state now has: ... + confidence
    END    → return full state to caller

Why TypedDict?
  Python's way of saying "this dict MUST have these keys with these types".
  Gives us autocomplete in VS Code and catches typos early.

Why Annotated[list, operator.add]?
  Normal dict update REPLACES the value. But for reasoning steps,
  we want each node to APPEND its steps to the list.
  operator.add tells LangGraph: "merge lists by concatenation, not replacement".

  Node 1 returns: reasoning=[{step: 1, ...}]
  Node 2 returns: reasoning=[{step: 2, ...}]
  Final state:    reasoning=[{step: 1, ...}, {step: 2, ...}]  ← both kept
"""

from typing import TypedDict, Annotated, Optional
import operator


class AgentState(TypedDict):
    # ── Input (set once at the start, never changes) ──
    query: str
    top_k: int
    conversation_id: Optional[str]

    # ── Classification (set by classify_query node) ──
    query_type: str  # "simple" | "complex" | "api_lookup"
    sub_queries: list[str]  # only populated for complex queries

    # ── Retrieval (set by search nodes) ──
    search_results: list[dict]  # each dict: {content, metadata, score, chunk_id}

    # ── Tool results ──
    api_result: Optional[dict]  # populated only for api_lookup queries
    tools_used: list[str]  # e.g. ["vector_search", "api_lookup"]

    # ── Generation (set by synthesize node) ──
    answer: str
    confidence: float  # 0.0 to 1.0
    is_confident: bool  # True if confidence >= threshold

    # ── Reasoning trace (APPENDED by every node) ──
    # Annotated with operator.add so each node's steps accumulate
    reasoning: Annotated[list[dict], operator.add]
