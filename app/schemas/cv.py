from pydantic import BaseModel

from app.services.cv_service import CVDocument


class CVResponse(BaseModel):
    filename: str
    page_count: int
    char_count: int
    word_count: int
    skills: list[str]
    text: str

    @classmethod
    def from_document(cls, cv: CVDocument, skills: list[str]) -> "CVResponse":
        return cls(
            filename=cv.filename,
            page_count=cv.page_count,
            char_count=cv.char_count,
            word_count=cv.word_count,
            skills=skills,
            text=cv.text,
        )
