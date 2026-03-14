import os
import re

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import HealthResponse
from app.ingestion.embedder import get_or_create_collection, run_ingestion_pipeline

from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    SourceDocument,
    ReasoningStep,
)
from app.agent.graph import run_agent
from app.config import DOCUMENTS_DIR

app = FastAPI(title="Kore.ai Knowledge Search Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory ingestion state — persists for the lifetime of the server process
_ingestion_state: dict = {"status": "idle", "error": None, "result": None}

SOURCE_URL_PATTERN = re.compile(r"^\s*#?\s*Source:\s*(https?://\S+)\s*$", re.MULTILINE)


def _resolve_source_url(metadata: dict) -> str | None:
    source_url = metadata.get("source_url")
    if source_url:
        return source_url

    relative_path = metadata.get("doc_id") or metadata.get("source")
    if not relative_path:
        return None

    file_path = os.path.join(DOCUMENTS_DIR, relative_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            header = f.read(2000)
    except OSError:
        return None

    match = SOURCE_URL_PATTERN.search(header)
    return match.group(1).strip() if match else None


def _run_ingestion_with_tracking():
    """Wraps run_ingestion_pipeline() to track success/failure in _ingestion_state."""
    global _ingestion_state
    _ingestion_state = {"status": "running", "error": None, "result": None}
    try:
        result = run_ingestion_pipeline()
        _ingestion_state = {"status": "done", "error": None, "result": result}
    except Exception as e:
        _ingestion_state = {"status": "failed", "error": str(e), "result": None}


@app.get("/")
async def root():
    return {"message": "Kore.ai Knowledge Search Agent API", "docs": "/docs"}


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """System health check — also verifies ChromaDB connection."""
    try:
        collection = get_or_create_collection()
        doc_count = collection.count()
        chroma_status = "connected"
    except Exception as e:
        doc_count = 0
        chroma_status = f"error: {e}"

    return HealthResponse(
        status="healthy",
        chroma_status=chroma_status,
        document_count=doc_count,
    )


@app.post("/api/ingest")
async def ingest(background_tasks: BackgroundTasks):
    """
    Triggers the full ingestion pipeline in the background.
    Returns immediately — poll /api/ingest/status to track progress.
    """
    if _ingestion_state["status"] == "running":
        return {
            "status": "already running",
            "message": "Ingestion is already in progress",
        }

    background_tasks.add_task(_run_ingestion_with_tracking)
    return {
        "status": "ingestion started",
        "message": "Poll /api/ingest/status for updates",
    }


@app.get("/api/ingest/status")
async def ingest_status():
    """Returns current ingestion state: idle | running | done | failed."""
    return _ingestion_state


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Main endpoint — runs a question through the full agent pipeline.

    Pipeline: classify → route → search → synthesize → score
    Returns: answer + sources + reasoning trace + confidence
    """
    try:
        result = await run_agent(
            query=request.query,
            top_k=request.top_k,
            conversation_id=request.conversation_id,
        )

        # Convert raw dicts → Pydantic models for validation
        sources = [
            SourceDocument(
                content=r.get("content", ""),
                source=r.get("metadata", {}).get("source", "unknown"),
                source_url=_resolve_source_url(r.get("metadata", {})),
                score=r.get("score", 0.0),
                chunk_id=r.get("chunk_id", ""),
            )
            for r in result.get("search_results", [])
        ]

        reasoning = [
            ReasoningStep(
                step=r.get("step", 0),
                action=r.get("action", ""),
                description=r.get("description", ""),
                tool_used=r.get("tool_used"),
            )
            for r in result.get("reasoning", [])
        ]

        confidence = result.get("confidence", 0.0)
        confidence_level = result.get("confidence_level", "low")
        is_confident = result.get("is_confident", False)
        answer = result.get("answer", "Unable to generate an answer. Please try again.")

        # Guardrail: prepend warning only for low-confidence answers.
        if confidence_level == "low":
            answer = (
                "⚠️ I'm not confident in this answer. "
                "Please verify with the source documents below.\n\n" + answer
            )

        return QueryResponse(
            answer=answer,
            sources=sources,
            reasoning=reasoning,
            confidence=confidence,
            confidence_level=confidence_level,
            is_confident=is_confident,
            query=request.query,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}",
        )
