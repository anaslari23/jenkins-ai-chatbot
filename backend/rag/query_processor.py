"""
Jenkins AI Chatbot — Query Processor

Converts raw user questions into semantic search query vectors.

Responsibilities:
    1. Normalize the user query (lowercase, strip special chars, collapse whitespace).
    2. Generate an embedding vector via SentenceTransformers.
    3. Return the query vector ready for FAISS similarity search.

Usage:
    from rag.query_processor import process_query
    vector = process_query("How do I install a Jenkins plugin?")
"""

import re

import numpy as np


# ---------------------------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------------------------


def normalize_query(query: str) -> str:
    """
    Clean and normalize a raw user query.

    Steps:
        - Strip leading / trailing whitespace
        - Lowercase
        - Remove special characters (keep letters, digits, spaces, and basic punctuation)
        - Collapse multiple spaces
    """
    query = query.strip().lower()
    # Keep alphanumerics, spaces, and basic punctuation useful for meaning
    query = re.sub(r"[^a-z0-9\s\-\?\.\,\']", "", query)
    # Collapse whitespace
    query = re.sub(r"\s+", " ", query).strip()
    return query


# ---------------------------------------------------------------------------
# Embedding generation
# ---------------------------------------------------------------------------


def generate_query_embedding(query: str) -> np.ndarray:
    """
    Generate a normalised embedding vector for a (pre-cleaned) query string.

    Returns a (1, D) float32 numpy array suitable for FAISS search.
    """
    from embeddings.embedder import generate_embeddings

    embedding = generate_embeddings([query])  # shape (1, D)
    return embedding


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def process_query(raw_query: str) -> tuple[str, np.ndarray]:
    """
    End-to-end query processing pipeline.

    Args:
        raw_query: The user's raw question string.

    Returns:
        (normalized_query, query_vector)
        - normalized_query: cleaned text
        - query_vector: (1, D) float32 numpy array
    """
    normalized = normalize_query(raw_query)
    if not normalized:
        raise ValueError("Query is empty after normalization")

    embedding = generate_query_embedding(normalized)
    return normalized, embedding


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process a user query into a search vector"
    )
    parser.add_argument("query", type=str, help="User query text")
    args = parser.parse_args()

    norm, vec = process_query(args.query)
    print(f"Original:   {args.query}")
    print(f"Normalized: {norm}")
    print(f"Vector shape: {vec.shape}")
    print(f"Vector dtype: {vec.dtype}")
    print(f"Vector norm:  {np.linalg.norm(vec):.4f}")
    print(f"First 5 dims: {vec[0, :5]}")
