"""CV handling: validate an uploaded PDF and extract its text with PyMuPDF.

CVs are processed in memory and never written to disk.
"""

from dataclasses import dataclass

import pymupdf
from fastapi import UploadFile

from app.config import get_settings
from app.errors import AppError
from app.utils.text import normalize_text, word_count

PDF_MAGIC = b"%PDF-"
_READ_CHUNK = 64 * 1024


@dataclass
class CVDocument:
    filename: str
    page_count: int
    text: str

    @property
    def char_count(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return word_count(self.text)


async def read_pdf_upload(file: UploadFile) -> bytes:
    """Read an uploaded file, rejecting non-PDFs and files over the size limit.

    The file is read in chunks so an oversized upload is rejected without
    loading all of it into memory.
    """
    settings = get_settings()
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise AppError("Only PDF files are supported (.pdf).", status_code=415)

    data = bytearray()
    while chunk := await file.read(_READ_CHUNK):
        data.extend(chunk)
        if len(data) > settings.max_upload_bytes:
            raise AppError(
                f"File is too large. Maximum size is {settings.max_upload_mb} MB.",
                status_code=413,
            )

    if not data:
        raise AppError("The uploaded file is empty.", status_code=400)
    if not bytes(data[:1024]).lstrip().startswith(PDF_MAGIC):
        raise AppError("The file does not look like a valid PDF.", status_code=415)
    return bytes(data)


def extract_cv_text(filename: str, pdf_bytes: bytes) -> CVDocument:
    """Extract normalized text from PDF bytes."""
    settings = get_settings()
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:  # PyMuPDF raises several error types for bad files
        raise AppError("The PDF could not be read. It may be corrupted.") from exc

    with doc:
        if doc.needs_pass:
            raise AppError("Password-protected PDFs are not supported.")
        if doc.page_count == 0:
            raise AppError("The PDF has no pages.")
        if doc.page_count > settings.max_pdf_pages:
            raise AppError(
                f"The PDF has too many pages (maximum {settings.max_pdf_pages})."
            )
        raw_text = "\n".join(page.get_text() for page in doc)
        page_count = doc.page_count

    text = normalize_text(raw_text)
    if not text:
        raise AppError(
            "No text could be extracted from the PDF. Scanned/image-only PDFs "
            "are not supported (no OCR).",
            status_code=422,
        )
    return CVDocument(filename=filename, page_count=page_count, text=text)
