"""
chunker.py
----------
Splits long document text into smaller overlapping chunks using LlamaIndex
node parsers and preserves metadata like source and page numbers.
"""
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter

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
    # 1. Base recursive character splitter (enforces character-level CHUNK_SIZE)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,  # Ensures chunks <= 200
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    chunk_counter = 0

    for doc in documents:
        text = doc.get("text", "")
        page = doc.get("page", 1)
        source = doc.get("source", "")

        # 2. Handle Markdown headers first, then pass through character splitter
        if is_markdown:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on
            )
            # Split into header sections
            header_splits = markdown_splitter.split_text(text)

            # Enforce CHUNK_SIZE on each header section
            for header_split in header_splits:
                sub_splits = text_splitter.split_text(header_split.page_content)
                for sub_text in sub_splits:
                    chunk_counter += 1
                    chunks.append(
                        {
                            "id": f"{source}_p{page}_c{chunk_counter}",
                            "text": sub_text,
                            "page": page,
                            "source": source,
                        }
                    )
        else:
            # Direct recursive splitting for raw text / PDFs
            splits = text_splitter.split_text(text)
            for sub_text in splits:
                chunk_counter += 1
                chunks.append(
                    {
                        "id": f"{source}_p{page}_c{chunk_counter}",
                        "text": sub_text,
                        "page": page,
                        "source": source,
                    }
                )

    return chunks