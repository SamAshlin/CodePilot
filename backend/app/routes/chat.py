from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import search_code
from app.services.llm_service import generate_answer


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):

    repository_id: str = Field(
        ...,
        min_length=1
    )

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


@router.post("/")
def chat(request: ChatRequest):

    try:

        print(
            "Chat request received"
        )

        print(
            "Repository ID:",
            request.repository_id
        )

        print(
            "Question:",
            request.question
        )


        # -----------------------------------------
        # 1. Search repository
        # -----------------------------------------

        chunks = search_code(
            request.question,
            request.repository_id,
            limit=20,
            final_limit=6
        )

        print(
            "Retrieved chunks:",
            len(chunks)
        )


        # -----------------------------------------
        # 2. Generate answer
        # -----------------------------------------

        answer = generate_answer(
            request.question,
            chunks
        )

        print(
            "Answer generated successfully"
        )


        # -----------------------------------------
        # 3. Build citations
        # -----------------------------------------

        citations = []

        for chunk in chunks:

            citations.append({

                "file":
                    chunk["file_path"],

                "start_line":
                    chunk["start_line"],

                "end_line":
                    chunk["end_line"],

                "name":
                    chunk.get("name"),

                "type":
                    chunk.get("chunk_type"),

                "vector_score":
                    chunk.get("vector_score"),

                "rerank_score":
                    chunk.get("rerank_score")
            })


        # -----------------------------------------
        # 4. Return response
        # -----------------------------------------

        return {

            "answer":
                answer,

            "citations":
                citations
        }


    except Exception as e:

        import traceback

        print(
            "CHAT ERROR:",
            str(e)
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )