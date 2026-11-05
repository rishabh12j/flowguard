import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from flowguard.api.dependencies import Services, open_services
from flowguard.api.routes import health, investigations
from flowguard.graph.nodes.intake import describe


async def invalid_request(request: Request, error: Exception) -> JSONResponse:
    # FastAPI's own answer repeats the rejected input, which could hold a secret.
    problems = error.errors() if isinstance(error, RequestValidationError) else []
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": [describe(problem) for problem in problems]},
    )


logger = logging.getLogger("flowguard.api")


async def unexpected_error(request: Request, error: Exception) -> JSONResponse:
    # The caller gets an ID to quote. The details, which may name files, hosts,
    # or data, go only to the server's log under the same ID.
    error_id = uuid4().hex[:12]
    logger.error(
        "unexpected error %s on %s %s",
        error_id,
        request.method,
        request.url.path,
        exc_info=error,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "internal error", "error_id": error_id},
    )


def create_app(
    services_from: Callable[[], AbstractAsyncContextManager[Services]] = open_services,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        # Loading the embedder and indexing documents takes seconds, so it happens
        # once, when the API starts. The checkpoint file closes when it stops.
        async with services_from() as services:
            application.state.services = services
            yield

    app = FastAPI(title="FlowGuard", lifespan=lifespan)
    app.add_exception_handler(RequestValidationError, invalid_request)
    # Every error is JSON with a "detail", including a crash.
    app.add_exception_handler(Exception, unexpected_error)
    app.include_router(health.router)
    app.include_router(investigations.router)
    return app


app = create_app()
