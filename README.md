# CodePilot — Codebase RAG Assistant

CodePilot is an AI-powered codebase assistant that allows developers to connect a GitHub repository and ask questions about its implementation.

Instead of manually searching through files, a developer can ask questions such as:

- How does the payment flow work?
- Which file handles JWT validation?
- Where is this API endpoint defined?
- Which files would I need to modify to add a new feature?
- Why might this API return a 401?

The system retrieves relevant parts of the repository and gives the retrieved code to an LLM as context. The final answer is grounded in the actual repository and includes file and line references.
The main goal of the project is to demonstrate how Retrieval-Augmented Generation (RAG) can be applied to real software repositories rather than only working with simple documents.

---

## Features

- GitHub repository indexing
- AST-aware code chunking using Tree-sitter
- Function, method, class, and module level code chunks
- Parent and surrounding context for code chunks
- Gemini-based code embeddings
- Qdrant vector database for semantic search
- Repository and commit-level filtering
- LLM-based reranking of retrieved code
- Grounded answers using repository context
- File and line-level citations
- Repository version tracking using Git commit SHA
- Duplicate indexing protection
- MongoDB metadata storage
- React frontend
- FastAPI backend
- Production deployment using Vercel and Render
- MongoDB Atlas and Qdrant Cloud integration

---

# Why RAG for a Codebase?

A normal LLM does not automatically know the implementation of a private or newly created codebase.

For example, suppose a repository contains:

```text
auth/
    auth_service.py
    jwt.py

payments/
    payment_service.py

routes/
    user_routes.py

If the developer asks:
Where is JWT authentication implemented?
Sending the question directly to an LLM does not give it access to these files.
CodePilot solves this by retrieving the relevant code first.

Technology Stack
Frontend
React, Vite, Axios, CSS
Backend
Python,FastAPI,Pydantic,Uvicorn
AI / RAG
Google Gemini,Gemini Embedding 2,Gemini LLM,Tree-sitter,Qdrant
Database
MongoDB,MongoDB Atlas
Deployment
Vercel,Render,Qdrant Cloud,MongoDB Atlas

Local Setup
1. Clone the repository
git clone https://github.com/<username>/CodePilot.git
cd CodePilot

2. Create the Python environment
cd backend
python -m venv .venv

Activate it on Windows:
.venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Start the backend:
uvicorn app.main:app --reload --port 8000

The API will be available at:
http://localhost:8000

Swagger documentation:
http://localhost:8000/docs

Frontend Setup
Move to the frontend:
cd frontend

Install dependencies:
npm install

Create:
frontend/.env

Add:
VITE_API_URL=http://localhost:8000

Start the development server:
npm run dev

