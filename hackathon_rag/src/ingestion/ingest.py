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

from src.ingestion.parser import load_documents
from src.ingestion.chunker import chunk_documents
from src.embedder import embedder
from src.vectorstore.vector_store import vector_store


def run_ingestion(is_markdown: bool = True, model_name: str = "text-embedding-3-small") -> None:
    print("Loading documents...")
    documents = load_documents()
    print(f"  found {len(documents)} document(s)")

    if not documents:
        print("No documents found in src/assets/documents. Add some .txt/.md/.pdf files and re-run.")
        return

    print("Chunking documents...")
    chunks = chunk_documents(documents, is_markdown=is_markdown)
    print(f"  created {len(chunks)} chunk(s)")

    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed_documents(texts, model_name=model_name)

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

