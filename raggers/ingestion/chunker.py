# ingestion/chunker.py
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import Document, TextNode
from typing import List

def chunk_markdown(markdown_text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[TextNode]:
    """
    Split markdown by headers using MarkdownNodeParser,
    then further split long sections with SentenceSplitter.
    """
    # 1. Parse markdown into nodes with header metadata
    parser = MarkdownNodeParser()
    doc = Document(text=markdown_text, metadata={"source": "book800"})
    nodes = parser.get_nodes_from_documents([doc])  # returns List[TextNode]

    # 2. Further split nodes that exceed chunk_size
    sent_splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    final_nodes = []

    for node in nodes:
        if len(node.text) > chunk_size:
            # Split this node further
            sub_docs = [Document(text=node.text)]
            sub_nodes = sent_splitter.get_nodes_from_documents(sub_docs)
            # Inherit metadata from the parent node
            for sub in sub_nodes:
                # Merge metadata (headers) from parent
                sub.metadata.update(node.metadata)
                final_nodes.append(sub)
        else:
            final_nodes.append(node)

    return final_nodes