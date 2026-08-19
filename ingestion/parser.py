import re
import pymupdf4llm

def clean_medical_text(text: str) -> str:
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    text = re.sub(r'^\s*\d+\s*$\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.replace('\x00', '')
    return text

def parse_pdf_to_markdown(pdf_path: str) -> str:
    raw = pymupdf4llm.to_markdown(pdf_path)
    return clean_medical_text(raw)