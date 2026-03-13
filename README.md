# Kore.ai Knowledge Search Agent

An agentic RAG (Retrieval-Augmented Generation) system for searching Kore.ai documentation and SDK references.

---

## Architecture

```text
scraper.py          → fetches docs from sitemap + GitHub READMEs → data/documents/
loader.py           → reads .md files from data/documents/ → Document objects
chunker.py          → splits documents into ~600-char chunks → Chunk objects
embedder.py         → embeds chunks via sentence-transformers → stores in ChromaDB
retriever.py        → embeds query → searches ChromaDB → returns top-K chunks
graph.py            → LangGraph agent: classify → route → search → generate → score
main.py             → FastAPI server exposing REST API
frontend/           → React UI                                                [TODO]
```

---

## Tech Stack

| Layer | Choice | Reason |
| --- | --- | --- |
| Embedding model | `all-MiniLM-L6-v2` (sentence-transformers) | Local, no API cost, 22MB, fast |
| Vector DB | ChromaDB | Embedded, no infra needed, cosine similarity |
| Agent orchestration | LangGraph | Explicit graph — each step inspectable and testable |
| LLM (dev) | Ollama (`llama3.2:3b`) | Local, unlimited, no API cost |
| LLM (prod) | Groq API | 500 tok/s, 14K req/day free tier |
| Backend | FastAPI + uvicorn | Async, auto-docs at /docs |
| Frontend | React + Vite | Assignment requirement |

---

## Project Structure

```text
kore.ai-rag/
├── backend/
│   ├── main.py                        # FastAPI app + API endpoints
│   ├── scraper.py                     # Sitemap-based doc scraper
│   ├── env.example                    # Environment variable template
│   ├── app/
│   │   ├── config.py                  # All configurable constants
│   │   ├── llm.py                     # LLM abstraction (Ollama / Groq)
│   │   ├── ingestion/
│   │   │   ├── loader.py              # Loads .md files → Document objects
│   │   │   ├── chunker.py             # Splits docs → Chunk objects
│   │   │   └── embedder.py            # Embeds + stores in ChromaDB
│   │   ├── retrieval/
│   │   │   └── retriever.py           # Vector search — cosine similarity
│   │   ├── agent/
│   │   │   ├── state.py               # AgentState dataclass (shared graph state)
│   │   │   ├── tools.py               # Agent tools: vector search, API lookup, KB lookup
│   │   │   └── graph.py               # LangGraph orchestration — all nodes + edges
│   │   └── models/
│   │       └── schemas.py             # Pydantic request/response models
│   └── pyproject.toml
└── frontend/                          # React app [TODO]
```

---

## Setup

### 1. Install dependencies

```bash
cd backend
uv sync
```

### 2. Set environment variables

Copy `backend/env.example` to `backend/.env` and fill in:

```env
ENV=development
LLM_PROVIDER=ollama          # or "groq" for production
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Scrape documents

```bash
cd backend
uv run python scraper.py
```

Fetches ~496 pages from `docs.kore.ai` sitemap + 8 GitHub SDK READMEs → saves to `data/documents/`.

### 4. Start the API server

```bash
cd backend
uv run uvicorn main:app --reload --port 5000
```

### 5. Trigger ingestion

```bash
curl -X POST http://localhost:5000/api/ingest
```

Runs in background. Poll status:

```bash
curl http://localhost:5000/api/ingest/status
```

### 6. Query the agent

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I create a bot in Kore.ai?"}'
```

---

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | API info |
| GET | `/api/health` | Health check + ChromaDB doc count |
| POST | `/api/ingest` | Start ingestion pipeline (background) |
| GET | `/api/ingest/status` | Track ingestion: idle / running / done / failed |
| POST | `/api/query` | Natural language query → answer + sources + reasoning + confidence |

### POST /api/query

**Request:**

```json
{
  "query": "How do I configure channels in Kore.ai?",
  "top_k": 5,
  "conversation_id": "optional-session-id"
}
```

**Response:**

```json
{
  "answer": "To configure channels in Kore.ai...",
  "confidence": 0.82,
  "is_confident": true,
  "sources": [
    { "source": "https://docs.kore.ai/...", "score": 0.87, "chunk_id": "...", "content": "..." }
  ],
  "reasoning": [
    { "step": 1, "action": "classify", "description": "Query classified as documentation lookup" },
    { "step": 2, "action": "search", "description": "Retrieved 5 chunks from ChromaDB", "tool_used": "vector_search" }
  ],
  "query": "How do I configure channels in Kore.ai?"
}
```

Low-confidence responses (score < 0.65) are prefixed with a warning rather than returning a hallucinated answer.

---

## Ingestion Pipeline

```text
scraper.py → data/documents/ (504 files)
    ↓
loader.py  → 504 Document objects
    ↓
chunker.py → ~27,000 Chunk objects (600 chars, 100 overlap)
    ↓
embedder.py → 384-dim vectors → ChromaDB (data/chroma_db/)
```

**Chunking config** (adjustable in `app/config.py`):

```python
CHUNK_SIZE = 600      # characters per chunk (~150 tokens)
CHUNK_OVERLAP = 100   # overlap between consecutive chunks
```

---

## Agent Pipeline

```text
POST /api/query
    ↓
classify   → determines query type (docs lookup / API question / general)
    ↓
route      → selects the right tool based on classification
    ↓
search     → vector_search | api_lookup | kb_lookup
    ↓
generate   → builds grounded prompt → calls LLM (Ollama or Groq)
    ↓
score      → computes confidence from retrieval similarity scores
    ↓
QueryResponse (answer + sources + reasoning trace + confidence)
```

**LLM config** (via env vars):

| `LLM_PROVIDER` | Model | Use case |
| --- | --- | --- |
| `ollama` (default) | `llama3.2:3b` | Local dev — unlimited, no API cost |
| `groq` | `llama-3.3-70b-versatile` | Production — 500 tok/s, free tier |

---

## What's Done / What's Next

| Component | Status |
| --- | --- |
| Scraper (sitemap-based) | Done |
| Document loader | Done |
| Chunker | Done |
| Embedder + ChromaDB storage | Done |
| Ingestion API with status tracking | Done |
| Retriever (vector search) | Done |
| LLM abstraction (Ollama / Groq) | Done |
| Agent (LangGraph — classify, route, search, generate, score) | Done |
| Confidence scoring + guardrails | Done |
| Query API endpoint | Done |
| React frontend | TODO |
| Design document | TODO |
