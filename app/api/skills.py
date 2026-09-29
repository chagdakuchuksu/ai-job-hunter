from fastapi import APIRouter

from app.errors import AppError
from app.schemas.skills import SkillMatchRequest, SkillMatchResponse
from app.services.job_service import prepare_job_description
from app.services.matching_service import match_skills
from app.services.skill_service import extract_skills
from app.utils.text import normalize_text

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.post("/match", response_model=SkillMatchResponse)
def match_texts(request: SkillMatchRequest):
    """Compare skills in CV text and job description text (no PDF needed)."""
    cv_text = normalize_text(request.cv_text)
    if not cv_text:
        raise AppError("CV text is required.", status_code=422)
    job = prepare_job_description(request.job_description)
    match = match_skills(extract_skills(cv_text), extract_skills(job.text))
    return SkillMatchResponse.from_match(match)
