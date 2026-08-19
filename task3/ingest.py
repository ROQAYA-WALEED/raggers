# ingest.py
class MockDocument:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def load_pdfs(data_dir):
    # Simulates loading PDF pages
    return ["Page 1 raw text", "Page 2 raw text"]

def chunk_documents(pages):
    # Simulates splitting pages into chunks with metadata
    return [
        MockDocument(
            page_content="WHO recommends the use of drugs from any of the following three classes... as an initial treatment.",
            metadata={"document_name": "WHO_Hypertension_Guideline_2021", "page_number": 8}
        )
    ]

def build_index(chunks):
    # Simulates returning a searchable VectorDB object
    return chunks