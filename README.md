# CodePilot — AI Codebase RAG Assistant

CodePilot is an AI-powered codebase assistant that allows developers to connect a GitHub repository and ask natural-language questions about its implementation.

Instead of sending an entire repository to an LLM, CodePilot indexes the repository, converts relevant code into vector embeddings, retrieves the most relevant code for a question, reranks the retrieved candidates, and generates a grounded answer with file and line-level citations.

---

## Features

- GitHub repository indexing
- AST-aware code chunking using Tree-sitter
- Context-aware code chunks
- Gemini embeddings
- Qdrant vector database
- Semantic vector search
- Repository and commit-level filtering
- LLM-based reranking
- Grounded answer generation
- File and line-level citations
- Repository version tracking using Git commit SHA
- Duplicate indexing prevention
- MongoDB metadata storage
- Production deployment
- React + Vite frontend
- FastAPI backend
- Vercel frontend deployment
- Render backend deployment
- MongoDB Atlas
- Qdrant Cloud

