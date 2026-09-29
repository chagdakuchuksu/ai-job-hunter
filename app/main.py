import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import analysis, cv, health, job, skills
from app.config import get_settings
from app.errors import register_error_handlers

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)  # quiet model-download request logs

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(
    title="AI Job Hunter",
    description=(
        "Compare a CV with a job description. "
        "A decision-support tool, not an automated hiring system."
    ),
    version="1.0.0",
)

# The frontend is served by this same app, so CORS is only needed if you open
# the HTML from another local origin (e.g. a separate static server).
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(health.router)
app.include_router(cv.router)
app.include_router(job.router)
app.include_router(skills.router)
app.include_router(analysis.router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
