from pydantic import BaseModel, Field
from typing import Optional


class HealthResponse(BaseModel):
    status: str
    chroma_status: str
    document_count: int


class IngestionResponse(BaseModel):
    docs_loaded: int
    chunks_created: int
    chunks_stored: int
    status: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    conversation_id: Optional[str] = None


class SourceDocument(BaseModel):
    content: str
    source: str
    score: float
    chunk_id: str


class ReasoningStep(BaseModel):
    step: int
    action: str
    description: str
    tool_used: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDocument] = []
    reasoning: list[ReasoningStep] = []
    confidence: float
    confidence_level: str
    is_confident: bool
    query: str
