from fastapi import APIRouter, Response, status

from flowguard.api.dependencies import ReadinessCheck, ServicesDep

router = APIRouter()


# Liveness: the process is up. It doesn't check Ollama, Qdrant, or the audit store.
@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def passes(check: ReadinessCheck) -> bool:
    # A check that can't run is a failing check. Its error stays in the server,
    # because a health endpoint is often public.
    try:
        return check()
    except Exception:  # noqa: BLE001
        return False


# Readiness: every dependency can serve. Orchestrators route traffic only when it's 200.
@router.get("/health/ready")
def ready(services: ServicesDep, response: Response) -> dict[str, object]:
    results = {name: passes(check) for name, check in services.checks.items()}
    is_ready = all(results.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if is_ready else "not ready",
        "checks": {name: "ok" if ok else "failing" for name, ok in results.items()},
    }
