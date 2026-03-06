"""
Jenkins AI Chatbot — FastAPI AI Service

Main API module exposing the chatbot functionality.

Endpoints:
    GET  /              — API status
    GET  /health        — Health check
    GET  /workflows     — List available workflow topics
    POST /ask           — Submit a question and receive an AI-generated answer
    POST /troubleshoot  — Analyze error logs and get troubleshooting guidance
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Jenkins AI Chatbot API",
    description="AI-powered assistant for Jenkins workflow guidance",
    version="0.3.0",
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
        ...,
        min_length=1,
        description="The user's question about Jenkins",
    )


class AskResponse(BaseModel):
    """Chatbot answer with sources."""

    answer: str
    sources: list[str] = []


class TroubleshootRequest(BaseModel):
    """Error log for troubleshooting."""

    log: str = Field(
        ...,
        min_length=1,
        description="Jenkins error log or error message",
    )


class TroubleshootResponse(BaseModel):
    """Troubleshooting analysis result."""

    keywords: list[str] = []
    has_known_pattern: bool = False
    analysis: str = ""
    matches: list[dict] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    """API status endpoint."""
    return {
        "status": "online",
        "service": "Jenkins AI Chatbot",
        "version": "0.3.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/workflows")
async def list_workflows():
    """List all available workflow guidance topics."""
    from services.workflow_guide import get_all_workflow_topics

    return {"workflows": get_all_workflow_topics()}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Process a user question through the full RAG pipeline.

    1. Check for workflow guidance matches first.
    2. If no match, fall back to RAG pipeline.
    3. Return answer + source links.
    """
    try:
        # Check for workflow guidance first
        from services.workflow_guide import get_workflow_guidance

        guidance = get_workflow_guidance(request.question)
        if guidance:
            return AskResponse(
                answer=guidance["formatted"],
                sources=guidance.get("docs", []),
            )

        # Fall back to RAG pipeline
        from rag.response_generator import (
            generate_response_with_fallback,
        )

        result = generate_response_with_fallback(request.question)
        return AskResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=(f"Vector index not found. Please build the index first. ({e})"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(f"An error occurred while processing your question: {e}"),
        )


@app.post("/troubleshoot", response_model=TroubleshootResponse)
async def troubleshoot(request: TroubleshootRequest):
    """
    Analyze a Jenkins error log and return troubleshooting guidance.

    Extracts error keywords, matches known patterns, and suggests
    solutions with links to documentation.
    """
    try:
        from services.troubleshooter import analyze_error

        result = analyze_error(request.log)
        return TroubleshootResponse(
            keywords=result["keywords"],
            has_known_pattern=result["has_known_pattern"],
            analysis=result["formatted"],
            matches=result["matches"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing log: {e}",
        )
