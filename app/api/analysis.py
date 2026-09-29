from fastapi import APIRouter, File, Form, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.schemas.analysis import AnalysisResponse
from app.schemas.job import RAW_JOB_TEXT_LIMIT
from app.services.analysis_service import run_analysis
from app.services.cv_service import extract_cv_text, read_pdf_upload
from app.services.job_service import prepare_job_description

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    cv_file: UploadFile = File(..., description="CV as a PDF file"),
    job_description: str = Form(..., max_length=RAW_JOB_TEXT_LIMIT),
):
    """Full analysis: CV PDF + job description -> skill match and semantic similarity."""
    # Validate the cheap input first so a bad job description fails fast.
    job = prepare_job_description(job_description)
    pdf_bytes = await read_pdf_upload(cv_file)
    cv = extract_cv_text(cv_file.filename or "cv.pdf", pdf_bytes)
    # Computing embeddings is slow/blocking, so keep it off the event loop.
    analysis = await run_in_threadpool(run_analysis, cv, job)
    return AnalysisResponse.from_analysis(analysis)
