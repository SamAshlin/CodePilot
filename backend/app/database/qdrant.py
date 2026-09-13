from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    PayloadSchemaType
)

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION
)


# -----------------------------------------
# Qdrant client
# -----------------------------------------

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


# -----------------------------------------
# Create collection and payload indexes
# -----------------------------------------

def create_collection():

    collections = client.get_collections()

    existing = [
        collection.name
        for collection in collections.collections
    ]


    # -----------------------------------------
    # Create collection if it doesn't exist
    # -----------------------------------------

    if QDRANT_COLLECTION not in existing:

        client.create_collection(

            collection_name=QDRANT_COLLECTION,

            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )


    # -----------------------------------------
    # Get collection information
    # -----------------------------------------

    collection_info = client.get_collection(
        QDRANT_COLLECTION
    )

    payload_schema = (
        collection_info.payload_schema
    )


    # -----------------------------------------
    # Create repository_id index
    # -----------------------------------------

    if "repository_id" not in payload_schema:

        client.create_payload_index(

            collection_name=QDRANT_COLLECTION,

            field_name="repository_id",

            field_schema=PayloadSchemaType.KEYWORD
        )


    # -----------------------------------------
    # Create commit_sha index
    # -----------------------------------------

    if "commit_sha" not in payload_schema:

        client.create_payload_index(

            collection_name=QDRANT_COLLECTION,

            field_name="commit_sha",

            field_schema=PayloadSchemaType.KEYWORD
        )


# -----------------------------------------
# Insert chunks into Qdrant
# -----------------------------------------

def insert_chunks(chunks):

    points = []


    for chunk in chunks:

        points.append(

            PointStruct(

                id=chunk["id"],

                vector=chunk["embedding"],

                payload={

                    # Repository information
                    "repository_id":
                        chunk["repository_id"],

                    "commit_sha":
                        chunk.get(
                            "commit_sha"
                        ),


                    # File information
                    "file_path":
                        chunk["file_path"],

                    "language":
                        chunk["language"],


                    # Source location
                    "start_line":
                        chunk["start_line"],

                    "end_line":
                        chunk["end_line"],


                    # Code
                    "content":
                        chunk["content"],


                    # Tree-sitter metadata
                    "chunk_type":
                        chunk.get(
                            "chunk_type",
                            "code"
                        ),

                    "name":
                        chunk.get(
                            "name"
                        ),

                    "parent":
                        chunk.get(
                            "parent"
                        ),

                    "context":
                        chunk.get(
                            "context",
                            []
                        )
                }
            )
        )


    # -----------------------------------------
    # Insert points
    # -----------------------------------------

    if points:

        client.upsert(

            collection_name=QDRANT_COLLECTION,

            points=points
        )