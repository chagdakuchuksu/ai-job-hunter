import pytest

from app.services import analysis_service
from app.services.semantic_service import SemanticSimilarity

CV = (
    "Jane Doe - Software Engineering student.\n"
    "Skills: Python, FastAPI, Git, SQL, machine learning.\n"
    "Projects: REST API for a library system."
)
JOB = (
    "Backend intern. Requirements: Python, FastAPI, Docker, SQL and Git. "
    "Nice to have: Kubernetes."
)


@pytest.fixture
def fake_semantic(monkeypatch):
    monkeypatch.setattr(
        analysis_service,
        "compute_similarity",
        lambda cv, job: SemanticSimilarity(available=True, score=0.61, percentage=61, model="fake"),
    )


def post(client, pdf: bytes, job: str = JOB, filename: str = "cv.pdf"):
    return client.post(
        "/api/analyze",
        files={"cv_file": (filename, pdf, "application/pdf")},
        data={"job_description": job},
    )


def test_full_analysis(client, pdf_factory, fake_semantic):
    response = post(client, pdf_factory(CV))
    assert response.status_code == 200
    body = response.json()

    assert set(body) == {"cv", "job", "skill_match", "semantic_similarity", "disclaimer"}
    assert "Python" in body["cv"]["skills"]
    assert body["job"]["skills"] == ["Docker", "FastAPI", "Git", "Kubernetes", "Python", "SQL"]

    match = body["skill_match"]
    assert match["match_percentage"] == 67  # 4 of 6
    assert match["missing_skills"] == ["Docker", "Kubernetes"]
    assert "Machine Learning" in match["additional_skills"]

    assert body["semantic_similarity"]["percentage"] == 61
    assert "not a hiring prediction" in body["disclaimer"]


def test_analysis_rejects_invalid_job(client, pdf_factory, fake_semantic):
    response = post(client, pdf_factory(CV), job="short")
    assert response.status_code == 422
    assert "too short" in response.json()["detail"]


def test_analysis_rejects_non_pdf(client, fake_semantic):
    response = post(client, b"hello", filename="cv.docx")
    assert response.status_code == 415


def test_analysis_missing_fields(client):
    response = client.post("/api/analyze")
    assert response.status_code == 422
    locations = [e["loc"][-1] for e in response.json()["errors"]]
    assert {"cv_file", "job_description"} <= set(locations)


def test_unexpected_error_returns_generic_500(pdf_factory, fake_semantic, monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    def explode(*args):
        raise RuntimeError("database password is hunter2")

    monkeypatch.setattr(analysis_service, "match_skills", explode)
    client = TestClient(app, raise_server_exceptions=False)
    response = post(client, pdf_factory(CV))
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}


def test_frontend_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Job Hunter" in response.text
