# Kore.ai Knowledge Search Agent

An agentic RAG (Retrieval-Augmented Generation) system for searching Kore.ai documentation and SDK references.

---

## Architecture

```text
scraper.py          → fetches docs from sitemap + GitHub READMEs → data/documents/
loader.py           → reads .md files from data/documents/ → Document objects
chunker.py          → splits documents into ~600-char chunks → Chunk objects
embedder.py         → embeds chunks via sentence-transformers → stores in ChromaDB
retriever.py        → embeds query → searches ChromaDB → returns top-K chunks  [TODO]
agent.py            → decomposes query → calls retriever → generates answer     [TODO]
main.py             → FastAPI server exposing REST API
frontend/           → React UI                                                   [TODO]
```

---

## Tech Stack

| Layer | Choice | Reason |
| --- | --- | --- |
| Embedding model | `all-MiniLM-L6-v2` (sentence-transformers) | Local, no API cost, 22MB, fast |
| Vector DB | ChromaDB | Embedded, no infra needed, cosine similarity |
| Generation model | `gemini-2.0-flash` (Google Generative AI) | Fast, capable, free tier |
| Backend | FastAPI + uvicorn | Async, auto-docs at /docs |
| Frontend | React + Vite | Assignment requirement |

---

## Project Structure

```text
kore.ai-rag/
├── backend/
│   ├── main.py                        # FastAPI app + API endpoints
│   ├── scraper.py                     # Sitemap-based doc scraper
│   ├── app/
│   │   ├── config.py                  # All configurable constants
│   │   ├── ingestion/
│   │   │   ├── loader.py              # Loads .md files → Document objects
│   │   │   ├── chunker.py             # Splits docs → Chunk objects
│   │   │   └── embedder.py            # Embeds + stores in ChromaDB
│   │   ├── retrieval/
│   │   │   └── retriever.py           # Vector search [TODO]
│   │   ├── agent/
│   │   │   └── agent.py               # Agentic reasoning [TODO]
│   │   └── models/
│   │       └── schemas.py             # Pydantic response models
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

Create `backend/.env`:

```env
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

### 5. Trigger ingestion via API

```bash
curl -X POST http://localhost:5000/api/ingest
```

Runs in background. Poll status:

```bash
curl http://localhost:5000/api/ingest/status
```

---

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | API info |
| GET | `/api/health` | Health check + ChromaDB doc count |
| POST | `/api/ingest` | Start ingestion pipeline (background) |
| GET | `/api/ingest/status` | Track ingestion: idle / running / done / failed |
| POST | `/api/search` | Search query → answer + sources [TODO] |

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

## What's Done / What's Next

| Component | Status |
| --- | --- |
| Scraper (sitemap-based) | Done |
| Document loader | Done |
| Chunker | Done |
| Embedder + ChromaDB storage | Done |
| Ingestion API with status tracking | Done |
| Retriever (vector search) | TODO |
| Agent (agentic reasoning + confidence) | TODO |
| Search API endpoint | TODO |
| React frontend | TODO |
| Design document | TODO |
