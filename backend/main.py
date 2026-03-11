from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import HealthResponse

app = FastAPI(title="Kore.ai Knowledge Search Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Kore.ai Knowledge Search Agent API", "docs": "/docs"}


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")
