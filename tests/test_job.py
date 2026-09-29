JOB = "We are hiring a Python developer.\n\n\n\nExperience with FastAPI   and SQL."


def post_job(client, payload):
    return client.post("/api/job/analyze", json=payload)


def test_valid_job_is_normalized(client):
    response = post_job(client, {"description": JOB})
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == (
        "We are hiring a Python developer.\n\nExperience with FastAPI and SQL."
    )
    assert body["char_count"] == len(body["text"])
    assert body["word_count"] == 11


def test_missing_description_returns_422(client):
    assert post_job(client, {}).status_code == 422


def test_wrong_type_returns_422(client):
    assert post_job(client, {"description": 123}).status_code == 422


def test_whitespace_only_is_rejected(client):
    response = post_job(client, {"description": "   \n\t  "})
    assert response.status_code == 422
    assert response.json()["detail"] == "Job description is required."


def test_too_short_is_rejected(client):
    response = post_job(client, {"description": "Python dev"})
    assert response.status_code == 422
    assert "too short" in response.json()["detail"]


def test_too_long_is_rejected(client, monkeypatch):
    monkeypatch.setenv("MAX_JOB_CHARS", "100")
    response = post_job(client, {"description": "word " * 50})
    assert response.status_code == 422
    assert "too long" in response.json()["detail"]


def test_malformed_json_returns_422(client):
    response = client.post(
        "/api/job/analyze",
        content=b"{not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
