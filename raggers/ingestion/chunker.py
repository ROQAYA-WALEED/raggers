from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import Document, TextNode
from typing import List, Tuple

def chunk_pages(
    pages: List[Tuple[int, str]],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[TextNode]:
    """
    pages: list of (page_number, page_text)
    Returns TextNodes with metadata containing 'page' and any header info.
    """
    final_nodes = []
    header_parser = MarkdownNodeParser()      # extracts headers into metadata
    sent_splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    for page_num, page_text in pages:
        # Parse markdown headers on this page
        doc = Document(text=page_text, metadata={"page": page_num})
        header_nodes = header_parser.get_nodes_from_documents([doc])
        
        for node in header_nodes:
            # Ensure page number is in metadata
            node.metadata["page"] = page_num
            
            # If node is too long, split further with SentenceSplitter
            if len(node.text) > chunk_size:
                sub_docs = [Document(text=node.text)]
                sub_nodes = sent_splitter.get_nodes_from_documents(sub_docs)
                for sub in sub_nodes:
                    # Inherit metadata from parent
                    sub.metadata.update(node.metadata)
                    final_nodes.append(sub)
            else:
                final_nodes.append(node)

    return final_nodes