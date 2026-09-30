"""Application settings, read from environment variables (and a local .env file).

Settings are read on every call to `get_settings()` so tests can change
environment variables with monkeypatch without restarting anything.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    try:
        return int(value) if value else default
    except ValueError:
        return default


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    max_upload_mb: int
    max_pdf_pages: int
    max_job_chars: int
    min_job_chars: int
    semantic_enabled: bool
    embedding_model: str
    preload_embedding_model: bool
    cors_origins: list[str]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


def get_settings() -> Settings:
    origins = os.getenv(
        "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    )
    return Settings(
        max_upload_mb=_int_env("MAX_UPLOAD_MB", 5),
        max_pdf_pages=_int_env("MAX_PDF_PAGES", 20),
        max_job_chars=_int_env("MAX_JOB_CHARS", 20_000),
        min_job_chars=_int_env("MIN_JOB_CHARS", 30),
        semantic_enabled=_bool_env("SEMANTIC_ENABLED", True),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        preload_embedding_model=_bool_env("PRELOAD_EMBEDDING_MODEL", False),
        cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
    )
