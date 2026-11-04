from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from flowguard.api.dependencies import Services, load_services
from flowguard.api.routes import health, investigations
from flowguard.graph.nodes.intake import describe


async def invalid_request(request: Request, error: Exception) -> JSONResponse:
    # FastAPI's own answer repeats the rejected input, which could hold a secret.
    problems = error.errors() if isinstance(error, RequestValidationError) else []
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": [describe(problem) for problem in problems]},
    )


def create_app(load: Callable[[], Services] = load_services) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        # Loading the embedder and indexing documents takes seconds, so it happens
        # once, when the API starts, not on every request.
        application.state.services = load()
        yield

    app = FastAPI(title="FlowGuard", lifespan=lifespan)
    app.add_exception_handler(RequestValidationError, invalid_request)
    app.include_router(health.router)
    app.include_router(investigations.router)
    return app


app = create_app()
