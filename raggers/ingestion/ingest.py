import yaml
import pickle
import os
from .parser import parse_pdf_to_pages
from .chunker import chunk_pages
from ..embeddings.embedder import get_embedding_model
from ..vectorstore.chroma.chroma_store import ChromaStore

def get_project_root():
    # This file is at .../raggers/ingestion/ingest.py
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def run_ingestion(config_path: str = r"C:\Users\dell\OneDrive\Desktop\c++ folder\Ai hacathon creativa\raggers\config.yaml"):
    project_root = get_project_root()
    
    # Resolve config path
    if not os.path.isabs(config_path):
        config_path = os.path.join(project_root, config_path)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Ensure assets directory exists
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Resolve input/output paths
    pdf_path = os.path.join(project_root, config['pdf_path'])
    markdown_path = os.path.join(project_root, config['markdown_path'])

    print("📄 Parsing PDF page by page...")
    pages = parse_pdf_to_pages(pdf_path)

    print("✂️  Chunking per page (with header detection)...")
    nodes = chunk_pages(pages, config['chunk_size'], config['chunk_overlap'])

    print("🧠 Generating Embeddings...")
    embed_model = get_embedding_model(config['embedding_model_dense'])
    texts = [node.text for node in nodes]
    metadatas = [node.metadata for node in nodes]
    ids = [f"doc_{i}" for i in range(len(nodes))]

    print("💾 Storing in Chroma...")
    chroma = ChromaStore(
        collection_name=config['collection_name'],
        persist_directory=os.path.join(project_root, "chroma_db")
    )
    embeddings = embed_model._get_text_embeddings(texts)
    chroma.add_documents(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    print("📚 Saving BM25 data...")
    bm25_path = os.path.join(project_root, "assets", "bm25_data.pkl")
    with open(bm25_path, "wb") as f:
        pickle.dump({"ids": ids, "texts": texts}, f)

    # Also save markdown for reference (optional)
    with open(markdown_path, 'w', encoding='utf-8') as f:
        # Concatenate all pages (without page markers)
        full_markdown = "\n\n".join([text for _, text in pages])
        f.write(full_markdown)

    print(f"✅ Ingestion complete! {len(nodes)} chunks ingested.")