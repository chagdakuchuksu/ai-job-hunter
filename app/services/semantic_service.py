"""Semantic similarity between CV text and job description using sentence embeddings.

Uses sentence-transformers with a small local model (all-MiniLM-L6-v2 by
default, ~90 MB, runs on CPU). The model only sees ~256 tokens at a time, so
long texts are split into word chunks; each text's chunk embeddings are
averaged into one vector, and the two vectors are compared with cosine
similarity.

This is kept separate from skill matching on purpose: it measures how similar
the overall *wording/topic* of the two texts is, not whether skills match.
"""

import logging
import threading
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)

CHUNK_WORDS = 150
MAX_CHUNKS = 40  # keeps very long inputs from making requests slow

_model: Any = None
_model_error: str | None = None
_lock = threading.Lock()


@dataclass
class SemanticSimilarity:
    available: bool
    score: float | None = None  # raw cosine similarity, -1..1
    percentage: int | None = None  # score clamped to 0..1, as a percentage
    model: str | None = None
    message: str | None = None


def _load_model() -> Any:
    """Load the embedding model once. Imported lazily so the app starts fast."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(get_settings().embedding_model, device="cpu")


def get_model() -> Any | None:
    global _model, _model_error
    with _lock:
        if _model is None and _model_error is None:
            try:
                _model = _load_model()
            except Exception:
                logger.exception("Could not load the embedding model")
                _model_error = "The embedding model could not be loaded."
        return _model


def chunk_text(text: str, size: int = CHUNK_WORDS) -> list[str]:
    words = text.split()
    chunks = [" ".join(words[i : i + size]) for i in range(0, len(words), size)]
    return chunks[:MAX_CHUNKS]


def _document_vector(model: Any, text: str) -> np.ndarray:
    embeddings = np.asarray(
        model.encode(chunk_text(text), normalize_embeddings=True, show_progress_bar=False)
    )
    vector = embeddings.mean(axis=0)
    return vector / (np.linalg.norm(vector) or 1.0)


def cosine_to_percentage(score: float) -> int:
    return round(max(0.0, min(1.0, score)) * 100)


def compute_similarity(cv_text: str, job_text: str) -> SemanticSimilarity:
    settings = get_settings()
    if not settings.semantic_enabled:
        return SemanticSimilarity(
            available=False, message="Semantic similarity is disabled (SEMANTIC_ENABLED=false)."
        )

    model = get_model()
    if model is None:
        return SemanticSimilarity(available=False, message=_model_error)

    try:
        score = float(np.dot(_document_vector(model, cv_text), _document_vector(model, job_text)))
    except Exception:
        logger.exception("Embedding failed")
        return SemanticSimilarity(available=False, message="Semantic similarity could not be computed.")

    return SemanticSimilarity(
        available=True,
        score=round(score, 4),
        percentage=cosine_to_percentage(score),
        model=settings.embedding_model,
    )
