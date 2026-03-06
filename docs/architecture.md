# Architecture

## System Overview

```
User Query
    ↓
Jenkins Chat UI (React + TypeScript)
    ↓
Jenkins Plugin (Java — .hpi)
    ↓
AI Backend API (FastAPI)
    ↓
┌──────────────────────────────────────────┐
│            RAG Pipeline                   │
│                                          │
│  Query Processor → Embedding Model       │
│        ↓                                 │
│  Vector Search (FAISS) → Top-K Docs      │
│        ↓                                 │
│  Context Builder → LLM → Response        │
└──────────────────────────────────────────┘
```

## Component Breakdown

### Frontend (React + TypeScript + TailwindCSS)
- **ChatWindow** — Main chat orchestrator, manages conversation state
- **ChatMessage** — Individual message bubble (user/assistant)
- **InputBox** — Auto-resizing textarea with Enter-to-send
- **LoadingIndicator** — Animated typing dots during response generation

### Backend (Python + FastAPI)

| Module | Path | Responsibility |
|---|---|---|
| API Service | `backend/api/main.py` | REST endpoints (`/ask`, `/troubleshoot`, `/workflows`) |
| Query Processor | `backend/rag/query_processor.py` | Normalize + embed user queries |
| Vector Index | `backend/rag/vector_index.py` | FAISS index build, load, search |
| Retriever | `backend/rag/retriever.py` | End-to-end document retrieval |
| Context Builder | `backend/rag/context_builder.py` | Format retrieved docs into LLM prompt |
| Response Generator | `backend/rag/response_generator.py` | LLM inference (HF / Ollama) |
| Workflow Guide | `backend/services/workflow_guide.py` | Step-by-step Jenkins workflow instructions |
| Troubleshooter | `backend/services/troubleshooter.py` | Error log analysis + solution matching |
| Cache | `backend/services/cache.py` | LRU caching for search + embeddings |

### Data Pipeline

| Module | Path | Responsibility |
|---|---|---|
| Doc Crawler | `backend/ingestion/crawler_docs.py` | Crawl jenkins.io/doc/ |
| Plugin Crawler | `backend/ingestion/crawler_plugins.py` | Crawl plugins.jenkins.io |
| GitHub Crawler | `backend/ingestion/crawler_github.py` | Fetch jenkinsci READMEs |
| Community Crawler | `backend/ingestion/crawler_community.py` | Fetch community.jenkins.io topics |
| Cleaner | `backend/ingestion/cleaner.py` | HTML cleaning + text normalization |
| Preprocessor | `backend/embeddings/preprocessor.py` | Sentence-aware text chunking |
| Embedder | `backend/embeddings/embedder.py` | SentenceTransformers embedding generation |

### Jenkins Plugin (Java)
- **AiAssistantAction** — RootAction adding sidebar link + chat proxy
- Jelly views + CSS/JS for in-Jenkins chat UI
- Communicates with FastAPI backend via HTTP

## Data Flow

1. **Ingestion**: Crawlers → Raw JSON → `dataset/raw/`
2. **Preprocessing**: Raw JSON → Chunked JSON → `dataset/processed/`
3. **Embedding**: Chunks → SentenceTransformers → FAISS index → `vector_store/`
4. **Query time**: User query → Normalize → Embed → FAISS search → Context → LLM → Response
