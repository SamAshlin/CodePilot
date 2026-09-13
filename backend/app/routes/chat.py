from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import search_code
from app.services.llm_service import generate_answer


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):

    repository_id: str
    question: str


@router.post("/")
def chat(request: ChatRequest):

    chunks = search_code(
        request.question,
        request.repository_id,
        limit=8
    )

    answer = generate_answer(
        request.question,
        chunks
    )

    citations = []

    for chunk in chunks:

        citations.append({
            "file": chunk["file_path"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"]
        })

    return {
        "answer": answer,
        "citations": citations
    }