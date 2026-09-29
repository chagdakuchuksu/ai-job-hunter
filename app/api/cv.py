from fastapi import APIRouter, File, UploadFile

from app.schemas.cv import CVResponse
from app.services.cv_service import extract_cv_text, read_pdf_upload
from app.services.skill_service import extract_skills

router = APIRouter(prefix="/api/cv", tags=["cv"])


@router.post("/upload", response_model=CVResponse)
async def upload_cv(file: UploadFile = File(..., description="CV as a PDF file")):
    """Upload a CV (PDF) and return its extracted text and detected skills."""
    pdf_bytes = await read_pdf_upload(file)
    cv = extract_cv_text(file.filename or "cv.pdf", pdf_bytes)
    return CVResponse.from_document(cv, extract_skills(cv.text))
