"""
Jenkins AI Chatbot — Document Preprocessor

Loads raw JSON dataset files from dataset/raw/, chunks documents into
smaller text segments suitable for embedding, and saves the processed
chunks to dataset/processed/.

Each output chunk record:
    {
        "chunk_id": "<source_id>_chunk_<N>",
        "text": "chunk text ...",
        "source": "original URL",
        "category": "docs | plugins | github | community"
    }

Usage:
    python -m embeddings.preprocessor                     # process all
    python -m embeddings.preprocessor --file jenkins_docs.json
    python -m embeddings.preprocessor --chunk-size 800 --overlap 100
"""

import argparse
import json
import re
from pathlib import Path

from config.settings import CHUNK_OVERLAP, CHUNK_SIZE

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "dataset" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "dataset" / "processed"


# ---------------------------------------------------------------------------
# Tokenisation helpers
# ---------------------------------------------------------------------------


def _approx_token_count(text: str) -> int:
    """
    Approximate token count using whitespace splitting.

    For English text this is a reasonable proxy for sub-word tokeniser
    counts without needing a full tokeniser dependency at this stage.
    """
    return len(text.split())


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentence-like units to avoid cutting mid-sentence."""
    # Split on sentence-ending punctuation followed by whitespace
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# Core chunking
# ---------------------------------------------------------------------------


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split *text* into token-bounded chunks with overlap.

    Strategy:
    1. Split text into sentences.
    2. Accumulate sentences until adding the next one would exceed
       *chunk_size* tokens.
    3. Emit the chunk and start the next one from the last *overlap*
       tokens' worth of sentences to maintain context continuity.

    Returns a list of chunk strings.
    """
    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    chunks: list[str] = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sent_tokens = _approx_token_count(sentence)

        # If a single sentence exceeds chunk_size, include it as-is
        if sent_tokens > chunk_size:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
            chunks.append(sentence)
            current_sentences = []
            current_tokens = 0
            continue

        if current_tokens + sent_tokens > chunk_size and current_sentences:
            # Emit current chunk
            chunks.append(" ".join(current_sentences))

            # Build overlap: walk backwards through current_sentences
            overlap_sentences: list[str] = []
            overlap_tokens = 0
            for s in reversed(current_sentences):
                s_tok = _approx_token_count(s)
                if overlap_tokens + s_tok > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_tokens += s_tok

            current_sentences = overlap_sentences
            current_tokens = overlap_tokens

        current_sentences.append(sentence)
        current_tokens += sent_tokens

    # Final chunk
    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------


def load_raw_records(filepath: Path) -> list[dict]:
    """Load a JSON array of records from a raw dataset file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def process_records(
    records: list[dict],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Chunk a list of raw records and return processed chunk records.

    Each output record:
        chunk_id  — "<record_id>_chunk_<N>"
        text      — chunk text
        source    — original source URL
        category  — original category
    """
    chunks: list[dict] = []

    for record in records:
        record_id = record.get("id", "unknown")
        content = record.get("content", "")
        source_url = record.get("source_url", "")
        category = record.get("category", "unknown")

        if not content.strip():
            continue

        text_chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)

        for idx, chunk_text_str in enumerate(text_chunks):
            chunks.append(
                {
                    "chunk_id": f"{record_id}_chunk_{idx}",
                    "text": chunk_text_str,
                    "source": source_url,
                    "category": category,
                }
            )

    return chunks


def save_processed(chunks: list[dict], filename: str) -> Path:
    """Save processed chunks as JSON to dataset/processed/."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PROCESSED_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"[preprocessor] Saved {len(chunks)} chunks → {filepath}")
    return filepath


def process_file(
    input_filename: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Process a single raw JSON file end-to-end.

    Loads from dataset/raw/<input_filename>,
    chunks all records,
    saves to dataset/processed/<input_filename>.
    """
    input_path = RAW_DIR / input_filename
    if not input_path.exists():
        print(f"[preprocessor] File not found: {input_path}")
        return []

    print(f"[preprocessor] Processing {input_path}")
    records = load_raw_records(input_path)
    chunks = process_records(records, chunk_size=chunk_size, overlap=overlap)
    save_processed(chunks, input_filename)
    return chunks


def process_all(
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """Process all JSON files in dataset/raw/."""
    if not RAW_DIR.exists():
        print(f"[preprocessor] Raw directory not found: {RAW_DIR}")
        return []

    all_chunks: list[dict] = []
    for json_file in sorted(RAW_DIR.glob("*.json")):
        chunks = process_file(
            json_file.name,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        all_chunks.extend(chunks)

    print(f"[preprocessor] Total chunks across all files: {len(all_chunks)}")
    return all_chunks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess raw dataset into chunks")
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Specific raw JSON file to process (e.g. jenkins_docs.json). Processes all if omitted.",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=CHUNK_SIZE, help="Max tokens per chunk"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help="Overlap tokens between chunks",
    )
    args = parser.parse_args()

    if args.file:
        process_file(args.file, chunk_size=args.chunk_size, overlap=args.overlap)
    else:
        process_all(chunk_size=args.chunk_size, overlap=args.overlap)
