from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    chroma_status: str
    document_count: int


class IngestionResponse(BaseModel):
    docs_loaded: int
    chunks_created: int
    chunks_stored: int
    status: str
