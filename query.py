def retrieve(vectordb, question, k=5):
    return vectordb.similarity_search_with_score(question, k=k)