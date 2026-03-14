# Kore.ai Knowledge Search Agent

An agentic RAG application for searching Kore.ai documentation and SDK references with source-grounded answers, reasoning traces, confidence scoring, and a React UI.

## What It Does

- Ingests Kore.ai docs and GitHub README content into a local vector store
- Retrieves relevant chunks for user questions
- Routes queries through a LangGraph agent
- Uses additional tools for API-style and structured questions
- Returns answers with:
  - confidence tiers
  - reasoning steps
  - source citations
  - clickable original source links
- Provides an evaluation harness for broad QA and FP/FN analysis

## Architecture

```text
Source docs / README files
        |
        v
scraper.py
        |
        v
loader.py -> chunker.py -> embedder.py -> ChromaDB
        |
        v
FastAPI /api/query
        |
        v
LangGraph agent
  classify -> route -> retrieve/tool-use -> synthesize -> score
        |
        v
React UI
  answer + confidence + sources + reasoning
```

## Agent Flow

```text
START
  |
  v
classify_query ---- "simple / complex / api_lookup?"
  |
  |-- simple -----> simple_rag ----------------------\
  |                                                   |
  |-- complex ----> decompose_query                   |
  |                   |                               |
  |                   v                               |
  |                 multi_search ---------------------|
  |                                                   |
  \-- api_lookup -> handle_api_lookup ----------------|
                                                      |
                                                      v
                                               synthesize_answer
                                                      |
                                                      v
                                               score_confidence
                                                      |
                                                      v
                                                     END
```

Why this design:

- Simple questions take the fastest path
- Complex questions can be decomposed and merged
- API-style questions can use mock tool data plus docs context
- Every path leaves a reasoning trace for debugging and UI visibility

## Tech Stack

| Layer | Choice |
| --- | --- |
| Frontend | React + Vite |
| Backend | FastAPI + Uvicorn |
| Orchestration | LangGraph |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector DB | ChromaDB `PersistentClient` |
| Generation | Ollama locally, Groq-ready abstraction |
| Evaluation | Custom markdown-driven evaluation harness |

## Repository Structure

```text
kore.ai-rag/
├── backend/
│   ├── main.py
│   ├── scraper.py
│   ├── env.example
│   ├── data/
│   └── app/
│       ├── config.py
│       ├── llm.py
│       ├── ingestion/
│       ├── retrieval/
│       ├── agent/
│       └── models/
├── frontend/
├── scripts/
├── evaluation_outputs/
├── TECHNICAL_DESIGN_DOCUMENT.html
├── TECHNICAL_DESIGN_DOCUMENT.docx
├── PROJECT_EVALUATION_QUESTION_BANK.md
└── FP_FN_EVALUATION_PLAN.md
```

## Backend Features

- `POST /api/ingest` runs the ingestion pipeline in the background
- `GET /api/ingest/status` reports ingestion state
- `GET /api/health` checks backend and Chroma status
- `POST /api/query` returns:
  - answer
  - sources
  - reasoning
  - confidence
  - confidence tier

The backend also resolves markdown sources back to their original docs/GitHub URLs so citations are human-verifiable in the UI.

## Confidence Model

Configured in [config.py](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/backend/app/config.py):

```python
HIGH_CONFIDENCE_THRESHOLD = 0.80
MEDIUM_CONFIDENCE_THRESHOLD = 0.65
```

Behavior:

- `>= 0.80` -> high confidence
- `0.65 - 0.79` -> medium / cautious
- `< 0.65` -> low confidence with fallback warning

Low-confidence answers are prefixed with:

```text
⚠️ I'm not confident in this answer. Please verify with the source documents below.
```

## Frontend Features

The React UI currently supports:

- chat-style question input
- answer display
- confidence badge
- source panel with:
  - match score
  - clickable original source URL
  - local markdown path
  - expandable retrieved chunk content
- reasoning panel with step-by-step trace

## Setup

### 1. Backend dependencies

```bash
cd backend
uv sync
```

### 2. Environment

Copy `backend/env.example` to `backend/.env` and configure:

```env
ENV=development
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GOOGLE_API_KEY=your_google_api_key_here
```

Notes:

- The current retriever uses `sentence-transformers`, so the embedding model must be available locally or downloadable once.
- You do not need a separate `chroma run ...` server for this project because ChromaDB is used via `PersistentClient`.

### 3. Scrape source data

```bash
cd backend
uv run python scraper.py
```

### 4. Start Ollama if using local generation

```bash
ollama serve
```

Make sure the configured model is available:

```bash
ollama list
```

### 5. Start the backend

```bash
cd backend
uv run uvicorn main:app --reload --port 5000
```

### 6. Run ingestion

```bash
curl -X POST http://localhost:5000/api/ingest
curl http://localhost:5000/api/ingest/status
```

### 7. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

## Querying the API

Example request:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I create a dialog task?","top_k":5}'
```

Example response shape:

```json
{
  "answer": "To create a dialog task...",
  "sources": [
    {
      "content": "...",
      "source": "kore-docs/...",
      "source_url": "https://docs.kore.ai/...",
      "score": 0.81,
      "chunk_id": "chunk_123"
    }
  ],
  "reasoning": [
    {
      "step": 1,
      "action": "classify_query",
      "description": "Classified as 'simple'",
      "tool_used": null
    }
  ],
  "confidence": 0.78,
  "confidence_level": "medium",
  "is_confident": false,
  "query": "How do I create a dialog task?"
}
```

## Evaluation Harness

This repo includes an automated evaluation workflow based on two markdown test banks:

- [PROJECT_EVALUATION_QUESTION_BANK.md](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/PROJECT_EVALUATION_QUESTION_BANK.md)
- [FP_FN_EVALUATION_PLAN.md](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/FP_FN_EVALUATION_PLAN.md)

Available scripts:

- [scripts/extract_test_questions.py](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/scripts/extract_test_questions.py)
- [scripts/score_rag_responses.py](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/scripts/score_rag_responses.py)
- [scripts/run_rag_evaluation.py](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/scripts/run_rag_evaluation.py)

Run the evaluation against a live backend:

```bash
backend/.venv/bin/python scripts/run_rag_evaluation.py \
  --base-url http://127.0.0.1:5000 \
  --timeout 180
```

Generated outputs go to `evaluation_outputs/`:

- `rag_test_results_detailed.json`
- `rag_test_results_detailed.csv`
- `rag_test_results_summary.md`
- `rag_test_results_by_question.md`
- `rag_failure_analysis.md`

## Technical Design Document

Submission-ready design docs are included here:

- [TECHNICAL_DESIGN_DOCUMENT.html](https://github.com/bhuvan-dv/kore.ai-rag/blob/eval/metrics/TECHNICAL_DESIGN_DOCUMENT.html)

## Current Status

Implemented:

- ingestion pipeline
- semantic retrieval
- LangGraph-based agent routing
- additional tools beyond vector search
- confidence tiers and fallback warning
- React UI with source and reasoning panels
- clickable original citations
- automated evaluation harness
- technical design document

Not yet implemented or still limited:

- hybrid search
- true conversation memory
- deployment
- production-grade reliability tuning

## Known Practical Notes

- If Ollama is not running, the backend can still start but generation requests will fail.
- Retrieval quality is sensitive to chunking configuration and source cleanliness.
- The current chunking setup favors retrieval granularity over the assignment’s approximate `~1,000` chunk target.

## License

MIT
