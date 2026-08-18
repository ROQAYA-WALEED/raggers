# Hackathon RAG - Medical Document Assistant

A lightweight, local Retrieval-Augmented Generation (RAG) system built to parse, index, and answer queries over custom medical documents using local embeddings and a local LLM.

---

## 📌 Features

- **Document Parsing:** Automatically reads and extracts content from `.txt`, `.md`, and `.pdf` files.
- **Local Text Chunking:** Breaks long documents into structured chunks with preserved page-level metadata using LlamaIndex.
- **Vector Search:** Persists document embeddings locally using ChromaDB for fast semantic search.
- **API & Web Interface:** Includes a FastAPI backend (`api/`) and a Streamlit UI (`app.py`) for multi-turn chat interactions with document citations.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.9+ installed and running on your system.

### 2. Clone Repository & Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### 3. Setup Environment
Create a `.env` file in the root directory (if needed for local environment settings):
```bash
touch .env
```

---

## 🚀 How to Run

### Step 1: Add Source Documents
Place all target documents (`.pdf`, `.txt`, or `.md`) inside the input directory:
```
src/assets/documents/
```

### Step 2: Run Data Ingestion Pipeline
Parse documents, generate embeddings, and populate the local ChromaDB vector store:
```bash
python -m src.ingestion.ingest
```

### Step 3: Launch Web Application or API Server

**Option A: Streamlit UI**
```bash
streamlit run src/app.py
```

**Option B: FastAPI Server**
```bash
uvicorn src.main:app --reload
```

---

## 📂 Project Architecture

```text
hackathon_rag/
├── src/
│   ├── api/                 # FastAPI routes & request/response schemas
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── assets/
│   │   └── documents/       # Raw input documents (.pdf, .txt, .md)
│   ├── generation/          # LLM response generation
│   │   └── generator.py
│   ├── ingestion/           # Document ingestion & chunking
│   │   ├── chunker.py
│   │   ├── ingest.py
│   │   └── parser.py
│   ├── retrieval/           # Context retrieval logic
│   │   └── retriever.py
│   ├── vectorstore/         # Persistent ChromaDB client wrapper
│   │   ├── chroma/
│   │   ├── __init__.py
│   │   └── vector_store.py
│   ├── app.py               # Streamlit web app
│   ├── config.py            # Central configuration settings
│   ├── embedder.py          # FastEmbed wrapper
│   └── main.py              # FastAPI application entry point
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🤖 Models Used

- **Embedding Model:** `BAAI/bge-small-en-v1.5` *(via FastEmbed — runs locally without API keys)*
- **LLM (Large Language Model):** `medllama2:latest` *(via Ollama — local open-source medical LLM)*

## Data used 
- Guidelines for the treatment of malaria by World Health Organization

## Evaluation 
- bad
- got 2 correct out of 30
  
