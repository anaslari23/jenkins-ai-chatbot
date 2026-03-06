"""
Jenkins AI Chatbot — Vector Index (FAISS)

Provides a searchable FAISS vector index for the RAG pipeline.
Wraps index building, persistence, and similarity search.

Usage:
    # Build index from processed chunks
    python -m rag.vector_index --build

    # Search (interactive demo)
    python -m rag.vector_index --query "How to create a Jenkins pipeline"
"""

import argparse
import json
import pickle
from pathlib import Path
from typing import Optional

import faiss
import numpy as np

from config.settings import EMBEDDING_MODEL_NAME, VECTOR_STORE_DIR

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "dataset" / "processed"

# Default index name
INDEX_NAME = "jenkins_index"
DEFAULT_TOP_K = 5


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build_index(
    index_name: str = INDEX_NAME,
    processed_dir: Optional[Path] = None,
) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """
    Build a FAISS index from all processed chunk files.

    1. Loads every JSON file in dataset/processed/.
    2. Encodes texts via SentenceTransformers.
    3. Builds a FAISS IndexFlatIP (inner-product ≡ cosine on L2-normed vecs).
    4. Saves .faiss index and .meta.pkl to vector_store/.

    Returns (index, metadata).
    """
    # Import here to avoid loading the model at module-import time
    from embeddings.embedder import generate_embeddings

    src = processed_dir or PROCESSED_DIR
    if not src.exists():
        raise FileNotFoundError(f"Processed directory not found: {src}")

    all_texts: list[str] = []
    all_metadata: list[dict] = []

    for json_file in sorted(src.glob("*.json")):
        print(f"[vector_index] Loading: {json_file.name}")
        with open(json_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        for c in chunks:
            all_texts.append(c["text"])
            all_metadata.append(
                {
                    "chunk_id": c["chunk_id"],
                    "source": c["source"],
                    "category": c["category"],
                    "text": c["text"],
                }
            )

    if not all_texts:
        raise ValueError("No text chunks found in processed directory")

    print(f"[vector_index] Encoding {len(all_texts)} chunks …")
    embeddings = generate_embeddings(all_texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"[vector_index] FAISS index built — {index.ntotal} vectors, dim={dim}")

    # Persist
    _save(index, all_metadata, index_name)
    return index, all_metadata


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def load_index(
    index_name: str = INDEX_NAME,
) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """
    Load a FAISS index and its metadata from vector_store/.

    Returns (index, metadata).
    """
    index_path = VECTOR_STORE_DIR / f"{index_name}.faiss"
    meta_path = VECTOR_STORE_DIR / f"{index_name}.meta.pkl"

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found: {index_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata not found: {meta_path}")

    index = faiss.read_index(str(index_path))
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)

    print(f"[vector_index] Loaded index ({index.ntotal} vectors) from {index_path}")
    return index, metadata


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def search(
    query_embedding: np.ndarray,
    index: faiss.IndexFlatIP,
    metadata: list[dict],
    top_k: int = DEFAULT_TOP_K,
) -> list[dict]:
    """
    Search the FAISS index for the most similar vectors.

    Args:
        query_embedding: (1, D) or (D,) numpy float32 array.
        index:           FAISS index.
        metadata:        List of metadata dicts aligned with the index.
        top_k:           Number of results to return (default 5).

    Returns a list of result dicts, each containing:
        score     — similarity score (cosine)
        chunk_id  — chunk identifier
        source    — original URL
        category  — content category
        text      — chunk text
    """
    # Ensure 2-D shape
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    query_embedding = query_embedding.astype(np.float32)

    scores, indices = index.search(query_embedding, top_k)

    results: list[dict] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue  # FAISS returns -1 for missing results
        meta = metadata[idx]
        results.append(
            {
                "score": float(score),
                "chunk_id": meta["chunk_id"],
                "source": meta["source"],
                "category": meta["category"],
                "text": meta["text"],
            }
        )

    return results


# ---------------------------------------------------------------------------
# Convenience: search by text query
# ---------------------------------------------------------------------------


def search_by_text(
    query: str,
    index: Optional[faiss.IndexFlatIP] = None,
    metadata: Optional[list[dict]] = None,
    top_k: int = DEFAULT_TOP_K,
    index_name: str = INDEX_NAME,
) -> list[dict]:
    """
    End-to-end search: encode a text query and return top-k results.

    Loads the index automatically if not provided.
    """
    from embeddings.embedder import generate_embeddings

    if index is None or metadata is None:
        index, metadata = load_index(index_name)

    query_emb = generate_embeddings([query])
    return search(query_emb, index, metadata, top_k=top_k)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _save(
    index: faiss.IndexFlatIP,
    metadata: list[dict],
    index_name: str,
) -> None:
    """Persist FAISS index and metadata to disk."""
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    index_path = VECTOR_STORE_DIR / f"{index_name}.faiss"
    meta_path = VECTOR_STORE_DIR / f"{index_name}.meta.pkl"

    faiss.write_index(index, str(index_path))
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)

    print(f"[vector_index] Saved index    → {index_path}")
    print(f"[vector_index] Saved metadata → {meta_path} ({len(metadata)} entries)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FAISS Vector Index management")
    parser.add_argument(
        "--build", action="store_true", help="Build index from processed chunks"
    )
    parser.add_argument("--query", type=str, default=None, help="Search query text")
    parser.add_argument(
        "--top-k", type=int, default=DEFAULT_TOP_K, help="Number of results"
    )
    args = parser.parse_args()

    if args.build:
        build_index()
    elif args.query:
        results = search_by_text(args.query, top_k=args.top_k)
        print(f"\nTop {len(results)} results for: '{args.query}'\n")
        for i, r in enumerate(results, 1):
            print(f"--- Result {i} (score: {r['score']:.4f}) ---")
            print(f"Source:   {r['source']}")
            print(f"Category: {r['category']}")
            print(f"Text:     {r['text'][:200]}…\n")
    else:
        parser.print_help()
