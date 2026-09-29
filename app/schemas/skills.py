from pydantic import BaseModel, Field

from app.schemas.job import RAW_JOB_TEXT_LIMIT
from app.services.matching_service import SkillMatch


class SkillMatchRequest(BaseModel):
    cv_text: str = Field(..., max_length=RAW_JOB_TEXT_LIMIT)
    job_description: str = Field(..., max_length=RAW_JOB_TEXT_LIMIT)


class SkillMatchResponse(BaseModel):
    match_percentage: int | None = Field(
        description="Matched job skills / job skills detected x 100. "
        "Null when no skills were detected in the job description. "
        "A demo metric, not a hiring prediction."
    )
    matched_skills: list[str]
    missing_skills: list[str]
    additional_skills: list[str]
    cv_skills: list[str]
    job_skills: list[str]
    explanation: str

    @classmethod
    def from_match(cls, match: SkillMatch) -> "SkillMatchResponse":
        return cls(**match.__dict__)
