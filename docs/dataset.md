# Dataset Generation Guide

## Overview

The dataset generation pipeline collects, cleans, chunks, and embeds Jenkins knowledge from four sources:

1. **Jenkins Documentation** — jenkins.io/doc/
2. **Jenkins Plugins** — plugins.jenkins.io
3. **GitHub Repositories** — github.com/jenkinsci
4. **Community Discussions** — community.jenkins.io

## Pipeline Stages

### Stage 1: Crawling (Raw Data Collection)

Each crawler fetches content and saves cleaned JSON to `dataset/raw/`.

```bash
cd backend && source venv/bin/activate

# Crawl documentation (~50-100 pages)
python -m ingestion.crawler_docs

# Crawl plugin pages (~50 plugins)
python -m ingestion.crawler_plugins

# Fetch GitHub READMEs (~30 repos)
python -m ingestion.crawler_github

# Fetch community topics (~50 discussions)
python -m ingestion.crawler_community
```

Output files:
- `dataset/raw/jenkins_docs.json`
- `dataset/raw/jenkins_plugins.json`
- `dataset/raw/jenkins_github.json`
- `dataset/raw/jenkins_community.json`

### Record Schema

```json
{
  "id": "uuid",
  "title": "Page Title",
  "source_url": "https://...",
  "content": "Cleaned text content...",
  "category": "docs | plugins | github | community"
}
```

### Stage 2: Preprocessing (Chunking)

Splits documents into overlapping chunks for better retrieval:

```bash
python -m embeddings.preprocessor
```

- **Chunk size**: 800 tokens (configurable in `config/settings.py`)
- **Overlap**: 100 tokens
- **Method**: Sentence-aware splitting (no mid-sentence breaks)
- **Output**: `dataset/processed/*.json`

### Chunk Schema

```json
{
  "chunk_id": "original_id_chunk_0",
  "text": "Chunk text...",
  "source": "https://original-url",
  "category": "docs"
}
```

### Stage 3: Embedding & Indexing

Generates vector embeddings and builds FAISS index:

```bash
# Generate embeddings
python -m embeddings.embedder

# Build searchable index
python -m rag.vector_index --build
```

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Index type**: FAISS IndexFlatIP (cosine similarity)
- **Output**: `vector_store/jenkins_index.faiss` + `jenkins_index.meta.pkl`

## Updating the Dataset

To add new data or refresh:

1. Re-run the relevant crawler(s)
2. Re-run the preprocessor
3. Re-run the embedder and index builder
4. Restart the backend to reload the index

## Configuration

Edit `backend/config/settings.py` to adjust:

| Setting | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `CHUNK_SIZE` | `800` | Tokens per chunk |
| `CHUNK_OVERLAP` | `100` | Token overlap between chunks |
