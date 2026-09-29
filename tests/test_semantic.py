import os

import numpy as np
import pytest

from app.services import semantic_service
from app.services.semantic_service import chunk_text, compute_similarity, cosine_to_percentage

VOCAB = ["python", "api", "backend", "data", "cooking", "garden"]


class FakeModel:
    """Bag-of-words 'embedding' so tests are fast and need no download."""

    def encode(self, texts, normalize_embeddings=True, show_progress_bar=False):
        vectors = []
        for text in texts:
            words = text.lower().split()
            v = np.array([words.count(w) for w in VOCAB], dtype=float) + 1e-9
            vectors.append(v / np.linalg.norm(v))
        return np.array(vectors)


@pytest.fixture
def fake_model(monkeypatch):
    monkeypatch.setattr(semantic_service, "_model", FakeModel())
    monkeypatch.setattr(semantic_service, "_model_error", None)


def test_identical_texts_score_100(fake_model):
    result = compute_similarity("python api backend", "python api backend")
    assert result.available
    assert result.percentage == 100


def test_related_texts_score_higher_than_unrelated(fake_model):
    job = "python backend api data"
    related = compute_similarity("python api backend", job)
    unrelated = compute_similarity("cooking garden cooking", job)
    assert related.score > unrelated.score
    assert unrelated.percentage == 0


def test_disabled_by_setting(monkeypatch):
    monkeypatch.setenv("SEMANTIC_ENABLED", "false")
    result = compute_similarity("a", "b")
    assert not result.available
    assert "disabled" in result.message


def test_model_load_failure_is_reported_not_raised(monkeypatch):
    def broken_loader():
        raise OSError("no network")

    monkeypatch.setattr(semantic_service, "_model", None)
    monkeypatch.setattr(semantic_service, "_model_error", None)
    monkeypatch.setattr(semantic_service, "_load_model", broken_loader)
    result = compute_similarity("python", "python")
    assert not result.available
    assert result.message == "The embedding model could not be loaded."
    assert "no network" not in result.message


def test_chunk_text_splits_long_text():
    chunks = chunk_text("word " * 400, size=150)
    assert [len(c.split()) for c in chunks] == [150, 150, 100]


def test_cosine_to_percentage_clamps():
    assert cosine_to_percentage(-0.3) == 0
    assert cosine_to_percentage(0.456) == 46
    assert cosine_to_percentage(1.2) == 100


@pytest.mark.skipif(
    os.getenv("RUN_EMBEDDING_TESTS") != "1",
    reason="Downloads the real embedding model; set RUN_EMBEDDING_TESTS=1 to run.",
)
def test_real_model_ranks_related_text_higher(monkeypatch):
    monkeypatch.setattr(semantic_service, "_model", None)
    monkeypatch.setattr(semantic_service, "_model_error", None)
    job = "Backend developer building REST APIs in Python with FastAPI and PostgreSQL."
    related = compute_similarity("I built web APIs using Python, FastAPI and SQL databases.", job)
    unrelated = compute_similarity("I am a pastry chef who loves baking sourdough bread.", job)
    assert related.available and unrelated.available
    assert related.score > unrelated.score
