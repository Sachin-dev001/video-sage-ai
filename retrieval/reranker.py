from FlagEmbedding import FlagReranker


reranker = FlagReranker(
    'BAAI/bge-reranker-base',
    use_fp16=False
)


def rerank_documents(query, docs):

    pairs = [
        [query, doc.page_content]
        for doc in docs
    ]

    scores = reranker.compute_score(pairs)

    scored_docs = list(zip(docs, scores))

    scored_docs = sorted(
        scored_docs,
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, _ in scored_docs[:4]]