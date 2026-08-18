"""
chunker.py
----------
Splits long document text into smaller overlapping chunks using LlamaIndex
node parsers and preserves metadata like source and page numbers.
"""

from llama_index.core.node_parser import (
    MarkdownNodeParser,
    SentenceSplitter,
)
from llama_index.core.schema import Document
from src import config


def chunk_text(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[str]:
    """
    Splits raw text into chunks using LlamaIndex's SentenceSplitter.
    """
    text = text.strip()
    if not text:
        return []

    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)


def chunk_markdown(text: str) -> list[str]:
    """
    Splits Markdown text based on headers using LlamaIndex's MarkdownNodeParser.
    """
    text = text.strip()
    if not text:
        return []

    doc = Document(text=text)
    parser = MarkdownNodeParser()
    nodes = parser.get_nodes_from_documents([doc])
    return [node.get_content() for node in nodes]


def chunk_documents(
    documents: list[dict], is_markdown: bool = False
) -> list[dict]:
    """
    Takes document dicts {"source": ..., "text": ..., "page": ...} and returns a flat list
    of chunk dicts including 'source' and 'page' in each chunk.
    """
    all_chunks = []
    for doc in documents:
        if is_markdown:
            pieces = chunk_markdown(doc["text"])
        else:
            pieces = chunk_text(doc["text"])

        source = doc.get("source", "unknown")
        page = doc.get("page", None)

        for i, piece in enumerate(pieces):
            all_chunks.append({
                "id": f"{source}::page_{page}::chunk_{i}" if page else f"{source}::chunk_{i}",
                "source": source,
                "page": page,
                "text": piece,
            })
    return all_chunks