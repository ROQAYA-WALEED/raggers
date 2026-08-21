import json
import os
import sys
import pandas as pd

# 1. Ensure project root directory is in sys.path
project_root = "/Users/habibaadawi/Documents/projects/medical_RAG/hackathon_rag"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. Import vector store, embedder, and generator from your project
from src.embedder import embedder
from src.generation.generator import generate_answer
from src.vectorstore.vector_store import vector_store

# 3. Path to relevance dataset
dataset_path = "/Users/habibaadawi/Documents/projects/medical_RAG/RAG_Competition_Project/eval_data/relevance_dataset.json"

with open(dataset_path, "r") as f:
    relevance_dataset = json.load(f)

generation_results = []

print(
    f"🚀 Starting Evaluation on {len(relevance_dataset)} questions using src components..."
)

# 4. Iterate over dataset questions
for idx, sample in enumerate(relevance_dataset, start=1):
    question = sample["Question"]
    is_relevant_label = sample.get("Relevant", "true")

    print(
        f"\n[{idx}/{len(relevance_dataset)}] Processing Query: '{question[:60]}...'"
    )

    # Step A: Embed the question using project embedder
    query_embedding = embedder.embed_query(question)

    # Step B: Retrieve relevant chunks using project vector store (e.g. top_k=3)
    raw_results = vector_store.query(query_embedding, top_k=3)

    # Step C: Format chunks and context for generator.py
    if raw_results:
        # Construct evidence_chunks dicts adhering to generator requirements
        evidence_chunks = []
        context_parts = []

        for item in raw_results:
            text = (
                item.get("text")
                or item.get("document")
                or item.get("page_content", "")
            )
            metadata = item.get("metadata", {})

            context_parts.append(text)
            evidence_chunks.append(
                {
                    "text": text,
                    "page": metadata.get("page", "N/A"),
                    "section": metadata.get("section", "N/A"),
                }
            )

        context_str = "\n\n".join(context_parts)
    else:
        context_str = ""
        evidence_chunks = []

    # Step D: Run generation pipeline (includes Layer 1 & Layer 2 Guardrails)
    output = generate_answer(
        question=question,
        context=context_str,
        evidence_chunks=evidence_chunks,
    )

    llm_resp = output[0]["LLM response"]
    metrics = output[1]["Guardrail metrics"]

    # Append evaluation record
    generation_results.append(
        {
            "sample_id": idx,
            "question": question,
            "dataset_label": is_relevant_label,
            "recommendation": llm_resp.get("Recomendation"),
            "confidence": llm_resp.get("Confidence"),
            "was_blocked": metrics.get("was_blocked"),
            "blocked_at": metrics.get("blocked_at"),
            "faithfulness_score": metrics.get("faithfulness_score"),
            "citation_accuracy": metrics.get("citation_accuracy"),
            "reason": metrics.get("reason"),
            "full_output": output,
        }
    )

# 5. Display Summary
df_eval = pd.DataFrame(generation_results)

print("\n" + "=" * 50)
print("=== PIPELINE EVALUATION SUMMARY ===")
print("=" * 50)
print(f"Total Evaluated:        {len(df_eval)}")
print(f"Blocked Requests:       {df_eval['was_blocked'].sum()}")
print(
    f"Average Faithfulness:   {df_eval[~df_eval['was_blocked']]['faithfulness_score'].mean():.4f}"
)
print(
    f"Average Citation Acc:   {df_eval[~df_eval['was_blocked']]['citation_accuracy'].mean():.4f}"
)