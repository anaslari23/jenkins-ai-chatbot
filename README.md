# Jenkins AI Chatbot

AI-powered chatbot integrated into Jenkins that assists users in navigating workflows, configuring pipelines, installing plugins, and troubleshooting common issues using natural language queries.

Runs completely locally using open-source ML models and retrieval-augmented generation (RAG).

## Features

- **Workflow Guidance** — Step-by-step instructions for pipelines, plugins, agents, credentials, webhooks
- **Documentation Search** — RAG-powered semantic search over Jenkins docs, plugins, GitHub repos, community
- **Troubleshooting** — Paste error logs and get diagnostic analysis with suggested fixes
- **Pipeline Templates** — Example Jenkinsfiles for common setups (Node.js, Maven, Docker)
- **Jenkins Integration** — Custom `.hpi` plugin embeds chat directly in Jenkins dashboard
- **Local-First** — All AI models run locally (no cloud APIs required)

## Architecture

```
User Query → Jenkins Chat UI (React) → Jenkins Plugin (Java)
                                              ↓
                                    FastAPI Backend (Python)
                                              ↓
                               Query Processor → Embedding Model
                                              ↓
                               FAISS Vector Search → Top-K Docs
                                              ↓
                               Context Builder → LLM → Response
```

## Quick Start

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Generate Dataset

```bash
cd backend && source venv/bin/activate
python -m ingestion.crawler_docs
python -m embeddings.preprocessor
python -m rag.vector_index --build
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/workflows` | List workflow topics |
| POST | `/ask` | Ask a question → AI answer + sources |
| POST | `/troubleshoot` | Analyze error logs → solutions |

### Example

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How to create a Jenkins pipeline?"}'
```

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript, TailwindCSS |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS |
| LLM | HuggingFace Transformers / Ollama |
| Jenkins Plugin | Java, Maven (hpi) |

## Project Structure

```
jenkins-ai-chatbot/
├── backend/
│   ├── api/main.py              # FastAPI endpoints
│   ├── config/settings.py       # Configuration
│   ├── embeddings/
│   │   ├── embedder.py          # Embedding generation
│   │   └── preprocessor.py      # Document chunking
│   ├── ingestion/               # Data crawlers
│   ├── rag/
│   │   ├── context_builder.py   # LLM prompt construction
│   │   ├── query_processor.py   # Query normalization
│   │   ├── response_generator.py# LLM response generation
│   │   ├── retriever.py         # Document retrieval
│   │   └── vector_index.py      # FAISS index management
│   └── services/
│       ├── cache.py             # Performance caching
│       ├── troubleshooter.py    # Error log analysis
│       └── workflow_guide.py    # Workflow instructions
├── frontend/src/
│   ├── components/              # React chat components
│   └── services/api.ts          # API client
├── plugin/                      # Jenkins plugin (Java)
├── tests/                       # Pytest test suite
├── docs/                        # Documentation
├── dataset/                     # Raw + processed data
└── vector_store/                # FAISS indexes
```

## Testing

```bash
pip install pytest httpx
python -m pytest tests/ -v
```

26 tests covering preprocessing, retrieval, API endpoints, workflow guidance, and troubleshooting.

## Documentation

- [Architecture](docs/architecture.md)
- [Installation Guide](docs/installation.md)
- [Dataset Generation](docs/dataset.md)
- [Jenkins Plugin Guide](docs/plugin_guide.md)

## License

MIT
