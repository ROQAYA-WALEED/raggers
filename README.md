# Clinical RAG Assistant with Safety Guardrails

## Demo

[Watch the Demo Video](https://github.com/user-attachments/assets/182b43f6-6c8c-4333-a752-5d73eb245654)

---

## Project Overview

Clinical guidelines are often dense and difficult to navigate. Traditional LLM-based systems may hallucinate or provide unverified medical information when answering clinical questions.

**Clinical RAG Assistant** is a strictly bounded **Retrieval-Augmented Generation (RAG)** microservice developed for the **AI Clinical Decision Support Lite Hackathon**.

The system is designed to provide **faithful, context-grounded medical recommendations** while enforcing multiple layers of safety and verification.

---

## Architecture & Technologies

| Component                | Technology                |
| ------------------------ | ------------------------- |
| Language & Orchestration | Python, LangChain         |
| Vector Database          | ChromaDB                  |
| Backend & API            | FastAPI                   |
| Retrieval Evaluation     | ranx                      |
| Frontend                 | Flutter                   |
| Embedding Model          | `BAAI/bge-base-en-v1.5`   |
| LLM                      | `qwen2.5:1.5b` via Ollama |

---

## Key Features

### 1. Strict Context Verification

The system evaluates whether generated claims are actually supported by the retrieved medical evidence using **hybrid lexical overlap metrics**.

### 2. Two-Layer Safety System

#### Layer 1 — Input Safety Filter

Filters unauthorized or unsafe medical requests before they reach the generation stage.

#### Layer 2 — Output Safety Guardrail

Verifies the generated answer against the retrieved sources, checking both **claim support** and **citation alignment**.

### 3. Refusal Logic

When the retrieved context does not provide sufficient evidence, the system automatically refuses to generate an unsupported answer instead of guessing.

### 4. Mandatory Citations

Every generated recommendation is required to include its source information, including:

* Document Name
* Section
* Page Number

### 5. Dynamic Context Expansion

When a retrieved chunk contains only part of the required information, the system traces the chunk back to its original medical section and expands the context window.

This allows the LLM to receive the **full clinical context** instead of relying on an incomplete text fragment.

### 6. Structured JSON API

The API returns structured information including:

* Recommendation
* Evidence
* Citation
* Confidence Level
* Faithfulness Score
* Citation Accuracy
* Guardrail Status

### 7. Flutter Integration

The backend exposes REST API endpoints that can be integrated with both mobile and web applications.

---

## Project Structure

```text
main_rag_architecture/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── generator.py
│   └── ...
│
├── raggers_flutter_app/
│
├── requirements.txt
└── README.md
```

---

# Setup & Running

## Prerequisites

Make sure you have:

* Python 3.10+
* Ollama
* Flutter SDK

Pull the required local LLM:

```bash
ollama pull qwen2.5:1.5b
```

---

## Backend Installation

Clone the repository:

```bash
git clone <your-repo-url>
cd main_rag_architecture
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## Run the FastAPI Backend

Make sure port `8001` is available.

### Linux / macOS

```bash
lsof -ti :8001 | xargs kill -9
```

Set the Python path:

```bash
export PYTHONPATH=$PWD
```

Start the FastAPI server:

```bash
python -m uvicorn src.main:app --reload --port 8001
```

The API will be available at:

```text
http://127.0.0.1:8001
```

---

# Flutter App Integration

Set the API base URL according to your target platform.

| Platform              | Base URL                                   |
| --------------------- | ------------------------------------------ |
| iOS Simulator / macOS | `http://127.0.0.1:8001/api/v1/query`       |
| Android Emulator      | `http://10.0.2.2:8001/api/v1/query`        |
| Physical Device       | `http://<YOUR_LOCAL_IP>:8001/api/v1/query` |

### Run the Flutter Application

Open a new terminal:

```bash
cd raggers_flutter_app
flutter pub get
flutter run
```

---

# API Documentation

Once the FastAPI server is running, interactive API documentation is available at:

### Swagger UI

```text
http://127.0.0.1:8001/docs
```

### ReDoc

```text
http://127.0.0.1:8001/redoc
```

---

# API Usage

## POST `/api/v1/query`

### Request

```json
{
  "question": "What is the recommended dose of artesunate?"
}
```

### Response

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

# Safety & Reliability

The system follows a **bounded RAG approach**:

```text
User Question
      ↓
Input Safety Filter
      ↓
Medical Retrieval
      ↓
Dynamic Context Expansion
      ↓
LLM Generation
      ↓
Output Guardrail
      ↓
Faithfulness & Citation Verification
      ↓
Final Response / Safe Refusal
```

The core principle is:

> **If the evidence does not support the answer, the system should not guess.**

---

## Why This Approach?

Instead of allowing the LLM to rely on its internal knowledge, the system constrains generation to the retrieved medical evidence and verifies the generated response before returning it to the user.

This helps reduce:

* Medical hallucinations
* Unsupported recommendations
* Incorrect citations
* Overconfident responses
* Answers generated without sufficient evidence

---

## License

This project was developed as part of the **AI Clinical Decision Support Lite Hackathon**.
