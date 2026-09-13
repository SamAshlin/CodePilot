from app.database.qdrant import client
from app.database.mongodb import repositories_collection

from app.config import QDRANT_COLLECTION

from app.services.embedding_service import (
    generate_embedding
)

from app.services.reranker import (
    rerank
)


def search_code(
    question,
    repository_id,
    limit=20,
    final_limit=6
):

    # ---------------------------------------------
    # 1. Find repository metadata in MongoDB
    # ---------------------------------------------

    repository = repositories_collection.find_one(
        {
            "_id": repository_id
        }
    )

    if not repository:
        return []

    # ---------------------------------------------
    # 2. Get the current commit SHA
    # ---------------------------------------------

    current_commit_sha = repository.get(
        "commit_sha"
    )

    if not current_commit_sha:
        return []

    # ---------------------------------------------
    # 3. Convert question into embedding
    # ---------------------------------------------

    query_vector = generate_embedding(
        question
    )

    # ---------------------------------------------
    # 4. Search Qdrant
    #
    # IMPORTANT:
    # Search using BOTH repository_id
    # AND current commit SHA.
    # ---------------------------------------------

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
                },
                {
                    "key": "commit_sha",
                    "match": {
                        "value": current_commit_sha
                    }
                }
            ]
        },

        limit=limit
    )

    # ---------------------------------------------
    # 5. Convert Qdrant results into candidates
    # ---------------------------------------------

    candidates = []

    for result in results.points:

        payload = result.payload.copy()

        payload["vector_score"] = result.score

        candidates.append(
            payload
        )

    # ---------------------------------------------
    # 6. Rerank candidates using Gemini
    # ---------------------------------------------

    ranked_chunks = rerank(
        question,
        candidates,
        top_k=final_limit
    )

    return ranked_chunks