"""
evaluator.py
------------
Retrieval evaluation using the `ranx` library.
"""

from ranx import Qrels, Run, evaluate
from src.retrieval.retriever import retrieve
from src.retrieval.expand_retrieval import expand_context


def truncate_question(question: str, max_length: int = 58) -> str:
    """Truncates question text to fit terminal display cleanly."""
    if len(question) > max_length:
        return question[:max_length] + "..."
    return question


def evaluate_with_ranx(test_dataset: list[dict], k: int = 4, expand_ctx: bool = False):
    """
    Evaluates retrieval performance using ranx and prints individual
    query results matching terminal format.
    """
    qrels_dict = {}
    run_dict = {}
    total_q = len(test_dataset)

    for idx, item in enumerate(test_dataset, start=1):
        q_id = f"q_{idx}"
        target_page_str = str(item["page"])
        question_text = item["question"]

        # 1. Retrieve top chunks (or expand context directly using the query)
        if expand_ctx:
            retrieved_chunks = expand_context(question_text, k=k)
        else:
            retrieved_chunks = retrieve(question_text, top_k=k)

        # Extract page numbers as integers for clean terminal printing
        retrieved_pages_int = [int(chunk.get("page", 0)) for chunk in retrieved_chunks]

        # 2. Build Ground Truth (Qrels)
        qrels_dict[q_id] = {target_page_str: 1}

        # 3. Build Model Predictions (Run) with unique fallback identifiers
        single_run_dict = {}
        for rank, page in enumerate(retrieved_pages_int):
            page_str = str(page)
            # Store maximum score if duplicate pages are returned in top-k
            score = float(k - rank)
            if page_str not in single_run_dict:
                single_run_dict[page_str] = score

        # Ensure run_dict is never empty even if retrieval returned nothing
        if not single_run_dict:
            single_run_dict = {"doc_empty": 0.0}

        run_dict[q_id] = single_run_dict

        # Calculate manual single query Precision@K and Recall@K for display
        hits = sum(1 for p in retrieved_pages_int if p == item["page"])
        p_score = hits / k if k > 0 else 0.0
        r_score = 1.0 if hits > 0 else 0.0

        # 4. Terminal Print Matching Expected Format
        q_truncated = truncate_question(question_text)
        print(f"[{idx}/{total_q}] Question: {q_truncated}")
        print(f"    Target Page: {item['page']} | Retrieved Pages: {retrieved_pages_int}")
        print(f"    Precision@{k}: {p_score:.2f} | Recall@{k}: {r_score:.2f}")
        print()

    # Overall dataset aggregate evaluation via ranx
    overall_qrels = Qrels(qrels_dict)
    overall_run = Run(run_dict)

    overall_metrics = evaluate(
        overall_qrels, 
        overall_run, 
        metrics=[f"precision@{k}", f"recall@{k}", f"hit_rate@{k}"]
    )

    print("--- RanX Aggregate Evaluation ---")
    for metric, score in overall_metrics.items():
        print(f"{metric.capitalize()}: {score:.4f}")

    return overall_metrics