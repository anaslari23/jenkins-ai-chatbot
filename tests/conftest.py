"""
Jenkins AI Chatbot — Test Configuration

Shared fixtures for pytest test suite.
"""

import sys
from pathlib import Path

import pytest

# Ensure backend package is importable
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def sample_html():
    """Sample HTML document for cleaner tests."""
    return """
    <html>
    <head><title>Jenkins Pipeline</title></head>
    <body>
        <nav>Navigation bar</nav>
        <script>var x = 1;</script>
        <style>.foo { color: red; }</style>
        <header>Site header</header>
        <h1>Getting Started with Pipelines</h1>
        <p>Jenkins Pipeline is a suite of plugins that supports
        implementing continuous delivery pipelines.</p>
        <p>A pipeline is defined in a Jenkinsfile.</p>
        <footer>Site footer</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_records():
    """Sample raw records for preprocessing tests."""
    return [
        {
            "id": "test-001",
            "title": "Test Document 1",
            "source_url": "https://jenkins.io/doc/test1",
            "content": (
                "Jenkins Pipeline provides an extensible "
                "set of tools for modeling delivery pipelines. "
                "The definition of a Jenkins Pipeline is "
                "written into a text file called a Jenkinsfile."
            ),
            "category": "docs",
        },
        {
            "id": "test-002",
            "title": "Test Document 2",
            "source_url": "https://jenkins.io/doc/test2",
            "content": (
                "Blue Ocean is a project that rethinks "
                "the Jenkins user experience. "
                "It provides a modern and visual interface "
                "for continuous delivery pipelines."
            ),
            "category": "docs",
        },
    ]


@pytest.fixture
def sample_chunks():
    """Sample processed chunks."""
    return [
        {
            "chunk_id": "test-001_chunk_0",
            "text": (
                "Jenkins Pipeline provides an extensible "
                "set of tools for modeling delivery pipelines."
            ),
            "source": "https://jenkins.io/doc/test1",
            "category": "docs",
        },
        {
            "chunk_id": "test-002_chunk_0",
            "text": (
                "Blue Ocean is a project that rethinks the Jenkins user experience."
            ),
            "source": "https://jenkins.io/doc/test2",
            "category": "docs",
        },
    ]


@pytest.fixture
def error_log_oom():
    """Sample OOM error log."""
    return (
        "java.lang.OutOfMemoryError: Java heap space\n"
        "  at java.util.Arrays.copyOf(Arrays.java:3210)\n"
        "  at hudson.model.Build.execute(Build.java:180)"
    )


@pytest.fixture
def error_log_permission():
    """Sample permission denied error log."""
    return (
        "FATAL: Permission denied\n"
        "/var/lib/jenkins/workspace/my-job: "
        "Permission denied\nBuild step failed"
    )
