from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.github_service import clone_repository
from app.services.indexing_service import index_repository
from app.database.mongodb import repositories_collection
from app.database.qdrant import create_collection


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"]
)


class RepositoryRequest(BaseModel):

    github_url: str


@router.post("/index")
def create_repository(
    request: RepositoryRequest
):

    try:

        repository_id, repository_path = clone_repository(
            request.github_url
        )

        create_collection()

        result = index_repository(
            request.github_url,
            repository_id
        )

        repositories_collection.insert_one({
            "_id": repository_id,
            "github_url": request.github_url,
            "status": "indexed",
            "files": result["files"],
            "chunks": result["chunks"]
        })

        return {
            "message": "Repository indexed successfully",
            "repository_id": repository_id,
            "files": result["files"],
            "chunks": result["chunks"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )