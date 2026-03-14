"""
graph.py — LangGraph Agent

The CORE of the system. Defines the agent as a state graph:

    START
      │
      ▼
    classify_query ──── "simple / complex / api_lookup?"
      │
      ├── simple ────► simple_rag ────────────────────┐
      │                                                │
      ├── complex ───► decompose_query                 │
      │                  │                             │
      │                  ▼                             │
      │                multi_search ───────────────────┤
      │                                                │
      └── api_lookup ► handle_api_lookup ──────────────┤
                                                       │
                                                       ▼
                                                synthesize_answer
                                                       │
                                                       ▼
                                                score_confidence
                                                       │
                                                       ▼
                                                      END

Why this design?
  Simple queries → fast path (1 search, 1 generation)
  Complex queries → decompose into sub-questions, search each, merge
  API queries → mock API + docs for context

  This avoids wasting compute on simple questions while handling
  complex ones thoroughly. Interview-ready justification.
"""

import json
import os
import re
from langgraph.graph import StateGraph, START, END

from app.config import DOCUMENTS_DIR, HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD
from app.llm import llm_generate
from app.agent.state import AgentState
from app.agent.tools import vector_search_tool, api_lookup_tool, structured_lookup_tool


SOURCE_URL_PATTERN = re.compile(r"^\s*#?\s*Source:\s*(https?://\S+)\s*$", re.MULTILINE)


# ═══════════════════════════════════════════════════════════════
#  GRAPH NODES — each node is a function: state → partial update
# ═══════════════════════════════════════════════════════════════


