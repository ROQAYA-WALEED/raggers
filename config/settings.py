import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_PATH = DATA_DIR / "book800.pdf"
MD_PATH = DATA_DIR / "book800.md"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# Chunking parameters
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
# Markdown headers to split on (from h1 to h4)
HEADERS_TO_SPLIT_ON = [
    ("#", "Header1"),
    ("##", "Header2"),
    ("###", "Header3"),
    ("####", "Header4"),
]

# Embedding model (can be switched)
EMBEDDING_MODEL_NAME = "zeroentropy/zembed-1"  # or "BAAI/bge-small-en-v1.5"
# For hybrid retrieval
SPARSE_WEIGHT = 0.3
DENSE_WEIGHT = 0.7

# Reranker model
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"  # or "cross-encoder/ms-marco-MiniLM-L-6-v2"
USE_RERANKER = True
TOP_K_INITIAL = 10   # number of candidates before reranking
TOP_K_FINAL = 5      # final number after reranking

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000