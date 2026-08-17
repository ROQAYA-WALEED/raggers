from pathlib import Path


# Project directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"


# Chunking configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50