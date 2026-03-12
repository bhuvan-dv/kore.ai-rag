from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import HealthResponse
from app.ingestion.embedder import get_or_create_collection, run_ingestion_pipeline

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
        return {"status": "already running", "message": "Ingestion is already in progress"}

    background_tasks.add_task(_run_ingestion_with_tracking)
    return {"status": "ingestion started", "message": "Poll /api/ingest/status for updates"}


@app.get("/api/ingest/status")
async def ingest_status():
    """Returns current ingestion state: idle | running | done | failed."""
    return _ingestion_state
