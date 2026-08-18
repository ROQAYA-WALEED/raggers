import config1
import os
import chromadb
from fastembed import TextEmbedding
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Page:
    def __init__(self, name, num, pag):
        
        self.metadata = {
            'document_name': name,
            'page_number': num,
            'page' : pag,
        }
        self.page_content = pag

class get_embedding_function:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name=model_name)
    
    def embed_documents(self, texts):
        return list(self.model.embed(texts))

def load_pdfs(folder_path):
    pages = []
    for pdf in folder_path.glob("*.pdf"):
        reader = PyPDFLoader(pdf).load()
        for i, page in enumerate(reader):
            pages.append(
                Page(
                    pdf.name,
                    i,
                    page.page_content
                )
            )
            print(page.page_content)

    return pages

def chunk_documents(pages):
    return  RecursiveCharacterTextSplitter(
        chunk_size=config1.CHUNK_SIZE * 4,
        chunk_overlap=config1.CHUNK_OVERLAP * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
    ).split_documents(pages)

def build_index(chunks, persist_directory="./chroma_db", batch_size=100):
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    
    collection_name = config1.COLLECTION_NAME if hasattr(config1, 'COLLECTION_NAME') else "documents"
    
    try:
        chroma_client.delete_collection(collection_name)
    except:
        pass
    
    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    embedder = get_embedding_function()
    
    # Process in batches to reduce memory usage
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        
        ids = []
        documents = []
        metadatas = []
        
        for idx, chunk in enumerate(batch_chunks):
            global_idx = i + idx
            chunk_id = f"{chunk.metadata.get('document_name', 'unknown')}_{chunk.metadata.get('page_number', global_idx)}_{global_idx}"
            
            ids.append(chunk_id)
            documents.append(chunk.page_content)
            metadatas.append(chunk.metadata)
        
        # Generate embeddings only for the current batch
        embeddings = embedder.embed_documents(documents)
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    return collection