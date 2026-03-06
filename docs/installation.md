# Installation Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Java 11+ and Maven 3.x (for Jenkins plugin)
- Git

## 1. Clone Repository

```bash
git clone https://github.com/anaslari23/jenkins-ai-chatbot.git
cd jenkins-ai-chatbot
```

## 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Frontend Setup

```bash
cd frontend
npm install
```

## 4. Generate Dataset

```bash
cd backend
source venv/bin/activate

# Crawl Jenkins documentation (takes ~10 minutes)
python -m ingestion.crawler_docs
python -m ingestion.crawler_plugins
python -m ingestion.crawler_github
python -m ingestion.crawler_community

# Preprocess into chunks
python -m embeddings.preprocessor

# Generate embeddings and build FAISS index
python -m embeddings.embedder

# Build the vector index
python -m rag.vector_index --build
```

## 5. Start the Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

## 6. Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend available at: http://localhost:5173

## 7. Jenkins Plugin (Optional)

```bash
cd plugin/jenkins-ai-assistant-plugin
mvn package
```

Install the generated `.hpi` from `target/` via Jenkins → Manage Plugins → Advanced → Upload.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_BACKEND` | `transformers` | LLM backend: `transformers` or `ollama` |
| `LLM_MODEL_NAME` | from settings.py | HF model name or Ollama model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `MAX_NEW_TOKENS` | `512` | Max tokens in LLM response |
| `TEMPERATURE` | `0.7` | LLM sampling temperature |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL for frontend |

## Running Tests

```bash
pip install pytest httpx
cd jenkins-ai-chatbot
python -m pytest tests/ -v
```
