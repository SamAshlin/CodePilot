from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_URL

from app.routes.repositories import router as repository_router
from app.routes.chat import router as chat_router


app = FastAPI(
    title="CodePilot - Codebase AI Assistant",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    repository_router,
    prefix="/api"
)

app.include_router(
    chat_router,
    prefix="/api"
)


@app.get("/")
def root():

    return {
        "message": "Codebase RAG Assistant API"
    }