from fastapi import APIRouter

router = APIRouter()


# Says only that the API is running. It doesn't check Ollama or the audit store.
@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
