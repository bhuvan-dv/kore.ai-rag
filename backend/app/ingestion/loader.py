"""
loader.py — Document Loader
Reads files from data/documents/ and wraps them as Document objects.
The chunker and embedder consume these downstream.
"""

import os
import glob
from dataclasses import dataclass, field
from typing import Optional

from app.config import DOCUMENTS_DIR


# A dataclass is like a TypeScript interface — defines the shape of our data.
# Every loaded file becomes one Document. Later, each Document gets split into
# multiple Chunks.
@dataclass
class Document:
    content: str  # raw text from the file
    metadata: dict = field(default_factory=dict)  # source info, type, size
    doc_id: Optional[str] = None  # unique key (relative path)


def load_documents(directory: str = DOCUMENTS_DIR) -> list[Document]:
    """
    Scans the directory for supported files, reads each one,
    and returns a list of Document objects.
    """
    documents = []
    supported = ["*.md", "*.txt", "*.html"]

    for ext in supported:
        # "**" + recursive=True means: search ALL subdirectories
        pattern = os.path.join(directory, "**", ext)
        files = glob.glob(pattern, recursive=True)

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # skip empty / near-empty files
                if len(content.strip()) < 50:
                    continue

                # relative path is cleaner for display: "kore-docs/bot-builder.md"
                relative_path = os.path.relpath(file_path, directory)

                # detect source category from folder name
                source_category = (
                    "github" if "github" in relative_path.lower() else "kore_docs"
                )

                doc = Document(
                    content=content,
                    metadata={
                        "source": relative_path,
                        "source_type": os.path.splitext(file_path)[1].lstrip("."),
                        "source_category": source_category,
                        "file_size": len(content),
                    },
                    doc_id=relative_path,
                )
                documents.append(doc)

            except Exception as e:
                print(f"  ⚠ skipped {file_path}: {e}")

    print(f"✅ Loaded {len(documents)} documents from {directory}")
    return documents


# --- Run directly to test ---
# cd backend && uv run python -m app.ingestion.loader
if __name__ == "__main__":
    docs = load_documents()
    if docs:
        d = docs[0]
        print(f"  first doc: {d.doc_id}  ({d.metadata['file_size']} chars)")
    else:
        print(f"  no files found — add docs to {os.path.abspath(DOCUMENTS_DIR)}")
