import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "kore-search-agent"
ENV = os.getenv("ENV", "development")
# --- Path ---
DOCUMENTS_DIR = "./data/documents"

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Models ---
GENERATION_MODEL = "gemini-2.0-flash"
EMBEDDING_MODEL = "gemini-embedding-001"

# --- Chunking ---
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

# --- Retrieval ---
TOP_K = 5
CONFIDENCE_THRESHOLD = 0.65

# --- ChromaDB ---
CHROMA_PERSIST_DIR = "./data/chroma_db"
CHROMA_COLLECTION_NAME = "kore_docs"
