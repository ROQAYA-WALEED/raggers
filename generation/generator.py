import openai  # or use a local model via Ollama
from typing import List, Dict, Any
import yaml

class StrictGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.llm_model = config.get('llm_model', 'gpt-3.5-turbo')
        self.temperature = config.get('temperature', 0.0)
        # If using OpenAI, set API key; for local, use Ollama or similar.
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        # Build context from retrieved documents
        context = ""
        for i, doc in enumerate(retrieved_docs):
            # doc contains "text", "metadata" (with header info), "rerank_score"
            metadata = doc.get("metadata", {})
            section = metadata.get("Header1", "N/A") or metadata.get("Header2", "N/A") or "N/A"
            page = metadata.get("page", "unknown")  # you need to extract page from PDF parsing; you can add that during chunking
            context += f"Document {i+1}:\n{doc['text']}\n[Section: {section} | Page: {page}]\n\n"

        # Build the strict system prompt
        system_prompt = """You are a grounded AI assistant. Your sole purpose is to answer questions based **exclusively** on the provided document(s). You have no external knowledge, training data, or general world knowledge beyond the text given to you in this session.

STRICT RULES (ZERO EXCEPTIONS):
1. Mandatory Grounding: Every single claim, fact, number, or recommendation in your response must be directly extracted from the provided document. Do not add, infer, or elaborate beyond what is explicitly written.
2. Mandatory Citation Format: Every sentence or distinct factual paragraph must end with a citation in this exact format:
   [Source: Document_Title | Section: X | Page: Y]
   - Replace Document_Title with the actual name of the provided file.
   - Replace X with the specific section/chapter number.
   - Replace Y with the exact page number where the information appears.
   - If the document has no sections, write "N/A". The page number is never optional.
3. Refusal Protocol (Strict Non-Hallucination): If the provided document does **not** contain the information needed to answer the user's query, you **MUST NOT** guess, infer, or use prior knowledge. Instead, output this exact refusal message verbatim:
   "I cannot answer this question because the required information is not present in the provided document."
   - Do not add any additional text, suggestions, or citations after this refusal.
4. Formatting: Structure your answer with clear bullet points or short paragraphs for readability. Apply the citation rule to each bullet point or paragraph individually."""

        user_message = f"Context from documents:\n{context}\n\nUser question: {query}"

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=self.temperature
        )
        return response.choices[0].message.content