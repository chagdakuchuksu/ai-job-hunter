import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def make_pdf(text: str | None = "Hello", pages: int = 1) -> bytes:
    """Build a small PDF in memory. `text=None` produces blank pages."""
    doc = pymupdf.open()
    for _ in range(pages):
        page = doc.new_page()
        if text:
            page.insert_textbox(pymupdf.Rect(50, 50, 550, 800), text, fontsize=10)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def pdf_factory():
    return make_pdf
