import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_questions_empty():
    """Test questions endpoint when empty."""
    response = client.get("/questions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_questions_pagination():
    """Test questions pagination."""
    response = client.get("/questions?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_quiz_endpoint():
    """Test quiz endpoint."""
    response = client.get("/quiz?limit=5")
    assert response.status_code in [200, 404]  # 404 if no questions


def test_upload_no_file():
    """Test upload without file."""
    response = client.post("/upload")
    assert response.status_code == 422


def test_upload_invalid_file():
    """Test upload with non-PDF file."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"not a pdf", "text/plain")}
    )
    assert response.status_code == 400
