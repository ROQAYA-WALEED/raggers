import os
import sys
from raggers.retrieval.retriever import HybridRetriever

# Your test set (add all 10 queries)
formatted_test_set = [
    {
        "query": "What are the main categories of genes involved in the development of cancer?",
        "expected_keywords": [
            "tumour suppressor genes",
            "proto-oncogenes",
            "DNA repair genes"
        ]
    },
    # ... add remaining 9 queries
]

def evaluate():
    retriever = HybridRetriever(config_path=r"C:\Users\dell\OneDrive\Desktop\c++ folder\Ai hacathon creativa\raggers\config.yaml")
    k = 5
    total_precision = 0
    for item in formatted_test_set:
        query = item["query"]
        expected = [kw.lower() for kw in item["expected_keywords"]]
        
        docs = retriever.retrieve(query, top_k=k)
        relevant = 0
        for doc in docs:
            text_lower = doc["text"].lower()
            if any(kw in text_lower for kw in expected):
                relevant += 1
        precision = relevant / k
        total_precision += precision

        print("\n" + "="*80)
        print(f"QUERY: {query}")
        print(f"Precision@{k}: {precision:.2f} ({relevant}/{k} relevant)")
        print("\nRetrieved Chunks:")
        for i, doc in enumerate(docs, 1):
            page = doc.get("metadata", {}).get("page", "N/A")
            header = doc.get("metadata", {}).get("header_path", "N/A")
            print(f"\n  [{i}] Page: {page} | Section: {header}")
            print(f"      Score (hybrid): {doc.get('score', 'N/A')}")
            print(f"      Score (rerank): {doc.get('rerank_score', 'N/A')}")
            print(f"      Snippet: {doc['text'][:200]}...")

    avg_precision = total_precision / len(formatted_test_set)
    print("\n" + "="*80)
    print(f"📊 Average Precision@{k}: {avg_precision:.2f}")
    print("="*80)

if __name__ == "__main__":
    evaluate()