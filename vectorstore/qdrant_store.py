from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from langchain_qdrant import QdrantVectorStore

from services.embedding_service import get_embedding_model

import os
import uuid


def get_vector_store(video_id):

    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    collection_name = f"video_{video_id}"

    embeddings = get_embedding_model()

    collections = client.get_collections().collections

    existing = [
        collection.name
        for collection in collections
    ]

    if collection_name not in existing:

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )

    return vector_store