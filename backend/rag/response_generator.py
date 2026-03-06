"""
Jenkins AI Chatbot — Response Generator

Generates answers using a local LLM with the RAG context.

Supports multiple backends:
    1. Hugging Face transformers (local model)
    2. Ollama API (if running locally)

The backend is selected via the LLM_BACKEND env var:
    - "transformers"  (default) — loads model via HF transformers pipeline
    - "ollama"        — calls a locally running Ollama instance

Usage:
    from rag.response_generator import generate_response
    answer = generate_response("How to create a pipeline?")

    python -m rag.response_generator "How to install plugins?"
"""

import os
from typing import Optional

import requests

from config.settings import LLM_MODEL_NAME
from rag.context_builder import SYSTEM_PROMPT, build_context
from rag.retriever import retrieve

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LLM_BACKEND = os.getenv("LLM_BACKEND", "transformers")  # "transformers" | "ollama"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
DEFAULT_TOP_K = 5


# ---------------------------------------------------------------------------
# Transformers backend (Hugging Face local model)
# ---------------------------------------------------------------------------

_hf_pipeline = None


def _load_hf_pipeline():
    """Lazy-load a Hugging Face text-generation pipeline."""
    global _hf_pipeline
    if _hf_pipeline is not None:
        return _hf_pipeline

    from transformers import pipeline as hf_pipeline

    model_name = LLM_MODEL_NAME
    print(f"[response_generator] Loading HF model: {model_name}")

    _hf_pipeline = hf_pipeline(
        "text-generation",
        model=model_name,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        do_sample=True,
        return_full_text=False,
    )
    print(f"[response_generator] HF model loaded: {model_name}")
    return _hf_pipeline


def _generate_hf(prompt_text: str) -> str:
    """Generate a response using the HF transformers pipeline."""
    pipe = _load_hf_pipeline()
    outputs = pipe(prompt_text)
    return outputs[0]["generated_text"].strip()


# ---------------------------------------------------------------------------
# Ollama backend
# ---------------------------------------------------------------------------


def _generate_ollama(prompt_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Generate a response via a locally running Ollama instance."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": LLM_MODEL_NAME,
        "prompt": prompt_text,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_NEW_TOKENS,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except requests.RequestException as e:
        return f"[Error communicating with Ollama: {e}]"


# ---------------------------------------------------------------------------
# Unified generation
# ---------------------------------------------------------------------------


def _generate(prompt_text: str) -> str:
    """Route to the configured backend."""
    if LLM_BACKEND == "ollama":
        return _generate_ollama(prompt_text)
    else:
        return _generate_hf(prompt_text)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_response(
    raw_query: str,
    top_k: int = DEFAULT_TOP_K,
    context_results: Optional[list[dict]] = None,
) -> dict:
    """
    End-to-end RAG response generation.

    Steps:
        1. Retrieve relevant documents (or use provided ones).
        2. Build prompt context.
        3. Generate LLM response.
        4. Return structured answer.

    Args:
        raw_query:       The user's raw question.
        top_k:           Number of documents to retrieve.
        context_results: Pre-retrieved results (skips retrieval if provided).

    Returns:
        {
            "query":   normalized query,
            "answer":  LLM-generated response,
            "sources": list of source URLs used,
        }
    """
    # Step 1 — Retrieve
    if context_results is None:
        context_results = retrieve(raw_query, top_k=top_k)

    # Step 2 — Build context
    context = build_context(raw_query, context_results)

    # Construct the full prompt for the LLM
    full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nAnswer:"

    # Step 3 — Generate
    print(f"[response_generator] Generating response (backend={LLM_BACKEND})")
    answer = _generate(full_prompt)

    # Step 4 — Collect unique sources
    sources = list({r["source"] for r in context_results if r.get("source")})

    return {
        "query": raw_query,
        "answer": answer,
        "sources": sources,
    }


def generate_response_with_fallback(
    raw_query: str,
    top_k: int = DEFAULT_TOP_K,
) -> dict:
    """
    Generate a response with graceful fallback if the LLM is unavailable.

    Falls back to returning only the retrieved context without LLM generation.
    """
    context_results = retrieve(raw_query, top_k=top_k)

    try:
        return generate_response(
            raw_query, top_k=top_k, context_results=context_results
        )
    except Exception as e:
        print(f"[response_generator] LLM generation failed: {e}")
        # Fallback: return retrieved context as the answer
        fallback_text = "\n\n".join(
            f"• {r['text'][:300]}… (Source: {r['source']})" for r in context_results
        )
        return {
            "query": raw_query,
            "answer": f"I found relevant information but couldn't generate a full response:\n\n{fallback_text}",
            "sources": list({r["source"] for r in context_results}),
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate RAG response")
    parser.add_argument("query", type=str, help="User query")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument(
        "--backend", type=str, default=None, help="LLM backend: transformers or ollama"
    )
    args = parser.parse_args()

    if args.backend:
        LLM_BACKEND = args.backend

    result = generate_response_with_fallback(args.query, top_k=args.top_k)
    print(f"\nQuery:  {result['query']}")
    print(f"Sources: {result['sources']}")
    print(f"\nAnswer:\n{result['answer']}")
