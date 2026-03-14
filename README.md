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


Things I need to do 
- implement higher and lower threahsold barrier to get this to work (done)
- Frontend citiation view should be able to see the entire paragph and from where it generates along witht he link (done)
- Generate all questions that I can ask to test out the entire project
- Generate all questions to test out both False positives and false negatives 
- Generate the entire end to end diagram 
- deploy the entire application 
How do I create a dialog task?
K
⚠️ I'm not confident in this answer. Please verify with the source documents below.

To create a dialog task, you can follow these steps:

1. Select how you want to execute the dialog task.
2. Click the "Dialog Task" option to create a new intent for the selected utterance.
3. The "Create Dialog" panel is displayed. Enter the required details and click "Proceed" to add the new intent for the utterance.

This information can be found in [Source 1: kore-docs/xo_agentai_configuration_widget-theming-layout-customization.md] and [Source 2: kore-docs/xo_analytics_automation_conversation-insights.md].
⚠ 79% confidence
5 sources
4 steps
Y
what is kore.ai? is it same as AwS?
K
⚠️ I'm not confident in this answer. Please verify with the source documents below.

Based on the provided context, I found that Kore.ai is a cloud-based conversational AI platform. However, I couldn't find any direct information stating that it is the same as AWS.

The context mentions various features and functionalities of Kore.ai, such as AgentAssist, Data streaming, Kinesis Stream, Lambda functions, and more. It also provides information on how to use these features, but does not explicitly state what Kore.ai is or its relation to AWS.

Therefore, I can only provide a partial answer: Kore.ai appears to be a conversational AI platform, but its exact nature and relationship with AWS are unclear without further information.
⚠ 41% confidence
5 sources
4 steps
Y
Where can I use Kore.ai in my company? let's say my company is a insurance agency.
K
⚠️ I'm not confident in this answer. Please verify with the source documents below.

Based on the provided context, it appears that Kore.ai can be used within various sections of the platform, including:

1. Analytics (Source 2)
2. Admin Console (Source 5)
3. Data as Service (Source 6)

These sections suggest that Kore.ai can be utilized for analyzing real-time data generated by AI Agents, managing admin and custom roles, defining security settings, and manipulating data tables.

However, I couldn't find specific information on how to use Kore.ai in a company setting, such as an insurance agency. The context only provides general information on the platform's features and functionality.

To answer your question more accurately, I would need additional information on how Kore.ai can be integrated into an insurance agency's operations, such as using AI Agents for customer service or data analysis.
⚠ 59% confidence
8 sources
5 steps
Y
Where can I use Kore.ai in my company? let's say my company is a healtcare agency.
K
⚠️ I'm not confident in this answer. Please verify with the source documents below.

Based on the provided context, it appears that Kore.ai can be used in various settings within a company. However, there is no specific information about using Kore.ai in a healthcare agency.

The context mentions the following possible use cases:

1. Custom applications: Kore.ai offers Bots SDKs as a platform-specific client library to integrate Kore.ai chat capability into custom applications.
2. Salesforce Genesys CTI: The document guides Salesforce administrators through setting up and configuring the Kore Agent AI solution, allowing agents to access Genesys Cloud features.
3. Intercom integration: The AI Agent facilitates communication and interaction between users and Intercom agents using the chat module.

To use Kore.ai in a healthcare agency, you would need to explore these options further and potentially integrate Kore.ai with other systems or platforms used by your agency.

Sources:

* [Source 1: github/Koredotcom_web-kore-sdk_README.md]
* [Source 2: kore-docs/xo_automation_intelligence_intelligence-overview.md]
* [Source 3: kore-docs/xo_app-settings_integrations_agents_configuring-the-intercom-agent.md]
* [Source 4: kore-docs/xo_administration_adminconsole.md]
* [Source 5: kore-docs/c053bf3726df33f3.md]
* [Source 6: kore-docs/xo_app-settings_integrations_agents_configuring-the-genesys-agent.md]
* [Source 7: kore-docs/xo_app-settings_dev-tools_bot-authorization_bot-authentication.md]
* [Source 8: kore-docs/xo_administration_security-and-control_byok-aws-integration.md]
⚠ 62% confidence
8 sources
5 steps
chroma run --host localhost --port 8000 --path ./data/chroma_db


backend/.venv/bin/python scripts/run_rag_evaluation.py --base-url http://127.0.0.1:5000 --timeout 180