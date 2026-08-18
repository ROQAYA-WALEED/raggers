"""
config.py
---------
Central place for every setting the RAG pipeline needs.
Nothing else in the project should hardcode paths/model names —
they should all import from here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from a .env file if present (e.g. ANTHROPIC_API_KEY=...)
load_dotenv()

# --- Paths -------------------------------------------------------------
# BASE_DIR = .../hackathon_rag/src
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "assets" / "documents"      # raw source docs go here
CHROMA_DIR = BASE_DIR / "vectorstore" / "chroma"        # chroma's on-disk db

# --- Embedding model -----------------------------------------------------
# Small, fast, local embedding model (runs via fastembed, no API key needed)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- Chunking --------------------------------------------------------------
CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # characters shared between consecutive chunks

# --- Retrieval -------------------------------------------------------------
TOP_K = 4              # how many chunks to pull back per question

# --- Generation (Anthropic Claude) ------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = "medllama2:latest"
MAX_TOKENS = 1000

# --- Vector store ------------------------------------------------------------
COLLECTION_NAME = "rag_documents"

# Make sure the folders we need actually exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
