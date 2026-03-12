"""
embedder.py — Embedding + ChromaDB Storage
Takes Chunks, embeds them via Google API, and stores in ChromaDB.

ChromaDB is a vector database: instead of SQL queries you search by
"find me vectors closest to this one" — that's semantic search.
"""

import chromadb
from chromadb.config import Settings
from google import genai
from sentence_transformers import SentenceTransformer
from app.config import (
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)


# ---------- Embedding ----------


def get_embedding_function():
    model = SentenceTransformer("all-MiniLM-L6-v2")  # 22MB, blazing fast

    def embed_texts(texts: list[str]) -> list[list[float]]:
        embeddings = model.encode(texts)
        return embeddings.tolist()

    return embed_texts


# ---------- ChromaDB helpers ----------


def get_chroma_client():
    """Persistent client — data survives server restarts."""
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(client=None):
    """
    A 'collection' in ChromaDB ≈ a table in SQL.
    All our chunks live in one collection.
    hnsw:space=cosine → similarity is measured by cosine distance.
    """
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def clear_collection():
    """Wipe the collection (use before re-ingesting)."""
    client = get_chroma_client()
    try:
        client.delete_collection(CHROMA_COLLECTION_NAME)
        print(f"🗑  Cleared collection: {CHROMA_COLLECTION_NAME}")
    except Exception:
        pass  # didn't exist yet — that's fine


# ---------- Main pipeline ----------


def embed_and_store(chunks: list, batch_size: int = 50) -> int:
    """
    Embeds all chunks and upserts into ChromaDB.

    Why batching?
      Google's API has rate limits. Sending 1000 chunks one at a time
      = 1000 API calls = slow + rate-limited. Batching 50 at a time
      = 20 calls = fast.

    upsert = insert-or-update. Safe to run multiple times.
    """
    embed_fn = get_embedding_function()
    collection = get_or_create_collection()
    stored = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        ids = [c.chunk_id for c in batch]
        texts = [c.content for c in batch]
        metas = [c.metadata for c in batch]

        try:
            embeddings = embed_fn(texts)

            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metas,
            )
            stored += len(batch)
            print(f"  📥 batch {i // batch_size + 1}: +{len(batch)}  (total {stored})")

        except Exception as e:
            print(f"  ❌ batch {i // batch_size + 1} failed: {e}")

    print(f"✅ Stored {stored} chunks in ChromaDB ({CHROMA_PERSIST_DIR})")
    return stored


# ---------- API-callable pipeline ----------


def run_ingestion_pipeline() -> dict:
    """
    Called by POST /api/ingest.
    Runs the full load → chunk → embed → store pipeline and returns stats.
    """
    from app.ingestion.loader import load_documents
    from app.ingestion.chunker import chunk_documents

    docs = load_documents()
    if not docs:
        return {"docs_loaded": 0, "chunks_created": 0, "chunks_stored": 0, "status": "no documents found — run scraper.py first"}

    chunks = chunk_documents(docs)
    clear_collection()
    stored = embed_and_store(chunks)

    return {
        "docs_loaded": len(docs),
        "chunks_created": len(chunks),
        "chunks_stored": stored,
        "status": "ok",
    }


# --- Run the full pipeline directly ---
# cd backend && uv run python -m app.ingestion.embedder
if __name__ == "__main__":
    from app.ingestion.loader import load_documents
    from app.ingestion.chunker import chunk_documents

    print("🚀 Full ingestion pipeline\n")

    docs = load_documents()
    if not docs:
        print("❌ No docs found — run scraper.py first")
        exit(1)

    chunks = chunk_documents(docs)

    clear_collection()
    total = embed_and_store(chunks)

    print(f"\n🎉 Done: {len(docs)} docs → {len(chunks)} chunks → {total} stored")
