def retrieve_context(vector_store, query):

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 8,
            "fetch_k": 20
        }
    )

    docs = retriever.invoke(query)

    return docs