from fastapi import APIRouter

from app.schemas.job import JobRequest, JobResponse
from app.services.job_service import prepare_job_description
from app.services.skill_service import extract_skills

router = APIRouter(prefix="/api/job", tags=["job"])


@router.post("/analyze", response_model=JobResponse)
def analyze_job(request: JobRequest):
    """Validate and normalize a job description and detect its skills."""
    job = prepare_job_description(request.description)
    return JobResponse.from_job(job, extract_skills(job.text))
