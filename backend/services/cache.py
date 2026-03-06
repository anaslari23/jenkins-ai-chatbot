"""
Jenkins AI Chatbot — Performance Optimization

Provides caching, index preloading, and optimized search
to ensure response times under 2 seconds.

Usage:
    from services.cache import cached_search, preload
    preload()  # call at startup
"""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from typing import Any, Optional

import numpy as np


# ---------------------------------------------------------------------------
# LRU Cache for query results
# ---------------------------------------------------------------------------


class LRUCache:
    """Simple thread-safe LRU cache with TTL expiration."""

    def __init__(self, max_size: int = 256, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def _make_key(self, query: str) -> str:
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    def get(self, query: str) -> Any | None:
        key = self._make_key(query)
        if key not in self._cache:
            return None
        ts, value = self._cache[key]
        if time.time() - ts > self.ttl:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    def put(self, query: str, value: Any) -> None:
        key = self._make_key(query)
        self._cache[key] = (time.time(), value)
        self._cache.move_to_end(key)
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


# Global caches
_search_cache = LRUCache(max_size=256, ttl_seconds=3600)
_embedding_cache = LRUCache(max_size=512, ttl_seconds=7200)


# ---------------------------------------------------------------------------
# Cached search
# ---------------------------------------------------------------------------


def cached_search(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Search with caching. Returns cached results if available,
    otherwise performs the search and caches the result.
    """
    cache_key = f"{query}::{top_k}"
    cached = _search_cache.get(cache_key)
    if cached is not None:
        print(f"[cache] Hit for: '{query[:50]}…'")
        return cached

    from rag.retriever import retrieve

    results = retrieve(query, top_k=top_k)
    _search_cache.put(cache_key, results)
    return results


def cached_embedding(text: str) -> np.ndarray:
    """
    Generate embedding with caching. Avoids re-encoding
    duplicate queries.
    """
    cached = _embedding_cache.get(text)
    if cached is not None:
        return cached

    from embeddings.embedder import generate_embeddings

    embedding = generate_embeddings([text])
    _embedding_cache.put(text, embedding)
    return embedding


# ---------------------------------------------------------------------------
# Preloading
# ---------------------------------------------------------------------------

_preloaded = False


def preload() -> None:
    """
    Preload the embedding model and FAISS index at startup
    to eliminate cold-start latency on the first query.
    """
    global _preloaded
    if _preloaded:
        return

    print("[cache] Preloading embedding model and FAISS index…")
    start = time.time()

    try:
        from embeddings.embedder import get_model

        get_model()
    except Exception as e:
        print(f"[cache] Model preload warning: {e}")

    try:
        from rag.vector_index import load_index

        load_index()
    except Exception as e:
        print(f"[cache] Index preload warning: {e}")

    elapsed = time.time() - start
    print(f"[cache] Preload complete in {elapsed:.1f}s")
    _preloaded = True


def clear_caches() -> None:
    """Clear all caches."""
    _search_cache.clear()
    _embedding_cache.clear()
    print("[cache] All caches cleared")


def get_cache_stats() -> dict:
    """Return cache statistics."""
    return {
        "search_cache_size": _search_cache.size,
        "embedding_cache_size": _embedding_cache.size,
    }