def resolve_source_reference(metadata: dict) -> str:
    source_url = metadata.get("source_url")
    if source_url:
        return source_url

    relative_path = metadata.get("doc_id") or metadata.get("source")
    if not relative_path:
        return "unknown"

    file_path = os.path.join(DOCUMENTS_DIR, relative_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            header = f.read(2000)
    except OSError:
        return relative_path

    match = SOURCE_URL_PATTERN.search(header)
    return match.group(1).strip() if match else relative_path


def classify_query(state: AgentState) -> dict:
    """
    Node 1: Classify the query type using Gemini.

    Why LLM classification instead of keyword matching?
    "Tell me about the bot API" could be api_lookup OR simple
    depending on intent. The LLM handles ambiguity better.
    """
    query = state["query"]

    prompt = f"""Classify this query into EXACTLY one category:

- "simple" → straightforward factual question, one search is enough
  Examples: "What is a dialog task?", "How do I create a bot?"

- "complex" → multi-part question needing info from multiple topics
  Examples: "Compare dialog tasks and alert tasks and explain when to use each"

- "api_lookup" → asking about API endpoints, platform status, version, rate limits
  Examples: "What are the API rate limits?", "What's the platform version?"

Query: "{query}"

Respond with ONLY the word: simple, complex, or api_lookup"""

    try:
        response = llm_generate(prompt)
        query_type = response.strip().lower().strip('"').strip("'")
        if query_type not in ("simple", "complex", "api_lookup"):
            query_type = "simple"
    except Exception as e:
        print(f"Classification error: {e}")
        query_type = "simple"

    return {
        "query_type": query_type,
        "reasoning": [
            {
                "step": 1,
                "action": "classify_query",
                "description": f"Classified as '{query_type}'",
                "tool_used": None,
            }
        ],
    }


def simple_rag(state: AgentState) -> dict:
    """
    Node 2a: Fast path — single vector search.
    Most queries go through here.
    """
    result = vector_search_tool(state["query"], top_k=state.get("top_k", 5))

    return {
        "search_results": result["results"],
        "tools_used": ["vector_search"],
        "reasoning": [
            {
                "step": 2,
                "action": "vector_search",
                "description": f"Retrieved {len(result['results'])} chunks for: '{state['query']}'",
                "tool_used": "vector_search",
            }
        ],
    }


def decompose_query(state: AgentState) -> dict:
    """
    Node 2b: Break complex query into 2-4 sub-questions.

    Example:
      "Compare dialog tasks and alert tasks"
      → ["What are dialog tasks?", "What are alert tasks?",
         "When to use dialog vs alert tasks?"]
    """
    prompt = f"""Break this complex question into 2-4 simpler sub-questions.
When answered together, they should fully address the original question.

Question: "{state['query']}"

Return ONLY a JSON array of strings. No explanation, no markdown.
Example: ["sub-question 1", "sub-question 2"]"""

    try:
        text = llm_generate(prompt)
        text = text.strip().replace("```json", "").replace("```", "").strip()
        sub_queries = json.loads(text)
        if not isinstance(sub_queries, list) or len(sub_queries) == 0:
            sub_queries = [state["query"]]
    except Exception:
        sub_queries = [state["query"]]

    return {
        "sub_queries": sub_queries,
        "reasoning": [
            {
                "step": 2,
                "action": "decompose_query",
                "description": f"Split into {len(sub_queries)} sub-questions: {sub_queries}",
                "tool_used": None,
            }
        ],
    }


def multi_search(state: AgentState) -> dict:
    """
    Node 2c: Search each sub-question, deduplicate, merge results.
    Gives better coverage for multi-part queries.
    """
    sub_queries = state.get("sub_queries", [state["query"]])
    all_results = []
    seen_ids = set()
    tools_used = ["vector_search"]

    for sq in sub_queries:
        result = vector_search_tool(sq, top_k=3)  # fewer per sub-query
        for r in result["results"]:
            if r["chunk_id"] not in seen_ids:
                all_results.append(r)
                seen_ids.add(r["chunk_id"])

    # Check if structured lookup would help
    q = state["query"].lower()
    if any(w in q for w in ["channel", "language", "plan", "pricing", "compare"]):
        sr = structured_lookup_tool(state["query"])
        if sr["status"] == "success":
            all_results.append(
                {
                    "content": json.dumps(sr["data"], indent=2),
                    "metadata": {
                        "source": f"structured_db/{sr['table']}",
                        "source_type": "structured",
                    },
                    "score": 0.9,
                    "chunk_id": f"structured_{sr['table']}",
                }
            )
            tools_used.append("structured_lookup")

    # Sort by score, keep top results
    all_results.sort(key=lambda x: x["score"], reverse=True)
    top_k = state.get("top_k", 5)
    all_results = all_results[: top_k + 3]  # keep extras for complex queries

    return {
        "search_results": all_results,
        "tools_used": tools_used,
        "reasoning": [
            {
                "step": 3,
                "action": "multi_search",
                "description": f"Searched {len(sub_queries)} sub-questions → {len(all_results)} unique chunks. Tools: {tools_used}",
                "tool_used": ", ".join(tools_used),
            }
        ],
    }


def handle_api_lookup(state: AgentState) -> dict:
    """
    Node 2d: API queries — call mock API AND search docs for context.
    Both sources feed into the synthesis step.
    """
    api_result = api_lookup_tool(state["query"])
    doc_result = vector_search_tool(state["query"], top_k=3)

    return {
        "search_results": doc_result["results"],
        "api_result": api_result,
        "tools_used": ["api_lookup", "vector_search"],
        "reasoning": [
            {
                "step": 2,
                "action": "api_lookup",
                "description": f"Called {api_result.get('endpoint', '?')} — {api_result.get('status', '?')}",
                "tool_used": "api_lookup",
            },
            {
                "step": 3,
                "action": "vector_search",
                "description": f"Also searched docs — {len(doc_result['results'])} chunks for context",
                "tool_used": "vector_search",
            },
        ],
    }


def synthesize_answer(state: AgentState) -> dict:
    """
    Node 3: Generate the final answer from retrieved context.

    This is the "G" in RAG. Gemini reads the chunks + question
    and produces a grounded answer.

    Guardrails are in the prompt:
      - Only use provided context
      - Say "I don't know" if context is insufficient
      - Cite sources with [Source N]
    """
    search_results = state.get("search_results", [])
    api_result = state.get("api_result")

    # Build context string from search results
    context_parts = []
    for i, r in enumerate(search_results):
        source = resolve_source_reference(r.get("metadata", {}))
        context_parts.append(f"[Source {i + 1}: {source}]\n{r['content']}")
    context = "\n\n---\n\n".join(context_parts)

    # Append API data if available
    api_context = ""
    if api_result and api_result.get("status") == "success":
        api_context = (
            f"\n\n[API Data: {api_result.get('endpoint', 'API')}]\n"
            f"{json.dumps(api_result.get('data', {}), indent=2)}"
        )

    prompt = f"""You are a helpful Kore.ai knowledge assistant.
Answer the user's question based ONLY on the provided context.

RULES:
1. ONLY use information from the context below. Do NOT make things up.
2. If the context doesn't fully answer the question, say what you found
   and what information is missing.
3. Cite sources using [Source N] notation.
4. Be concise but thorough.
5. Do NOT print raw local markdown file paths in the answer.
6. If you include a Sources section, list the original source URLs, not `.md` filenames.

CONTEXT:
{context}
{api_context}

QUESTION: {state['query']}

ANSWER:"""

    try:
        answer = llm_generate(prompt)
    except Exception as e:
        answer = f"Error generating answer: {e}"

    step_num = len(state.get("reasoning", [])) + 1
    return {
        "answer": answer,
        "reasoning": [
            {
                "step": step_num,
                "action": "synthesize_answer",
                "description": f"Generated answer from {len(search_results)} chunks"
                + (" + API data" if api_result else ""),
                "tool_used": "llm_generation",
            }
        ],
    }


def score_confidence(state: AgentState) -> dict:
    """
    Node 4: Calculate confidence from retrieval scores.

    Why retrieval-based confidence (not LLM self-assessment)?
    Retrieval scores are calibrated — if ChromaDB can't find relevant
    chunks, the LLM WILL hallucinate. Retrieval score is the honest
    signal. LLM "I'm 90% confident" is often miscalibrated.
    """
    search_results = state.get("search_results", [])
    api_result = state.get("api_result")

    if search_results:
        scores = [r.get("score", 0) for r in search_results]
        best = max(scores)
        avg_top3 = sum(scores[:3]) / min(len(scores), 3)
        confidence = (0.6 * best) + (0.4 * avg_top3)
    else:
        confidence = 0.0

    # Boost if API returned real data
    if api_result and api_result.get("status") == "success":
        confidence = min(1.0, confidence + 0.15)

    confidence = round(max(0.0, min(1.0, confidence)), 4)

    if confidence >= HIGH_CONFIDENCE_THRESHOLD:
        confidence_level = "high"
    elif confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    is_confident = confidence_level == "high"

    step_num = len(state.get("reasoning", [])) + 1
    if confidence_level == "high":
        label = "✅ Confident"
    elif confidence_level == "medium":
        label = "⚠️ Medium confidence"
    else:
        label = "⚠️ Low confidence"

    return {
        "confidence": confidence,
        "confidence_level": confidence_level,
        "is_confident": is_confident,
        "reasoning": [
            {
                "step": step_num,
                "action": "score_confidence",
                "description": f"{label} ({confidence:.2f})",
                "tool_used": None,
            }
        ],
    }


# ═══════════════════════════════════════════════════════════════
#  ROUTING — conditional edge that picks the path
# ═══════════════════════════════════════════════════════════════


def route_query(state: AgentState) -> str:
    """Returns the next node name based on query_type."""
    qt = state.get("query_type", "simple")
    if qt == "complex":
        return "decompose_query"
    elif qt == "api_lookup":
        return "handle_api_lookup"
    return "simple_rag"


# ═══════════════════════════════════════════════════════════════
#  BUILD + RUN
# ═══════════════════════════════════════════════════════════════


def build_graph() -> StateGraph:
    """
    Constructs and compiles the LangGraph agent.

    compile() validates the graph structure (no dangling edges),
    optimizes execution, and returns a runnable.
    """
    g = StateGraph(AgentState)

    # ── Nodes ──
    g.add_node("classify_query", classify_query)
    g.add_node("simple_rag", simple_rag)
    g.add_node("decompose_query", decompose_query)
    g.add_node("multi_search", multi_search)
    g.add_node("handle_api_lookup", handle_api_lookup)
    g.add_node("synthesize_answer", synthesize_answer)
    g.add_node("score_confidence", score_confidence)

    # ── Edges ──
    g.add_edge(START, "classify_query")

    g.add_conditional_edges(
        "classify_query",
        route_query,
        {
            "simple_rag": "simple_rag",
            "decompose_query": "decompose_query",
            "handle_api_lookup": "handle_api_lookup",
        },
    )

    # All three paths converge at synthesize → score → END
    g.add_edge("simple_rag", "synthesize_answer")
    g.add_edge("decompose_query", "multi_search")
    g.add_edge("multi_search", "synthesize_answer")
    g.add_edge("handle_api_lookup", "synthesize_answer")
    g.add_edge("synthesize_answer", "score_confidence")
    g.add_edge("score_confidence", END)

    return g.compile()


async def run_agent(query: str, top_k: int = 5, conversation_id: str = None) -> dict:
    """
    Entry point — runs a query through the full agent graph.
    Returns the final state dict.
    """
    agent = build_graph()

    initial_state = {
        "query": query,
        "top_k": top_k,
        "conversation_id": conversation_id,
        "query_type": "",
        "sub_queries": [],
        "search_results": [],
        "answer": "",
        "confidence": 0.0,
        "confidence_level": "low",
        "is_confident": False,
        "reasoning": [],
        "api_result": None,
        "tools_used": [],
    }

    return await agent.ainvoke(initial_state)


# ── Run directly to test ─────────────────────────────────────
# cd backend && uv run python -m app.agent.graph
if __name__ == "__main__":
    import asyncio

    async def test():
        queries = [
            "How do I create a dialog task?",
            "Compare dialog tasks and alert tasks in Kore.ai",
            "What is the current platform version?",
        ]
        for q in queries:
            print(f"\n{'='*60}")
            print(f"Q: {q}")
            result = await run_agent(q)
            print(f"Type: {result['query_type']}")
            print(f"Confidence: {result['confidence']:.2f} ({result['confidence_level']})")
            print(f"Tools: {result['tools_used']}")
            print(f"Steps: {len(result['reasoning'])}")
            print(f"Answer: {result['answer'][:200]}...")

    asyncio.run(test())
