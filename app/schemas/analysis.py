from pydantic import BaseModel

from app.schemas.cv import CVResponse
from app.schemas.job import JobResponse
from app.schemas.skills import SkillMatchResponse
from app.services.analysis_service import FullAnalysis

DISCLAIMER = (
    "These results are technical indicators for self-improvement only. "
    "They are not a hiring prediction or an automated hiring decision."
)


class SemanticSimilarityResponse(BaseModel):
    available: bool
    score: float | None
    percentage: int | None
    model: str | None
    message: str | None


class AnalysisResponse(BaseModel):
    cv: CVResponse
    job: JobResponse
    skill_match: SkillMatchResponse
    semantic_similarity: SemanticSimilarityResponse
    disclaimer: str = DISCLAIMER

    @classmethod
    def from_analysis(cls, a: FullAnalysis) -> "AnalysisResponse":
        return cls(
            cv=CVResponse.from_document(a.cv, a.cv_skills),
            job=JobResponse.from_job(a.job, a.job_skills),
            skill_match=SkillMatchResponse.from_match(a.skill_match),
            semantic_similarity=SemanticSimilarityResponse(**a.semantic_similarity.__dict__),
        )
