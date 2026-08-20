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
PROCESSED_DOCUMENTS_DIR = BASE_DIR / "assets" / "documents" / "processed"      # processed docs go here
RAW_DOCUMENTS_DIR = BASE_DIR / "assets" / "documents" / "raw"      # raw docs go here
CHROMA_DIR = BASE_DIR / "vectorstore" / "chroma"        # chroma's on-disk db

# Make sure the folders we need actually exist BEFORE scanning them
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
RAW_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 📄 DYNAMIC FILE DISCOVERY HELPERS
# ==========================================
def get_file_registry(directory: Path, glob_pattern: str = "*.*") -> dict[str, Path]:
    """Scans a directory and returns a dictionary mapping filename -> full Path object."""
    if not directory.exists():
        return {}
    return {file.name: file for file in directory.glob(glob_pattern) if file.is_file()}


# Registries containing all file names and paths
RAW_FILES: dict[str, Path] = get_file_registry(RAW_DOCUMENTS_DIR, "*.pdf")
PROCESSED_FILES: dict[str, Path] = get_file_registry(PROCESSED_DOCUMENTS_DIR, "*.json")


# ==========================================
# 🎯 SELECTED TARGET FILE FOR RUNTIME
# ==========================================
# Option A: Explicitly set a active target file name
SELECTED_RAW_FILENAME = "malaria_book_pages_1_114.pdf" # you are allowed to change this variable only 
SELECTED_RAW_FILE_PATH: Path | None = RAW_FILES.get(SELECTED_RAW_FILENAME)

# Fallback 1: Direct path construction if registry missed it
if not SELECTED_RAW_FILE_PATH:
    SELECTED_RAW_FILE_PATH = RAW_DOCUMENTS_DIR / SELECTED_RAW_FILENAME

# Option B: Fallback to the first available raw PDF if specified file doesn't exist
if not SELECTED_RAW_FILE_PATH.exists() and RAW_FILES:
    SELECTED_RAW_FILE_PATH = next(iter(RAW_FILES.values()))

# --- Embedding model -----------------------------------------------------
# Small, fast, local embedding model (runs via fastembed, no API key needed)
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# --- Chunking --------------------------------------------------------------
CHUNK_SIZE = 100       # characters per chunk
CHUNK_OVERLAP = 20     # characters shared between consecutive chunks

# --- Retrieval -------------------------------------------------------------
TOP_K = 4              # how many chunks to pull back per question

# --- Generation (Anthropic Claude) ------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = "qwen2.5:1.5b"
OLLAMA = True  # Set to True if you want to use Ollama for local LLM inference
OLLAMA_LOCALHOST = "" # set to your local Ollama server URL (e.g., "http://localhost:11434") if OLLAMA is True
HUGGINGFACE = True  # Set to True if you want to use HuggingFace for local LLM inference or to load from it LLM 
MAX_TOKENS = 1000

# --- Vector store ------------------------------------------------------------
COLLECTION_NAME = "malaria_documents"

# --- device type -----------------------------------------------------
DEVICE = "cpu"