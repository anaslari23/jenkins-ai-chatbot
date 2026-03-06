"""
Jenkins AI Chatbot — Embedding Generator

Generates vector embeddings for processed text chunks using
SentenceTransformers (all-MiniLM-L6-v2) and stores them in a
FAISS index alongside metadata for retrieval.

Usage:
    python -m embeddings.embedder                        # embed all processed files
    python -m embeddings.embedder --file jenkins_docs.json
    python -m embeddings.embedder --batch-size 64
"""

import argparse
import json
import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL_NAME, VECTOR_STORE_DIR

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "dataset" / "processed"

# Defaults
DEFAULT_BATCH_SIZE = 64


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

_model_cache: SentenceTransformer | None = None


def get_model(model_name: str = EMBEDDING_MODEL_NAME) -> SentenceTransformer:
    """Load (and cache) the SentenceTransformer embedding model."""
    global _model_cache
    if _model_cache is None:
        print(f"[embedder] Loading model: {model_name}")
        _model_cache = SentenceTransformer(model_name)
        print(
            f"[embedder] Model loaded — embedding dim: {_model_cache.get_sentence_embedding_dimension()}"
        )
    return _model_cache


# ---------------------------------------------------------------------------
# Embedding generation
# ---------------------------------------------------------------------------


def generate_embeddings(
    texts: list[str],
    model: SentenceTransformer | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> np.ndarray:
    """
    Generate embedding vectors for a list of texts.

    Returns an (N, D) numpy array of float32 embeddings.
    """
    if model is None:
        model = get_model()

    print(
        f"[embedder] Generating embeddings for {len(texts)} texts (batch_size={batch_size})"
    )
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,  # L2 normalise for cosine similarity via inner product
    )
    return embeddings.astype(np.float32)


# ---------------------------------------------------------------------------
# FAISS index management
# ---------------------------------------------------------------------------


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build a FAISS flat inner-product index from embeddings.

    Since embeddings are L2-normalised, inner product == cosine similarity.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"[embedder] FAISS index built — {index.ntotal} vectors, dim={dim}")
    return index


def save_index(
    index: faiss.IndexFlatIP,
    metadata: list[dict],
    index_name: str = "jenkins_index",
) -> tuple[Path, Path]:
    """
    Save FAISS index and metadata to vector_store/.

    Files:
        vector_store/<index_name>.faiss    — the FAISS index
        vector_store/<index_name>.meta.pkl — list of metadata dicts
    """
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    index_path = VECTOR_STORE_DIR / f"{index_name}.faiss"
    meta_path = VECTOR_STORE_DIR / f"{index_name}.meta.pkl"

    faiss.write_index(index, str(index_path))
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)

    print(f"[embedder] Saved index  → {index_path}")
    print(f"[embedder] Saved metadata → {meta_path} ({len(metadata)} entries)")
    return index_path, meta_path


def load_index(
    index_name: str = "jenkins_index",
) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """Load a previously saved FAISS index and its metadata."""
    index_path = VECTOR_STORE_DIR / f"{index_name}.faiss"
    meta_path = VECTOR_STORE_DIR / f"{index_name}.meta.pkl"

    index = faiss.read_index(str(index_path))
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)

    print(f"[embedder] Loaded index ({index.ntotal} vectors) from {index_path}")
    return index, metadata


# ---------------------------------------------------------------------------
# End-to-end pipeline
# ---------------------------------------------------------------------------


def load_processed_chunks(filepath: Path) -> list[dict]:
    """Load processed chunks from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_file(
    filename: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """
    Embed a single processed JSON file and save the FAISS index.

    Returns the index and metadata list.
    """
    filepath = PROCESSED_DIR / filename
    if not filepath.exists():
        print(f"[embedder] File not found: {filepath}")
        return None, []

    chunks = load_processed_chunks(filepath)
    if not chunks:
        print(f"[embedder] No chunks in {filepath}")
        return None, []

    texts = [c["text"] for c in chunks]
    metadata = [
        {
            "chunk_id": c["chunk_id"],
            "source": c["source"],
            "category": c["category"],
            "text": c["text"],
        }
        for c in chunks
    ]

    embeddings = generate_embeddings(texts, batch_size=batch_size)
    index = build_faiss_index(embeddings)

    index_name = filepath.stem  # e.g. "jenkins_docs"
    save_index(index, metadata, index_name=index_name)

    return index, metadata


def embed_all(
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """
    Embed all processed JSON files and build a single combined FAISS index.

    Saves:
        vector_store/jenkins_index.faiss
        vector_store/jenkins_index.meta.pkl
    """
    if not PROCESSED_DIR.exists():
        print(f"[embedder] Processed directory not found: {PROCESSED_DIR}")
        return None, []

    all_texts: list[str] = []
    all_metadata: list[dict] = []

    for json_file in sorted(PROCESSED_DIR.glob("*.json")):
        print(f"[embedder] Loading: {json_file.name}")
        chunks = load_processed_chunks(json_file)
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
        print("[embedder] No texts found to embed")
        return None, []

    print(f"[embedder] Total chunks to embed: {len(all_texts)}")
    embeddings = generate_embeddings(all_texts, batch_size=batch_size)
    index = build_faiss_index(embeddings)
    save_index(index, all_metadata, index_name="jenkins_index")

    return index, all_metadata


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate embeddings and build FAISS index"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Specific processed JSON file to embed (e.g. jenkins_docs.json). Embeds all if omitted.",
    )
    parser.add_argument(
        "--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Encoding batch size"
    )
    args = parser.parse_args()

    if args.file:
        embed_file(args.file, batch_size=args.batch_size)
    else:
        embed_all(batch_size=args.batch_size)
