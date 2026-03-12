"""
chunker.py — Document Chunker
Splits large Documents into smaller Chunks for embedding and retrieval.

Why 600 chars / 100 overlap?
  - 600 chars ≈ 150 tokens — well under embedding model's 2048 token limit
  - small enough for precise retrieval, large enough to hold a full paragraph
  - 100 char overlap ≈ 1-2 sentences carried across boundaries, so no info is "lost"
    at the seam between two chunks
"""

from dataclasses import dataclass, field
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


@dataclass
class Chunk:
    content: str
    metadata: dict = field(default_factory=dict)
    chunk_id: Optional[str] = None


def chunk_documents(
    documents: list,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """
    Splits every Document into Chunks.

    RecursiveCharacterTextSplitter tries these separators in order:
      "\n\n"  →  paragraph break   (best split)
      "\n"    →  line break
      "## "   →  markdown H2
      "# "    →  markdown H1
      ". "    →  end of sentence
      " "     →  word boundary
      ""      →  single character   (worst split, last resort)

    So it always picks the most natural split point that keeps chunks
    under chunk_size characters.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "## ", "# ", ". ", " ", ""],
    )

    all_chunks = []
    counter = 0

    for doc in documents:
        pieces = splitter.split_text(doc.content)

        for i, text in enumerate(pieces):
            if len(text.strip()) < 20:  # skip tiny fragments
                continue

            chunk = Chunk(
                content=text.strip(),
                metadata={
                    **doc.metadata,  # inherit everything from parent doc
                    "chunk_index": i,  # which piece of this document (0, 1, 2…)
                    "total_chunks": len(pieces),
                    "chunk_size_chars": len(text),
                    "doc_id": doc.doc_id,
                },
                chunk_id=f"chunk_{counter}",
            )
            all_chunks.append(chunk)
            counter += 1

    print(f"✅ Chunked {len(documents)} docs → {len(all_chunks)} chunks")
    print(f"   config: size={chunk_size}  overlap={chunk_overlap}")
    return all_chunks


# --- Run directly to test ---
# cd backend && uv run python -m app.ingestion.chunker
if __name__ == "__main__":
    from app.ingestion.loader import load_documents

    docs = load_documents()
    if docs:
        chunks = chunk_documents(docs)
        if chunks:
            c = chunks[0]
            print(
                f"  first chunk: {c.chunk_id}  ({c.metadata['chunk_size_chars']} chars)"
            )
            print(f"  preview: {c.content[:120]}…")
