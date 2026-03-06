"""
Jenkins AI Chatbot — API Routes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Jenkins AI Chatbot API",
    description="AI-powered assistant for Jenkins workflow guidance",
    version="0.1.0",
)

# Allow CORS for the Jenkins UI / frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Incoming user query."""

    query: str


class QueryResponse(BaseModel):
    """Chatbot response."""

    answer: str
    sources: list[str] = []


@app.get("/health")
async def health_check():
    """Health-check endpoint."""
    return {"status": "ok"}


@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Handle a user chat query.

    TODO: Wire up the RAG pipeline in a later phase.
    """
    return QueryResponse(
        answer=f"Echo: {request.query}  (RAG pipeline not yet connected)",
        sources=[],
    )
