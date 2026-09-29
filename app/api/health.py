from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple liveness check: returns 200 if the server is running."""
    return {"status": "ok"}
