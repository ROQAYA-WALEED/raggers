import os
import sys
from raggers.retrieval.retriever import HybridRetriever

# Your test set (add all 10 queries)
formatted_test_set = [
    {
        "query": "What are the five Plasmodium species that cause malaria in humans?",
        "expected_keywords": [
            "P. falciparum",
            "P. vivax",
            "P. ovale",
            "P. malariae",
            "P. knowlesi"
        ]
    },
    {
        "query": "What is the recommended treatment for uncomplicated Plasmodium falciparum malaria in adults and children?",
        "expected_keywords": [
            "artemisinin-based combination therapy",
            "ACT",
            "artemether + lumefantrine",
            "artesunate + amodiaquine"
        ]
    },
    {
        "query": "What is the first-line treatment for severe malaria according to the WHO guidelines?",
        "expected_keywords": [
            "intravenous or intramuscular artesunate",
            "parenteral artesunate",
            "severe malaria"
        ]
    },
    {
        "query": "What is the recommended dose of primaquine to reduce transmission of P. falciparum in low-transmission areas?",
        "expected_keywords": [
            "single dose of 0.25 mg/kg",
            "primaquine",
            "reduce transmission"
        ]
    },
    {
        "query": "What are the signs and symptoms of severe malaria?",
        "expected_keywords": [
            "cerebral malaria",
            "metabolic acidosis",
            "severe anaemia",
            "hypoglycaemia",
            "acute renal failure",
            "pulmonary oedema"
        ]
    },
    {
        "query": "What is the recommended treatment for uncomplicated P. vivax malaria in areas with chloroquine-resistant infections?",
        "expected_keywords": [
            "ACT",
            "artemisinin-based combination therapy",
            "chloroquine-resistant P. vivax"
        ]
    },
    {
        "query": "What is the role of sulfadoxine-pyrimethamine (SP) in intermittent preventive treatment in pregnancy (IPTp)?",
        "expected_keywords": [
            "intermittent preventive treatment in pregnancy",
            "SP-IPTp",
            "sulfadoxine-pyrimethamine",
            "antenatal care"
        ]
    },
    {
        "query": "What is the definition of antimalarial drug resistance?",
        "expected_keywords": [
            "ability of a parasite strain to survive",
            "despite the administration and absorption",
            "drug resistance"
        ]
    },
    {
        "query": "What are the recommended pre-referral treatment options for severe malaria when parenteral artesunate is not available?",
        "expected_keywords": [
            "intramuscular artemether",
            "intramuscular quinine",
            "rectal artesunate",
            "pre-referral treatment"
        ]
    },
    {
        "query": "What are the recommended ACTs for the treatment of uncomplicated P. falciparum malaria?",
        "expected_keywords": [
            "artemether + lumefantrine",
            "artesunate + amodiaquine",
            "artesunate + mefloquine",
            "dihydroartemisinin + piperaquine",
            "artesunate + sulfadoxine-pyrimethamine"
        ]
    }
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