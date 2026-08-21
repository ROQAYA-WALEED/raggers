"""
ingest.py
---------
End-to-end ingestion pipeline:
  1. parse raw files in assets/documents
  2. split them into chunks
  3. embed the chunks
  4. store them in ChromaDB

Run directly with:  python -m src.ingestion.ingest
"""

import os
import pickle
from pathlib import Path
from src.ingestion.parser import load_documents
from src.vectorstore.vector_store import vector_store
from .preprocesser_and_chunker import process_pdf, save_chunks
from src.config import BASE_DIR, SELECTED_RAW_FILE_PATH, PROCESSED_DOCUMENTS_DIR, COLLECTION_NAME


# Setup directories
EMBEDDINGS_DIR = BASE_DIR / "assets" / "embeddings"
MODELS_DIR = BASE_DIR / "assets" / "models"

EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Set HF_HOME environment variable to force local model storage
os.environ["FASTEMBED_CACHE_PATH"] = str(MODELS_DIR)
os.environ["HF_HOME"] = str(MODELS_DIR)


def run_ingestion(is_markdown: bool = True, model_name: str = "text-embedding-3-small") -> None:
    #--------------------------------------resetting collection------------------------------------
    print(f"Resetting ChromaDB collection '{COLLECTION_NAME}'...")
    vector_store.reset_collection(collection_name=COLLECTION_NAME)

    #--------------------------------------LOADING------------------------------------
    print("Loading documents...")
    documents = load_documents()
    print(f"  found {len(documents)} document(s)")

    if not documents:
        print("No documents found in src/assets/documents. Add some .txt/.md/.pdf files and re-run.")
        return
    #--------------------------------------CHUNKING------------------------------------
    print("Chunking and cleaning documents...")
    if SELECTED_RAW_FILE_PATH and os.path.exists(SELECTED_RAW_FILE_PATH):
        chunks = process_pdf(SELECTED_RAW_FILE_PATH)
        save_chunks(chunks, PROCESSED_DOCUMENTS_DIR)
    else:
        print(f"ℹ️  Set SELECTED_RAW_FILE_PATH to a real file path (got: {PROCESSED_DOCUMENTS_DIR})")
    
    print(f"  created {len(chunks)} chunk(s)")
    #--------------------------------------EMBEDDING------------------------------------
    print("Embedding chunks...")
    
    # Generate cache file path based on selected input file or collection name
    file_stem = Path(SELECTED_RAW_FILE_PATH).stem if SELECTED_RAW_FILE_PATH else COLLECTION_NAME
    cache_path = EMBEDDINGS_DIR / f"{file_stem}_embeddings.pkl"

    if cache_path.exists():
        print(f"📦 Loading existing embeddings from {cache_path}...")
        with open(cache_path, "rb") as f:
            embeddings = pickle.load(f)
        print(f"  loaded {len(embeddings)} pre-computed embedding(s)")
    else:
        print(f"⚡ No cached embeddings found. Loading model from local cache ({MODELS_DIR})...")
        
        # Lazy import embedder ONLY when missing cache
        from src.embedder import embedder
        
        texts = [c["text"] for c in chunks]
        embeddings = embedder.embed_documents(texts)
        
        # Save newly created embeddings to src/assets/embeddings
        with open(cache_path, "wb") as f:
            pickle.dump(embeddings, f)
        print(f"💾 Saved embeddings to {cache_path}")

    #--------------------------------------STORING------------------------------------
    print("Storing in ChromaDB...")
    vector_store.add_chunks(chunks, embeddings)

    print(f"Done. Vector store now has {vector_store.count()} chunk(s).")


if __name__ == "__main__":
    run_ingestion(is_markdown=True)

    

    #query = "What is the main topic of the documents?"

    #print(f"Querying vector store for: '{query}'")

    #query_embedding = embedder.embed_query(query)

    #results = vector_store.query(query_embedding, top_k=3)
    #print(f"Found {len(results)} result(s):")
    


    