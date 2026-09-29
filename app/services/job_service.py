"""Job description handling: validate and normalize pasted text."""

from dataclasses import dataclass

from app.config import get_settings
from app.errors import AppError
from app.utils.text import normalize_text, word_count


@dataclass
class JobDescription:
    text: str

    @property
    def char_count(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return word_count(self.text)


def prepare_job_description(raw_text: str | None) -> JobDescription:
    """Normalize a job description and check its length.

    Used by both the /api/job endpoint and the full analysis endpoint, so the
    validation rules live in one place.
    """
    settings = get_settings()
    text = normalize_text(raw_text or "")
    if not text:
        raise AppError("Job description is required.", status_code=422)
    if len(text) < settings.min_job_chars:
        raise AppError(
            f"Job description is too short (minimum {settings.min_job_chars} characters).",
            status_code=422,
        )
    if len(text) > settings.max_job_chars:
        raise AppError(
            f"Job description is too long (maximum {settings.max_job_chars} characters).",
            status_code=422,
        )
    return JobDescription(text=text)
