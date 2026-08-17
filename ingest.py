from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdfs(data_dir: Path):
    """Load all PDF files and normalize citation metadata."""

    pdf_files = sorted(data_dir.glob("*.pdf"))

    pages = []

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        for doc in docs:
            # PyPDFLoader uses 0-indexed page numbers
            page = doc.metadata.get("page", 0)

            # Normalize metadata for citations
            doc.metadata["document_name"] = pdf_path.name
            doc.metadata["page_number"] = page + 1

            pages.append(doc)

    return pages
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(pages)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks
from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_function():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
import chromadb
from langchain_chroma import Chroma


def build_index(chunks):
    embedding_function = get_embedding_function()

    vectordb = Chroma(
        collection_name="documents",
        embedding_function=embedding_function,
        persist_directory="./chroma_db",
    )

    vectordb.add_documents(chunks)

    return vectordb