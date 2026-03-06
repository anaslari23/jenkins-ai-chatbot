# Jenkins AI Chatbot

An AI-powered chatbot integrated into Jenkins that assists users in navigating Jenkins workflows, configuring pipelines, installing plugins, and troubleshooting common issues using natural language queries.

## Key Features

- **Natural Language Interface** — Ask questions about Jenkins in plain English directly from the Jenkins dashboard.
- **Retrieval-Augmented Generation (RAG)** — Combines vector search over Jenkins documentation with a local LLM for accurate, contextual answers.
- **Fully Local** — Runs entirely on your infrastructure using open-source models. No data leaves your network.
- **Jenkins Plugin** — A custom Jenkins plugin provides a polished chat UI inside the Jenkins dashboard.

## Architecture

```
User Query
    ↓
Jenkins Chat UI (React + TypeScript)
    ↓
Jenkins Plugin (Java)
    ↓
AI Backend API (FastAPI)
    ↓
Query Processor
    ↓
Embedding Model (all-MiniLM-L6-v2)
    ↓
Vector Search (FAISS)
    ↓
Retrieved Jenkins Knowledge
    ↓
Local LLM Response Generation (Mistral / LLaMA)
    ↓
Formatted Answer → Response returned to Jenkins UI
```

## Technology Stack

| Layer | Technology |
|---|---|
| Backend AI Service | Python, FastAPI |
| Retrieval System | LangChain, LlamaIndex |
| Embedding Model | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector Database | FAISS |
| LLM | Mistral / LLaMA (local) |
| Frontend | React, TypeScript, TailwindCSS |
| Plugin Integration | Jenkins Plugin SDK (Java) |
| Data Ingestion | BeautifulSoup, Scrapy, Requests |
| Testing | pytest |

## Project Structure

```
jenkins-ai-chatbot/
├── backend/            # FastAPI backend & RAG pipeline
│   ├── api/            # REST API routes
│   ├── rag/            # RAG query engine
│   ├── embeddings/     # Embedding model utilities
│   ├── ingestion/      # Document ingestion pipeline
│   ├── services/       # Business logic services
│   └── config/         # Configuration & settings
├── dataset/            # Training / knowledge data
│   ├── raw/            # Raw scraped data
│   ├── processed/      # Cleaned & chunked documents
│   └── metadata/       # Metadata about sources
├── vector_store/       # FAISS index files
├── frontend/           # React + TS chat UI
├── plugin/             # Jenkins plugin (Java)
│   └── jenkins-ai-assistant-plugin/
├── scripts/            # Utility scripts
├── tests/              # Test suite
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Java 11+ (for Jenkins plugin development)
- Git

### 1. Clone the Repository

```bash
git clone <repo-url>
cd jenkins-ai-chatbot
```

### 2. Set Up the Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

### 3. Run the Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Set Up the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the API

- API: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

## License

This project is for educational and internal use.
