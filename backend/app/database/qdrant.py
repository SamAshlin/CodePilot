from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from app.config import QDRANT_URL, QDRANT_COLLECTION


client = QdrantClient(
    url=QDRANT_URL
)


def create_collection():

    collections = client.get_collections()

    existing = [
        collection.name
        for collection in collections.collections
    ]

    if QDRANT_COLLECTION not in existing:

        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )


def insert_chunks(chunks):

    points = []

    for chunk in chunks:

        points.append(
            PointStruct(
                id=chunk["id"],
                vector=chunk["embedding"],
                payload={
                    "repository_id": chunk["repository_id"],
                    "file_path": chunk["file_path"],
                    "language": chunk["language"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"]
                }
            )
        )

    if points:

        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points
        )