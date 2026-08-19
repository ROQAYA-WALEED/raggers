# Developer Onboarding & Quickstart Guide

Welcome to the **Mini RAG** project! This guide provides a complete, step-by-step walk-through to get your local development environment set up, configure your providers, and begin contributing code cleanly without breaking the team’s core architecture.

---

## 1. Quick Setup & Local Execution

Follow these steps in your terminal to set up and run the application on your machine.

### Step 1: Clone and Navigate to the Repository

```bash
git clone <repository-url>
cd mini-rag

```

### Step 2: Set Up Virtual Environment

Create and activate a Python virtual environment (Python 3.10+ recommended):

```bash
# Using Conda
conda create -n mini_rag python=3.11 -y
conda activate mini_rag

# OR using venv
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

```

### Step 3: Configure Environment Variables

Copy `.env.example` to create your local `.env` file:

```bash
cp .env.example .env

```

Open `.env` in your code editor and adjust `LLM_PROVIDER`, `EMBEDDING_PROVIDER`, and your local credentials or API keys (e.g., `OPENAI_API_KEY` or `OLLAMA_BASE_URL`).

### Step 4: Install Dependencies

Install core dependencies alongside the extras needed for your specific assignment:

```bash
# Install core dependencies
pip install -r requirements.txt

# (Optional) Install specialized provider packages as needed:
# pip install langchain-openai   # If using OpenAI
# pip install ollama           # If using Ollama locally

```

### Step 5: Run the Server

Launch the application with live-reloading:

```bash
uvicorn src.main:app --reload

```

Open **[http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs)** in your browser to interact with the auto-generated Swagger API documentation.

---

## 2. Where to Start Coding Your Feature

To maintain modularity across team members, every RAG feature follows a clear sequence. Here is the recommended order for building your components:

1. **Step 1: Implement the Store Class:** Under src/stores/.
Locate the abstract interface for your component:

* **LLM:** Extend `LLMInterface` in `src/stores/llm/` (e.g., `OllamaProvider.py`).
* **Vector DB:** Extend `VectorDBInterface` in `src/stores/vectordb/` (e.g., `ChromaDBProvider.py`).

Ensure your class implements all required abstract methods (`generate`, `add_documents`, `similarity_search`).


2. **Step 2: Connect Factory Loading:** Under src/stores/llm/init.py or vectordb/init.py.
Register your new provider in the factory instantiation logic. Use **lazy imports** inside the loader function to ensure dependencies are only loaded when selected in `.env`:

```python
# Example inside get_llm_provider()
if provider == "ollama":
    try:
        from src.stores.llm.OllamaProvider import OllamaProvider
        return OllamaProvider()
    except ImportError:
        raise ImportError("Missing Ollama dependencies. Run: pip install ollama")

```


3. **Step 3: Build the Business Logic:** Under src/controllers/.
Create or update a controller (e.g., `NLPController.py` or `DataController.py`). Controllers request instantiated providers from the store factory and orchestrate the document loading, vector storage, and response retrieval pipelines.


4. **Step 4: Expose API Endpoint:** Under src/routes/.
Expose your feature through FastAPI endpoints in `src/routes/nlp.py` or `src/routes/data.py`. Call your controller methods inside route handlers and return structured Pydantic models.


---

## 3. Project File & Directory Map

Below is a complete reference explaining the role of every directory and foundational file in the repository structure:

| Path / File | Purpose & Responsibilities |
| --- | --- |
| `.env.example` | Template containing all available configuration keys. Copy to `.env` for local setup. |
| `.gitignore` | Prevents local runtime artifacts (`.env`, `__pycache__`, `chroma_db/`) from being committed to Git. |
| `requirements.txt` | Core Python dependencies required to start the FastAPI server and base system utilities. |
| `alembic.ini` | Configuration file for database schema migrations via Alembic. |
| `alembic/versions/` | Houses auto-generated schema revision scripts for PostgreSQL tracking. |
| `src/main.py` | FastAPI application entry point. Registers routers, CORS, and middleware settings. |
| `src/config.py` | Loads and validates environment variables into Pydantic settings objects. |
| `src/routes/` | API routes layer handling HTTP requests and status codes (`data.py`, `nlp.py`, `base.py`). |
| `src/controllers/` | Orchestrates RAG logic, bridging route requests to underlying stores and processing modules. |
| `src/models/` | SQLAlchemy database models (`db_schemes/`) and Pydantic request/response schemas (`enums/`). |
| `src/stores/llm/` | Abstract `LLMInterface.py` contracts and concrete LLM implementation classes. |
| `src/stores/vectordb/` | Abstract `VectorDBInterface.py` contracts and concrete Vector DB integration wrappers. |
| `src/tasks/` | Celery task scripts for offloading background tasks like document embedding. |

---
