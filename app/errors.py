"""Application errors and the handlers that turn them into clean JSON responses.

Services raise `AppError` with a user-safe message. Anything unexpected is
logged on the server and returned as a generic 500, so internal exception
details never reach the client.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """An error whose message is safe to show to the user."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def _validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Keep the location and message but drop the echoed input, which could be
    # a whole job description or CV.
    errors = [
        {"loc": [str(part) for part in err.get("loc", [])], "msg": err.get("msg", "")}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422, content={"detail": "Invalid request.", "errors": errors}
    )


async def _unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
