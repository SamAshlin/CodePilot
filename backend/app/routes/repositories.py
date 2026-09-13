from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.github_service import (
    clone_repository,
    get_remote_commit_sha,
    get_repository_key
)

from app.services.indexing_service import index_repository
from app.database.mongodb import repositories_collection
from app.database.qdrant import create_collection
import shutil


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"]
)


class RepositoryRequest(BaseModel):

    github_url: str


@router.post("/index")
def create_repository(request: RepositoryRequest):

    try:

        # -----------------------------------------
        # 1. Get GitHub URL
        # -----------------------------------------

        github_url = request.github_url.strip()

        # -----------------------------------------
        # 2. Get repository key
        # -----------------------------------------

        repository_key = get_repository_key(
            github_url
        )

        print(
            "Repository key:",
            repository_key
        )

        # -----------------------------------------
        # 3. Get latest GitHub commit SHA
        # -----------------------------------------

        remote_commit_sha = get_remote_commit_sha(
            github_url
        )

        print(
            "Latest commit SHA:",
            remote_commit_sha
        )

        # -----------------------------------------
        # 4. Find existing repository
        # -----------------------------------------

        existing = repositories_collection.find_one(
            {
                "repository_key": repository_key
            }
        )

        # -----------------------------------------
        # 5. Same repository + same commit
        # -----------------------------------------

        if (
            existing
            and
            existing.get("commit_sha")
            == remote_commit_sha
        ):

            print(
                "Repository version already indexed."
            )

            return {
                "message": "Repository is already indexed",

                "repository_id":
                    existing["_id"],

                "commit_sha":
                    remote_commit_sha,

                "files":
                    existing.get(
                        "files",
                        0
                    ),

                "chunks":
                    existing.get(
                        "chunks",
                        0
                    )
            }

        # -----------------------------------------
        # 6. Determine repository ID
        # -----------------------------------------

        if existing:

            repository_id = existing["_id"]

            print(
                "Existing repository found."
            )

            print(
                "Reusing repository ID:",
                repository_id
            )

        else:

            repository_id = None

            print(
                "New repository."
            )

            print(
                "Creating new repository ID."
            )

        # -----------------------------------------
        # 7. Clone repository
        # -----------------------------------------

        (
            repository_id,
            repository_path,
            commit_sha
        ) = clone_repository(
            github_url,
            repository_id
        )

        print(
            "Cloned commit SHA:",
            commit_sha
        )

        # -----------------------------------------
        # 8. Create Qdrant collection
        # -----------------------------------------

        create_collection()

        # -----------------------------------------
        # 9. Index repository
        # -----------------------------------------

        result = index_repository(
            github_url,
            repository_id,
            commit_sha,
            repository_path
        )

        # -----------------------------------------
        # 10. Store/update repository metadata
        # -----------------------------------------

        now = datetime.utcnow()

        repositories_collection.update_one(

            {
                "_id": repository_id
            },

            {
                "$set": {

                    "github_url":
                        github_url,

                    "repository_key":
                        repository_key,

                    "commit_sha":
                        commit_sha,

                    "status":
                        "indexed",

                    "files":
                        result["files"],

                    "chunks":
                        result["chunks"],

                    "updated_at":
                        now
                },

                "$setOnInsert": {

                    "created_at":
                        now
                }
            },

            upsert=True
        )

        # -----------------------------------------
        # Remove temporary clone
        # -----------------------------------------

        if repository_path:

            shutil.rmtree(
            repository_path,
            ignore_errors=True
            )

        # -----------------------------------------
        # 11. Return result
        # -----------------------------------------

        return {

            "message":
                "Repository indexed successfully",

            "repository_id":
                repository_id,

            "commit_sha":
                commit_sha,

            "files":
                result["files"],

            "chunks":
                result["chunks"]
        }

    except Exception as e:

        print(
            "Repository indexing error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Repository indexing failed"
        )