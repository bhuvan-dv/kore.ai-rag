"""
retriever.py — Vector Search
Embeds a query using the same model used during ingestion,
then searches ChromaDB for the top-K most similar chunks.

Flow:
  query string
    → embed (all-MiniLM-L6-v2)
    → ChromaDB cosine similarity search
    → list[RetrievedChunk] sorted by relevance score
"""

from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from app.ingestion.embedder import get_or_create_collection
from app.config import TOP_K, CONFIDENCE_THRESHOLD


# ---------- Result type ----------


@dataclass
class RetrievedChunk:
    content: str
    metadata: dict
    score: float  # cosine similarity: 1.0 = identical, 0.0 = unrelated
    chunk_id: str


# ---------- Core retrieval ----------

_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    """
    Embeds the query and returns the top-K most similar chunks from ChromaDB.

    ChromaDB returns distances not similarities. With cosine space:
      distance = 1 - cosine_similarity
    So we convert:  score = 1 - distance
    """

    query_embedding = _model.encode([query])[0].tolist()

    collection = get_or_create_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist, cid in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        results["ids"][0],
    ):
        score = round(1.0 - dist, 4)  # convert distance → similarity
        chunks.append(
            RetrievedChunk(content=doc, metadata=meta, score=score, chunk_id=cid)
        )

    # already sorted by ChromaDB (closest first), but make it explicit
    chunks.sort(key=lambda c: c.score, reverse=True)
    return chunks


def retrieve_above_threshold(query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    """
    Like retrieve(), but filters out chunks below CONFIDENCE_THRESHOLD.
    Returns empty list when the query has no good matches in the knowledge base.
    """
    chunks = retrieve(query, top_k=top_k)
    return [c for c in chunks if c.score >= CONFIDENCE_THRESHOLD]


# ---------- Run directly ----------
# cd backend && uv run python -m app.retrieval.retriever
if __name__ == "__main__":
    test_query = "What does Kore.ai do is a AI SaaS or some normal chatbot wrapper on chatgot with UI?"
    print(f"Query: {test_query}\n")

    results = retrieve(test_query, top_k=3)
    if not results:
        print("No results — is ChromaDB populated? Run POST /api/ingest first.")
    else:
        for i, r in enumerate(results, 1):
            print(f"[{i}] score={r.score:.4f}  id={r.chunk_id}")
            print(f"     source: {r.metadata.get('source', 'unknown')}")
            print(f"     preview: {r.content[:120]}…\n")
