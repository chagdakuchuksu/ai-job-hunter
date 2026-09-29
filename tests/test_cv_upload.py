CV_TEXT = "Jane Doe\nSoftware Engineering student\nSkills: Python, FastAPI, Git"


def upload(client, content: bytes, filename: str = "cv.pdf"):
    files = {"file": (filename, content, "application/pdf")}
    return client.post("/api/cv/upload", files=files)


def test_upload_valid_pdf_extracts_text(client, pdf_factory):
    response = upload(client, pdf_factory(CV_TEXT))
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "cv.pdf"
    assert body["page_count"] == 1
    assert "FastAPI" in body["text"]
    assert body["char_count"] == len(body["text"])
    assert body["word_count"] > 0


def test_upload_multi_page_pdf(client, pdf_factory):
    response = upload(client, pdf_factory(CV_TEXT, pages=3))
    assert response.status_code == 200
    assert response.json()["page_count"] == 3


def test_rejects_non_pdf_extension(client):
    response = upload(client, b"just text", filename="cv.txt")
    assert response.status_code == 415


def test_rejects_fake_pdf_content(client):
    response = upload(client, b"this is not really a pdf")
    assert response.status_code == 415
    assert "valid PDF" in response.json()["detail"]


def test_rejects_empty_file(client):
    response = upload(client, b"")
    assert response.status_code == 400


def test_rejects_corrupted_pdf(client):
    response = upload(client, b"%PDF-1.7\n garbage garbage garbage")
    assert response.status_code == 400
    assert "could not be read" in response.json()["detail"]


def test_rejects_pdf_without_text(client, pdf_factory):
    response = upload(client, pdf_factory(text=None))
    assert response.status_code == 422
    assert "No text" in response.json()["detail"]


def test_rejects_oversized_file(client, monkeypatch, pdf_factory):
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    big = pdf_factory(CV_TEXT) + b"0" * (1024 * 1024 + 1)
    response = upload(client, big)
    assert response.status_code == 413


def test_rejects_too_many_pages(client, monkeypatch, pdf_factory):
    monkeypatch.setenv("MAX_PDF_PAGES", "2")
    response = upload(client, pdf_factory(CV_TEXT, pages=3))
    assert response.status_code == 400
    assert "too many pages" in response.json()["detail"]


def test_missing_file_field_returns_422(client):
    response = client.post("/api/cv/upload")
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid request."
