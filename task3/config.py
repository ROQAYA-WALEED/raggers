# config.py
import os

# Dummy directory for the PDF files
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Fallback model name if an API key is eventually added
OPENAI_CHAT_MODEL = "gpt-4"