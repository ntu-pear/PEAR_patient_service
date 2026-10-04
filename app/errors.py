"""Standard error responses for Patient Service.

Every error leaves the API as {"detail": str, "code": str, "status": int}, plus
"errors" for request validation failures. See
docs/specs/2026-10-04-api-error-format-design.md.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

GENERIC_SERVER_ERROR = "An unexpected error occurred"
VALIDATION_FAILED = "Request validation failed"

STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


class AppError(HTTPException):
    """HTTPException with an optional machine-readable code.

    Subclasses FastAPI's HTTPException so existing `except HTTPException: raise`
    pass-throughs keep working.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


class BadRequestError(AppError):
    def __init__(self, detail: str, code: Optional[str] = None):
        super().__init__(400, detail, code)


class ForbiddenError(AppError):
    def __init__(self, detail: str, code: Optional[str] = None):
        super().__init__(403, detail, code)


class NotFoundError(AppError):
    def __init__(self, detail: str, code: Optional[str] = None):
        super().__init__(404, detail, code)


class ConflictError(AppError):
    def __init__(self, detail: str, code: Optional[str] = None):
        super().__init__(409, detail, code)


class ServiceUnavailableError(AppError):
    def __init__(self, detail: str, code: Optional[str] = None):
        super().__init__(503, detail, code)


def error_body(
    status: int,
    detail: str,
    code: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "detail": detail,
        "code": code or STATUS_CODES.get(status, "ERROR"),
        "status": status,
    }
    if errors is not None:
        body["errors"] = errors
    return body


def _where(request: Request) -> str:
    return f"{request.method} {request.url.path}"


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    status = exc.status_code
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    if status >= 500 and status != 503:
        logger.error("HTTP %s at %s: %s", status, _where(request), detail)
        detail = GENERIC_SERVER_ERROR
    return JSONResponse(
        status_code=status,
        content=error_body(status, detail, getattr(exc, "code", None)),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Field paths and messages only: exc.errors() also carries the submitted
    # values ("input"), which can contain patient data such as NRIC.
    errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())),
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]
    logger.warning("Validation failed at %s: %s", _where(request), errors)
    return JSONResponse(status_code=422, content=error_body(422, VALIDATION_FAILED, errors=errors))


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error("Database error at %s", _where(request), exc_info=exc)
    return JSONResponse(status_code=500, content=error_body(500, GENERIC_SERVER_ERROR))


async def unhandled_exception_middleware(request: Request, call_next):
    # A middleware rather than @app.exception_handler(Exception): Starlette runs
    # Exception handlers outside CORSMiddleware, so those 500s would lose their
    # CORS headers and the browser would hide the response from the WebFE.
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error("Unhandled error at %s", _where(request), exc_info=exc)
        return JSONResponse(status_code=500, content=error_body(500, GENERIC_SERVER_ERROR))


def register_error_handlers(app: FastAPI) -> None:
    """Install the standard error handlers.

    Call before app.add_middleware(CORSMiddleware, ...) so CORS wraps the
    catch-all middleware.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.middleware("http")(unhandled_exception_middleware)
