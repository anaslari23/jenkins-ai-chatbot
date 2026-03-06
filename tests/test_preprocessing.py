"""
Tests for document preprocessing (cleaner + preprocessor).
"""


def test_clean_html_removes_scripts(sample_html):
    from ingestion.cleaner import clean_html

    result = clean_html(sample_html)
    assert "var x = 1" not in result
    assert "color: red" not in result


def test_clean_html_removes_nav(sample_html):
    from ingestion.cleaner import clean_html

    result = clean_html(sample_html)
    assert "Navigation bar" not in result
    assert "Site footer" not in result
    assert "Site header" not in result


def test_clean_html_preserves_content(sample_html):
    from ingestion.cleaner import clean_html

    result = clean_html(sample_html)
    assert "Getting Started with Pipelines" in result
    assert "continuous delivery pipelines" in result
    assert "Jenkinsfile" in result


def test_extract_title(sample_html):
    from ingestion.cleaner import extract_title

    title = extract_title(sample_html)
    assert title == "Jenkins Pipeline"


def test_make_record():
    from ingestion.cleaner import make_record

    record = make_record(
        "Test Title",
        "https://example.com",
        "Test content",
        "docs",
    )
    assert record["title"] == "Test Title"
    assert record["source_url"] == "https://example.com"
    assert record["content"] == "Test content"
    assert record["category"] == "docs"
    assert len(record["id"]) == 36  # UUID format


def test_chunk_text_basic():
    from embeddings.preprocessor import chunk_text

    # Create many sentences to ensure chunking triggers
    sentences = [f"This is sentence number {i} about Jenkins." for i in range(200)]
    text = " ".join(sentences)
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) > 1


def test_chunk_text_overlap():
    from embeddings.preprocessor import chunk_text

    text = ". ".join([f"Sentence {i}" for i in range(50)])
    chunks = chunk_text(text, chunk_size=10, overlap=3)
    assert len(chunks) > 1
    # Check that chunks share some content (overlap)
    if len(chunks) >= 2:
        last_words_first = set(chunks[0].split()[-5:])
        first_words_second = set(chunks[1].split()[:5])
        # There should be some overlap
        assert len(last_words_first & first_words_second) > 0


def test_process_records(sample_records):
    from embeddings.preprocessor import process_records

    chunks = process_records(
        sample_records,
        chunk_size=50,
        overlap=10,
    )
    assert len(chunks) > 0
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "source" in chunk
        assert "category" in chunk
        assert chunk["category"] == "docs"
