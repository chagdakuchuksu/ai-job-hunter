from pydantic import BaseModel, Field

from app.services.job_service import JobDescription

# Hard cap on the raw request body field. The real (configurable) limit is
# checked after normalization in job_service; this only stops absurd payloads.
RAW_JOB_TEXT_LIMIT = 100_000


class JobRequest(BaseModel):
    description: str = Field(..., max_length=RAW_JOB_TEXT_LIMIT)


class JobResponse(BaseModel):
    text: str
    char_count: int
    word_count: int
    skills: list[str]

    @classmethod
    def from_job(cls, job: JobDescription, skills: list[str]) -> "JobResponse":
        return cls(
            text=job.text,
            char_count=job.char_count,
            word_count=job.word_count,
            skills=skills,
        )
