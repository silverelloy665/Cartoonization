from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
