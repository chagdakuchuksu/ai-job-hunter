from fastapi.testclient import TestClient

from app.main import app
from app.services import semantic_service


def count_model_loads(monkeypatch) -> list[int]:
    calls = []
    monkeypatch.setattr(semantic_service, "get_model", lambda: calls.append(1))
    return calls


def test_model_is_not_preloaded_by_default(monkeypatch):
    monkeypatch.delenv("PRELOAD_EMBEDDING_MODEL", raising=False)
    calls = count_model_loads(monkeypatch)
    with TestClient(app) as client:  # the `with` block runs startup/shutdown
        assert client.get("/health").status_code == 200
    assert calls == []


def test_model_is_preloaded_when_enabled(monkeypatch):
    monkeypatch.setenv("PRELOAD_EMBEDDING_MODEL", "true")
    calls = count_model_loads(monkeypatch)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
    assert calls == [1]


def test_no_preload_when_semantic_disabled(monkeypatch):
    monkeypatch.setenv("PRELOAD_EMBEDDING_MODEL", "true")
    monkeypatch.setenv("SEMANTIC_ENABLED", "false")
    calls = count_model_loads(monkeypatch)
    with TestClient(app):
        pass
    assert calls == []
