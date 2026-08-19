"""
Day 1 Starter — Retrieval + Optional Grounded Answer
------------------------------------------------------
Loads the Chroma index built by ingest.py, retrieves the top-k most
relevant chunks for a question, and prints them with full citation
metadata (document name, page number, chunk id).

If OPENAI_API_KEY is set in .env, it also generates a short grounded
answer that cites only the retrieved text — a preview of the work
you'll formalize on Day 3.

Usage:
    python query.py "What is the recommended screening interval for breast cancer?"
"""
import os
import sys

from langchain_chroma import Chroma

import config
from ingest import get_embedding_function


def load_index():
    embedding_fn = get_embedding_function()
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embedding_fn,
        persist_directory=str(config.CHROMA_DIR),
    )


def retrieve(vectordb, question: str, k: int = None):
    k = k or config.TOP_K
    return vectordb.similarity_search_with_relevance_scores(question, k=k)


def print_results(results):
    print(f"\nTop {len(results)} retrieved chunks:\n")
    for i, (doc, score) in enumerate(results, 1):
        meta = doc.metadata
        print(f"[{i}] score={score:.3f}  "
              f"{meta.get('document_name')}, page {meta.get('page_number')}, "
              f"chunk {meta.get('chunk_id')}")
        preview = doc.page_content.strip().replace("\n", " ")[:200]
        print(f'    "{preview}..."\n')


def maybe_generate_answer(question, results):
    """Optional: if an OpenAI key is configured, generate a short grounded
    answer citing only the retrieved chunks. Skipped otherwise."""
    if not os.getenv("OPENAI_API_KEY"):
        print("(Set OPENAI_API_KEY in .env to also see a generated, cited answer.)")
        return

    from langchain_openai import ChatOpenAI

    context = "\n\n".join(
        f"[{doc.metadata.get('document_name')}, page {doc.metadata.get('page_number')}]\n"
        f"{doc.page_content}"
        for doc, _ in results
    )

    prompt = f"""You are a clinical evidence assistant. Answer ONLY using the context
below. If the context does not contain enough information, say so explicitly.
Always cite the document name and page number for every claim.

Context:
{context}

Question: {question}

Answer (with inline citations):"""

    llm = ChatOpenAI(model=config.OPENAI_CHAT_MODEL, temperature=0)
    response = llm.invoke(prompt)
    print("=== Grounded Answer ===\n")
    print(response.content)


def main():
    if len(sys.argv) < 2:
        print('Usage: python query.py "your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    print(f"Question: {question}")

    vectordb = load_index()
    results = retrieve(vectordb, question)
    print_results(results)
    maybe_generate_answer(question, results)


if __name__ == "__main__":
    main()
