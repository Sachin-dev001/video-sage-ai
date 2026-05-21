from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_model():

    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base"
    )

    return embeddings