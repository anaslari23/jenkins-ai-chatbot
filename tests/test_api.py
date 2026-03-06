"""
Tests for FastAPI API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from api.main import app

    return TestClient(app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Jenkins AI Chatbot" in data["service"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workflows(client):
    response = client.get("/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert len(data["workflows"]) >= 6


def test_ask_workflow(client):
    """Test /ask with a query that matches a known workflow."""
    response = client.post(
        "/ask",
        json={"question": "How to create a Jenkins pipeline"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["answer"]) > 0


def test_ask_empty(client):
    """Test /ask with empty question returns 422."""
    response = client.post(
        "/ask",
        json={"question": ""},
    )
    assert response.status_code == 422


def test_troubleshoot_oom(client):
    """Test /troubleshoot with OOM error."""
    response = client.post(
        "/troubleshoot",
        json={"log": "java.lang.OutOfMemoryError: Java heap space"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_known_pattern"] is True
    assert len(data["matches"]) > 0


def test_troubleshoot_empty(client):
    """Test /troubleshoot with empty log returns 422."""
    response = client.post(
        "/troubleshoot",
        json={"log": ""},
    )
    assert response.status_code == 422
