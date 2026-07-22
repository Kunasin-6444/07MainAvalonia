from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    """Quick liveness check — does not touch the database."""
    return {"status": "ok"}
