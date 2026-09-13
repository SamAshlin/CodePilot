import uuid

from app.services.file_scanner import scan_repository
from app.services.chunker import chunk_code
from app.services.embedding_service import generate_embedding
from app.database.qdrant import insert_chunks


def index_repository(
    github_url,
    repository_id,
    commit_sha,
    repository_path
):

    files = scan_repository(
        repository_path
    )

    all_chunks = []

    for file in files:

        chunks = chunk_code(
            content=file["content"],
            file_path=file["path"],
            language=file["language"]
        )

        for chunk in chunks:

            # ---------------------------------
            # Extract AST metadata
            # ---------------------------------

            context = chunk.get(
                "context",
                []
            )

            parent = chunk.get(
                "parent"
            )

            name = chunk.get(
                "name"
            )

            chunk_type = chunk.get(
                "chunk_type",
                "code"
            )

            # ---------------------------------
            # Build contextual representation
            # for embedding
            # ---------------------------------

            embedding_text = f"""
Repository code

File: {chunk['file_path']}

Language: {chunk['language']}

Code unit type: {chunk_type}

Name: {name or 'unknown'}

Parent class: {parent or 'none'}

Context: {', '.join(context) if context else 'none'}

Lines: {chunk['start_line']}-{chunk['end_line']}

Source code:

{chunk['content']}
""".strip()

            # ---------------------------------
            # Generate embedding
            # ---------------------------------

            embedding = generate_embedding(
                embedding_text
            )

            # ---------------------------------
            # Store metadata
            # ---------------------------------

            chunk["id"] = str(
                uuid.uuid4()
            )

            chunk["embedding"] = embedding

            chunk["repository_id"] = (
                repository_id
            )

            chunk["commit_sha"] = (
                commit_sha
            )

            all_chunks.append(chunk)

    # -----------------------------------------
    # Insert everything into Qdrant
    # -----------------------------------------

    insert_chunks(
        all_chunks
    )

    return {
        "repository_id": repository_id,
        "files": len(files),
        "chunks": len(all_chunks)
    }