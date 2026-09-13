from app.database.qdrant import client
from app.config import QDRANT_COLLECTION
from app.services.embedding_service import generate_embedding


def search_code(question, repository_id, limit=8):

    query_vector = generate_embedding(
        question
    )

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        query_filter={
            "must": [
                {
                    "key": "repository_id",
                    "match": {
                        "value": repository_id
                    }
                }
            ]
        },
        limit=limit
    )

    chunks = []

    for result in results.points:

        chunks.append(
            result.payload
        )

    return chunks