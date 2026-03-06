"""
Jenkins AI Chatbot — Configuration
"""

import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
DATASET_DIR = PROJECT_ROOT / "dataset"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Embedding model
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

# LLM settings
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "mistral")

# FAISS
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "jenkins_docs.faiss"

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
