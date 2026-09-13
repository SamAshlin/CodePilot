from datetime import datetime
import shutil

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.github_service import (
    clone_repository,
    get_repository_key
)

from app.services.indexing_service import index_repository
from app.database.mongodb import repositories_collection
from app.database.qdrant import create_collection


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"]
)


class RepositoryRequest(BaseModel):

    github_url: str = Field(
        ...,
        min_length=1,
        max_length=500
    )


@router.post("/index")
def create_repository(request: RepositoryRequest):

    repository_path = None

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
        # 3. Find existing repository
        # -----------------------------------------

        existing = repositories_collection.find_one(
            {
                "repository_key": repository_key
            }
        )


        # -----------------------------------------
        # 4. Determine repository ID
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
        # 5. Clone repository
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
                # 7. Create Qdrant collection
                # -----------------------------------------
        
        create_collection()
        


        # -----------------------------------------
        # 6. Check same repository + same commit
        # -----------------------------------------

        if (
            existing
            and
            existing.get("commit_sha")
            == commit_sha
        ):

            print(
                "Repository version already indexed."
            )

            return {

                "message":
                    "Repository is already indexed",

                "repository_id":
                    repository_id,

                "commit_sha":
                    commit_sha,

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
        # 8. Index repository
        # -----------------------------------------

        result = index_repository(

            github_url,

            repository_id,

            commit_sha,

            repository_path
        )


        # -----------------------------------------
        # 9. Store/update repository metadata
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
        # 10. Return result
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


    finally:

        # -----------------------------------------
        # Remove temporary clone
        # -----------------------------------------

        if repository_path:

            shutil.rmtree(
                repository_path,
                ignore_errors=True
            )