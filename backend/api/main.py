"""
Jenkins AI Chatbot — FastAPI AI Service

Main API module exposing the chatbot functionality.

Endpoints:
    GET  /       — API status
    GET  /health — Health check
    POST /ask    — Submit a question and receive an AI-generated answer
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Jenkins AI Chatbot API",
    description="AI-powered assistant for Jenkins workflow guidance",
    version="0.2.0",
)

# CORS — allow Jenkins UI and frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class AskRequest(BaseModel):
    """Incoming user question."""

    question: str = Field(
        ..., min_length=1, description="The user's question about Jenkins"
    )


class AskResponse(BaseModel):
    """Chatbot answer with sources."""

    answer: str
    sources: list[str] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    """API status endpoint."""
    return {
        "status": "online",
        "service": "Jenkins AI Chatbot",
        "version": "0.2.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Process a user question through the full RAG pipeline.

    1. Normalize and embed the query.
    2. Retrieve relevant documents from the FAISS index.
    3. Build LLM prompt context.
    4. Generate response via LLM (with fallback).
    5. Return answer + source links.
    """
    try:
        from rag.response_generator import generate_response_with_fallback

        result = generate_response_with_fallback(request.question)

        return AskResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector index not found. Please build the index first. ({e})",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {e}",
        )
