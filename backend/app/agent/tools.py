"""
tools.py — Agent Tools

Tools are functions the agent can call to get information.
The agent decides WHICH tool to use based on the query type.

Three tools:
  1. vector_search  — searches ChromaDB (your retriever.py)
  2. api_lookup     — mock Kore.ai API call
  3. structured_lookup — mock structured DB query (feature matrices)

Why mock tools?
  The assignment says "implement at least one additional tool such as
  a mock API call". The interface is identical to a real API — swapping
  in real HTTP calls is a config change, not an architecture change.

  Interview answer: "The agent doesn't know if data comes from a mock
  or a real endpoint. The tool abstraction makes the source swappable."
"""

import json
from app.retrieval.retriever import retrieve
from app.config import TOP_K


# ── Tool 1: Vector Search (wraps your retriever) ────────────────


def vector_search_tool(query: str, top_k: int = TOP_K) -> dict:
    """
    Searches ChromaDB for relevant documentation chunks.
    This is the PRIMARY tool — used for most queries.
    """
    results = retrieve(query, top_k=top_k)

    return {
        "tool": "vector_search",
        "results": [
            {
                "content": r.content,
                "metadata": r.metadata,
                "score": r.score,
                "chunk_id": r.chunk_id,
            }
            for r in results
        ],
    }


# ── Tool 2: Mock API Lookup ─────────────────────────────────────


def api_lookup_tool(query: str) -> dict:
    """
    Simulates Kore.ai platform API calls.

    In production: real httpx.get() to Kore.ai endpoints.
    For the assignment: realistic mock responses.

    The tool interface stays the same either way — the agent
    doesn't care where the data comes from.
    """
    q = query.lower()

    if any(w in q for w in ["version", "platform", "release"]):
        return {
            "tool": "api_lookup",
            "endpoint": "/api/v1/platform/version",
            "status": "success",
            "data": {
                "platform": "Kore.ai XO Platform",
                "version": "11.x",
                "release_date": "2024",
                "features": [
                    "Conversational AI",
                    "Process Automation",
                    "Agent AI",
                    "Search AI",
                    "GALE (Generative AI & LLM Engine)",
                ],
            },
        }

    elif any(w in q for w in ["bot", "assistant", "agent", "list"]):
        return {
            "tool": "api_lookup",
            "endpoint": "/api/v1/bots",
            "status": "success",
            "data": {
                "bots": [
                    {
                        "name": "HR Assistant",
                        "status": "active",
                        "channels": ["web", "slack"],
                    },
                    {
                        "name": "IT Helpdesk",
                        "status": "active",
                        "channels": ["teams", "web"],
                    },
                    {"name": "Sales Bot", "status": "paused", "channels": ["web"]},
                ],
                "total_count": 3,
            },
        }

    elif any(w in q for w in ["status", "health", "uptime"]):
        return {
            "tool": "api_lookup",
            "endpoint": "/api/v1/platform/health",
            "status": "success",
            "data": {
                "status": "operational",
                "uptime": "99.95%",
                "services": {
                    "nlp_engine": "healthy",
                    "bot_runtime": "healthy",
                    "analytics": "healthy",
                },
            },
        }

    elif any(w in q for w in ["api", "endpoint", "rate", "limit"]):
        return {
            "tool": "api_lookup",
            "endpoint": "/api/v1/platform/limits",
            "status": "success",
            "data": {
                "rate_limits": {
                    "requests_per_minute": 100,
                    "requests_per_day": 10000,
                },
                "auth_method": "JWT Bearer Token",
                "base_url": "https://bots.kore.ai/api",
            },
        }

    else:
        return {
            "tool": "api_lookup",
            "endpoint": "/api/v1/general",
            "status": "no_match",
            "data": {
                "message": "No specific API endpoint matched.",
                "available": ["version", "bots", "health", "rate limits"],
            },
        }


# ── Tool 3: Structured Lookup ───────────────────────────────────


def structured_lookup_tool(query: str) -> dict:
    """
    Simulates a structured database query — feature matrices,
    comparison tables, things that live in rows/columns not prose.
    """
    q = query.lower()

    if any(w in q for w in ["channel", "integration", "connect"]):
        return {
            "tool": "structured_lookup",
            "table": "supported_channels",
            "status": "success",
            "data": {
                "channels": [
                    {"name": "Web/Mobile SDK", "category": "Digital"},
                    {"name": "Slack", "category": "Enterprise"},
                    {"name": "Microsoft Teams", "category": "Enterprise"},
                    {"name": "WhatsApp", "category": "Messaging"},
                    {"name": "Facebook Messenger", "category": "Social"},
                    {"name": "Twilio SMS/Voice", "category": "Voice"},
                ],
            },
        }

    elif any(w in q for w in ["language", "nlp", "multilingual"]):
        return {
            "tool": "structured_lookup",
            "table": "supported_languages",
            "status": "success",
            "data": {
                "total_supported": 100,
                "full_nlp": ["English", "Spanish", "German", "French", "Japanese"],
                "partial_nlp": ["Chinese", "Arabic", "Korean"],
            },
        }

    elif any(w in q for w in ["plan", "pricing", "tier", "enterprise"]):
        return {
            "tool": "structured_lookup",
            "table": "platform_plans",
            "status": "success",
            "data": {
                "plans": [
                    {"name": "Standard", "sessions": "Up to 10K/month"},
                    {"name": "Enterprise", "sessions": "Unlimited"},
                    {"name": "Enterprise+", "sessions": "Unlimited + on-prem"},
                ],
            },
        }

    else:
        return {
            "tool": "structured_lookup",
            "table": "general",
            "status": "no_match",
            "data": {"available_lookups": ["channels", "languages", "plans"]},
        }


# ── Tool Registry ───────────────────────────────────────────────
# The agent graph imports this to know what tools exist.

TOOL_REGISTRY = {
    "vector_search": {
        "function": vector_search_tool,
        "description": "Search documentation using semantic similarity",
    },
    "api_lookup": {
        "function": api_lookup_tool,
        "description": "Look up platform API info, bot status, or system health",
    },
    "structured_lookup": {
        "function": structured_lookup_tool,
        "description": "Query structured data: channels, languages, pricing",
    },
}
