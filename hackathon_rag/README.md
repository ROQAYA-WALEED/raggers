Here is a complete, production-ready `README.md` for your Medical RAG project, incorporating all your exact model details, port cleanup commands, and FastAPI execution steps.

```markdown
# Clinical RAG Assistant with Safety Guardrails

A clinical Retrieval-Augmented Generation (RAG) microservice designed to deliver faithful, context-anchored medical recommendations while enforcing multi-layer safety guardrails.

## Core Models
* **Embedding Model:** `BAAI/bge-base-en-v1.5`
* **LLM Engine:** `qwen2.5:1.5b` (via Ollama)

---

## Key Features
* **Strict Context Verification:** Evaluates claim faithfulness using hybrid lexical overlap metrics.
* **Two-Layer Safety System:** 
  * **Layer 1:** Input Keyword Filtering for unauthorized or unsafe medical requests.
  * **Layer 2:** Output Guardrail verifying claim support and citation alignment against retrieved sources.
* **Structured JSON API:** Delivers recommendations, evidence, page citations, confidence ratings, and guardrail metrics.
* **Flutter Integration:** Simple REST API endpoints ready for mobile and web frontends.

---

## Setup & Running the API

### 1. Prerequisites
Ensure you have Python 3.10+ installed and Ollama running with the local LLM model:
```bash
ollama pull qwen2.5:1.5b

```

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone <your-repo-url>
cd hackathon_rag
pip install -r requirements.txt

```

### 3. Clear Port & Launch FastAPI

Make sure to kill the port you want to use 1st:

```bash
lsof -ti :8001 | xargs kill -9

```

This is how you run the fastapi:

```bash
export PYTHONPATH=$PWD
python -m uvicorn src.main:app --reload --port 8001

```

---

## API Endpoints & Testing

### Interactive Documentation (Swagger UI)

Once running, open your browser to test endpoints interactively:

* **Swagger UI:** `http://127.0.0.1:8001/docs`
* **ReDoc:** `http://127.0.0.1:8001/redoc`

### Example Request (`POST /api/v1/query`)

```json
{
  "question": "What is the recommended dose of artesunate?"
}

```

### Example Response

```json
{
  "question": "What is the recommended dose of artesunate?",
  "recommendation": "The recommended dose of artesunate is 2.4 mg/kg bw per dose. [Page 13]",
  "evidence": "The evidence provided states that for children weighing < 20 kg, a higher dose of artesunate...",
  "citation": "[Page 13]",
  "confidence": "high",
  "guardrail_metrics": {
    "answer": "The recommended dose of artesunate is 2.4 mg/kg bw per dose.",
    "was_blocked": false,
    "blocked_at": "None",
    "faithfulness_score": 1.0,
    "citation_accuracy": 1.0,
    "reason": null
  }
}

```

---

## Flutter Integration

Set the base URL in your Flutter app's HTTP service according to your target platform:

* **iOS Simulator / macOS:** `http://127.0.0.1:8001/api/v1/query`
* **Android Emulator:** `http://10.0.2.2:8001/api/v1/query`
* **Physical Device (Wi-Fi):** `http://<YOUR_LOCAL_IP>:8001/api/v1/query`

```

```