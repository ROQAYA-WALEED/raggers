from .parser import parse_pdf_to_markdown
from .chunker import chunk_markdown
from embeddings.embedder import get_embedding_model
from vectorstore.chroma.chroma_store import ChromaStore
import yaml

def run_ingestion(config_path: str = "config.yaml"):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # 1. Parse PDF to markdown
    markdown = parse_pdf_to_markdown(config['pdf_path'])
    with open(config['markdown_path'], 'w', encoding='utf-8') as f:
        f.write(markdown)

    # 2. Chunk
    nodes = chunk_markdown(markdown, config['chunk_size'], config['chunk_overlap'])

    # 3. Embed
    embed_model = get_embedding_model(config['embedding_model_dense'])
    # Also need to collect texts for BM25 (sparse) and store in Chroma
    texts = [node.text for node in nodes]
    metadatas = [node.metadata for node in nodes]
    ids = [f"doc_{i}" for i in range(len(nodes))]

    # 4. Store in Chroma
    chroma = ChromaStore(collection_name=config['collection_name'])
    # Get dense embeddings (batch)
    embeddings = embed_model._get_text_embeddings(texts)
    chroma.add_documents(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    # 5. Also store for BM25 (we need a separate index for sparse search)
    # We'll save texts and IDs for BM25 retrieval later
    import pickle
    with open("assets/bm25_data.pkl", "wb") as f:
        pickle.dump({"ids": ids, "texts": texts}, f)

    print(f"Ingested {len(nodes)} chunks into Chroma and BM25 store.")