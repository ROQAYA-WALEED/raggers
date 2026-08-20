import re
import pymupdf  # pip install pymupdf

def clean_medical_text(text: str) -> str:
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    text = re.sub(r'^\s*\d+\s*$\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.replace('\x00', '')
    return text

def parse_pdf_to_pages(pdf_path: str):
    """
    Extract text page by page, returning a list of (page_number, cleaned_text).
    """
    doc = pymupdf.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        cleaned = clean_medical_text(text)
        pages.append((page_num, cleaned))
    return pages