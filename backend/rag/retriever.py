"""
Jenkins AI Chatbot — Retrieval Engine

Retrieves the most relevant knowledge documents for a user query
by combining query processing with FAISS vector search.

Usage:
    from rag.retriever import retrieve
    results = retrieve("How do I set up a Jenkins pipeline?")

    python -m rag.retriever "How to install Jenkins plugins"
"""

from typing import Optional

import faiss
import numpy as np

from rag.query_processor import process_query
from rag.vector_index import load_index, search, INDEX_NAME, DEFAULT_TOP_K


# ---------------------------------------------------------------------------
# Retriever state (lazy-loaded singleton)
# ---------------------------------------------------------------------------

_index: Optional[faiss.IndexFlatIP] = None
_metadata: Optional[list[dict]] = None


def _ensure_loaded(
    index_name: str = INDEX_NAME,
) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """Load the FAISS index and metadata if not already cached."""
    global _index, _metadata
    if _index is None or _metadata is None:
        _index, _metadata = load_index(index_name)
    return _index, _metadata


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def retrieve(
    raw_query: str,
    top_k: int = DEFAULT_TOP_K,
    index_name: str = INDEX_NAME,
) -> list[dict]:
    """
    End-to-end retrieval: raw user question → ranked document list.

    Steps:
        1. Normalize the query and generate its embedding.
        2. Search the FAISS index for the top-k most similar chunks.
        3. Return a ranked list of result dicts.

    Args:
        raw_query:  The user's raw question string.
        top_k:      Number of documents to retrieve (default 5).
        index_name: Name of the FAISS index to search.

    Returns:
        List of dicts, each containing:
            score     — cosine similarity (float)
            chunk_id  — chunk identifier
            source    — original URL
            category  — content category (docs / plugins / github / community)
            text      — chunk text
    """
    index, metadata = _ensure_loaded(index_name)

    normalized_query, query_embedding = process_query(raw_query)
    print(f"[retriever] Query: '{normalized_query}' → searching top {top_k}")

    results = search(query_embedding, index, metadata, top_k=top_k)

    print(f"[retriever] Retrieved {len(results)} documents")
    return results


def retrieve_with_context(
    raw_query: str,
    top_k: int = DEFAULT_TOP_K,
    index_name: str = INDEX_NAME,
) -> dict:
    """
    Retrieve documents and return them bundled with the query context.

    Returns a dict with:
        query      — normalized query text
        results    — ranked list of document dicts
        context    — concatenated text of all retrieved chunks (for LLM prompt)
    """
    index, metadata = _ensure_loaded(index_name)

    normalized_query, query_embedding = process_query(raw_query)
    results = search(query_embedding, index, metadata, top_k=top_k)

    # Build combined context string for the LLM
    context_parts: list[str] = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[Source {i}: {r['source']}]\n{r['text']}")
    context = "\n\n---\n\n".join(context_parts)

    return {
        "query": normalized_query,
        "results": results,
        "context": context,
    }


def reload_index(index_name: str = INDEX_NAME) -> None:
    """Force-reload the FAISS index (e.g. after re-building)."""
    global _index, _metadata
    _index, _metadata = load_index(index_name)
    print(f"[retriever] Index reloaded ({_index.ntotal} vectors)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Retrieve relevant Jenkins documents")
    parser.add_argument("query", type=str, help="User query text")
    parser.add_argument(
        "--top-k", type=int, default=DEFAULT_TOP_K, help="Number of results"
    )
    args = parser.parse_args()

    results = retrieve(args.query, top_k=args.top_k)
    print(f"\nTop {len(results)} results for: '{args.query}'\n")
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (score: {r['score']:.4f}) ---")
        print(f"Source:   {r['source']}")
        print(f"Category: {r['category']}")
        print(f"Text:     {r['text'][:200]}…\n")
