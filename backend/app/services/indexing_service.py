
import uuid

from app.services.github_service import clone_repository
from app.services.file_scanner import scan_repository
from app.services.chunker import chunk_code
from app.services.embedding_service import generate_embedding
from app.database.qdrant import insert_chunks


def index_repository(github_url, repository_id=None):

    print("\n========== INDEX REPOSITORY START ==========")
    print(f"[1] github_url: {github_url}")
    print(f"[2] repository_id: {repository_id}")

    # Clone repository
    if repository_id is None:
        print("[3] repository_id is None -> Starting clone_repository()")

        repository_id, repository_path = clone_repository(
            github_url
        )

        print("[4] clone_repository() completed")
        print(f"[5] repository_id: {repository_id}")
        print(f"[6] repository_path: {repository_path}")

    else:
        print("[3] repository_id provided -> Skipping clone")
        
        repository_path = f"repositories/{repository_id}"

        print(f"[4] repository_path: {repository_path}")

    # Scan repository
    print("[7] Starting scan_repository()")

    files = scan_repository(
        repository_path
    )

    print("[8] scan_repository() completed")
    print(f"[9] Number of files found: {len(files)}")

    all_chunks = []

    # Process files
    print("[10] Starting file processing loop")

    for file_index, file in enumerate(files, start=1):

        print("\n----------------------------------------")
        print(f"[11] Processing file {file_index}/{len(files)}")
        print(f"[12] File path: {file.get('path')}")
        print(f"[13] Language: {file.get('language')}")

        try:
            # Chunk code
            print("[14] Starting chunk_code()")

            chunks = chunk_code(
                content=file["content"],
                file_path=file["path"],
                language=file["language"]
            )

            print("[15] chunk_code() completed")
            print(f"[16] Number of chunks: {len(chunks)}")

            # Process chunks
            for chunk_index, chunk in enumerate(chunks, start=1):

                print(
                    f"[17] Processing chunk "
                    f"{chunk_index}/{len(chunks)} "
                    f"of file: {file['path']}"
                )

                print("[18] Generating embedding...")

                embedding_text = f"""
                File: {chunk['file_path']}
                Language: {chunk['language']}
                Lines: {chunk['start_line']}-{chunk['end_line']}

                Code: {chunk['content']}"""

                embedding = generate_embedding(
                    embedding_text
                )

                print("[19] generate_embedding() completed")
                print(
                    f"[20] Embedding generated. "
                    f"Length: {len(embedding)}"
                )

                chunk["id"] = str(uuid.uuid4())
                chunk["embedding"] = embedding
                chunk["repository_id"] = repository_id

                all_chunks.append(chunk)

                print(
                    f"[21] Chunk added to all_chunks. "
                    f"Total chunks: {len(all_chunks)}"
                )

        except Exception as e:
            print("\n!!!!!!!! ERROR !!!!!!!")
            print(f"File: {file.get('path')}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {e}")
            print("!!!!!!!!!!!!!!!!!!!!!!\n")

            # Re-raise so the actual traceback is still shown
            raise

    # Insert into Qdrant
    print("\n[22] Finished processing all files")
    print(f"[23] Total chunks to insert: {len(all_chunks)}")

    print("[24] Starting insert_chunks()")

    insert_chunks(all_chunks)

    print("[25] insert_chunks() completed")

    result = {
        "repository_id": repository_id,
        "files": len(files),
        "chunks": len(all_chunks)
    }

    print("[26] Returning result")
    print(f"[27] Result: {result}")
    print("========== INDEX REPOSITORY END ==========\n")

    return result


