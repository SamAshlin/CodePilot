from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION
)


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
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
                "commit_sha": chunk.get(
                "commit_sha"
                ),
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "content": chunk["content"],
                "chunk_type": chunk.get(
                    "chunk_type",
                    "code"
                ),

                "name": chunk.get(
                    "name"
                ),

                "parent": chunk.get(
                    "parent"
                ),

                "context": chunk.get(
                    "context",
                    []
                )
                }
            )
        )

    if points:

        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points
        )