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