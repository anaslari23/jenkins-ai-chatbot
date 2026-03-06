"""
Tests for the retrieval pipeline (query processor, workflow guide,
troubleshooter).
"""


def test_normalize_query():
    from rag.query_processor import normalize_query

    assert normalize_query("  HELLO World!  ") == "hello world"
    assert normalize_query("What is @Jenkins?") == "what is jenkins?"
    assert normalize_query("  multiple   spaces  ") == "multiple spaces"


def test_normalize_query_preserves_punctuation():
    from rag.query_processor import normalize_query

    result = normalize_query("How do I create a pipeline?")
    assert "?" in result
    assert "pipeline" in result


def test_workflow_guidance_pipeline():
    from services.workflow_guide import get_workflow_guidance

    result = get_workflow_guidance("How to create pipeline in Jenkins")
    assert result is not None
    assert "steps" in result
    assert "docs" in result
    assert len(result["steps"]) > 0
    assert "jenkinsfile" in result


def test_workflow_guidance_plugins():
    from services.workflow_guide import get_workflow_guidance

    result = get_workflow_guidance("How to install plugins")
    assert result is not None
    assert "Plugin Manager" in str(result["steps"])


def test_workflow_guidance_nodejs():
    from services.workflow_guide import get_workflow_guidance

    result = get_workflow_guidance("How to configure Jenkins for NodeJS")
    assert result is not None
    assert "NodeJS" in result["title"] or "Node" in result["title"]


def test_workflow_guidance_no_match():
    from services.workflow_guide import get_workflow_guidance

    result = get_workflow_guidance("What is the weather today?")
    assert result is None


def test_workflow_list():
    from services.workflow_guide import get_all_workflow_topics

    topics = get_all_workflow_topics()
    assert len(topics) >= 6


def test_troubleshooter_oom(error_log_oom):
    from services.troubleshooter import analyze_error

    result = analyze_error(error_log_oom)
    assert result["has_known_pattern"] is True
    assert len(result["matches"]) > 0
    assert "OutOfMemoryError" in result["matches"][0]["title"]
    assert len(result["formatted"]) > 0


def test_troubleshooter_permission(error_log_permission):
    from services.troubleshooter import analyze_error

    result = analyze_error(error_log_permission)
    assert result["has_known_pattern"] is True
    assert any("Permission" in m["title"] for m in result["matches"])


def test_troubleshooter_unknown():
    from services.troubleshooter import analyze_error

    result = analyze_error("This is a normal log message")
    assert result["has_known_pattern"] is False
    assert "general troubleshooting" in result["formatted"]


def test_troubleshooter_keywords(error_log_oom):
    from services.troubleshooter import extract_error_keywords

    keywords = extract_error_keywords(error_log_oom)
    assert len(keywords) > 0
    assert any("OutOfMemoryError" in kw for kw in keywords)
