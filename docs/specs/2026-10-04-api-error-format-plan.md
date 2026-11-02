# Standardised API Error Responses — Implementation Plan

**Goal:** Every Patient Service error response has one shape (`detail`/`code`/`status`), correct status codes, and no leaked exception text or submitted data.

**Architecture:** A new `app/errors.py` holds `AppError` subclasses and `register_error_handlers(app)`, which installs FastAPI exception handlers plus a catch-all middleware. `main.py` calls it before adding CORS. Existing `raise HTTPException(...)` sites are normalised by the handler; only the 38 leak sites, 4 swallow sites and 40 conflict sites are edited. An AST guard test keeps those conventions from regressing.

**Tech Stack:** Python 3.9 (CI), FastAPI, Starlette, SQLAlchemy, pytest, `fastapi.testclient`.

**Spec:** `docs/specs/2026-10-04-api-error-format-design.md`

## Global Constraints

- Branch: `feature/standardize-error-responses` (from `origin/staging` @ `b7a62ec`). One branch for this task only.
- Python 3.9 syntax only (`Optional[...]`, `Dict[...]`; no `X | None`).
- Do not touch `app/messaging/` or `app/crud/ref_user_crud.py`.
- Keep empty-collection `404` behaviour (WebFE screens depend on it).
- `detail` must always be a string; `5xx` other than `503` returns `"An unexpected error occurred"`.
- Error-message text at conflict sites stays exactly as it is; only the status changes.
- Unit tests need env vars. Use this prefix for every pytest command:
  `SERVICE_NAME=PATIENT DB_DRIVER=x DB_SERVER=localhost DB_DATABASE=test DB_DATABASE_PORT=1433 DB_USERNAME=u DB_PASSWORD=p RABBITMQ_HOST=localhost RABBITMQ_PORT=5672 RABBITMQ_USER=g RABBITMQ_PASS=g RABBITMQ_VIRTUAL_HOST=/`
  (written below as `$ENV`). Baseline with this env: `python -m pytest tests/unit` → **461 passed**.

## Review Focus

1. **CORS on unhandled 500s.** Once leak sites re-raise, CRUD failures become unhandled exceptions. Starlette runs `@app.exception_handler(Exception)` outside `CORSMiddleware`, so the browser would see a CORS failure instead of a `500` (verified: header present via middleware, absent via exception handler). Pinned by `test_unhandled_500_keeps_cors_headers` (Task 1) and `test_unhandled_error_in_real_app_keeps_cors_headers` (Task 2).
2. **Patient data in validation logs/responses.** FastAPI's `exc.errors()` includes submitted values (`input`), e.g. NRIC; today `main.py:231` logs them and `main.py:235` returns `exc.body`. Pinned by `test_validation_error_is_422_with_fields_and_no_input_echo` (Task 1).
3. **Rollback before re-raise.** Leak fixes must keep `db.rollback()` before the bare `raise`, otherwise a failed save could leave an outbox row behind. Pinned by the explicit per-site rule in Task 3 Step 3 and the unchanged outbox integration tests (`tests/integration/test_patient_outbox_integration.py`, run in CI).
4. **Real 404/409 surviving catch-alls.** Sites such as `get_all_dementia_stage_list_entries` currently turn their own `404` into `500`. Pinned by `test_catch_all_handlers_do_not_swallow_http_errors` (Task 3) and `test_empty_dementia_stage_list_returns_404` (Task 3).
5. **Intentional user messages not masked.** Vital range-check `ValueError`s ("Temperature must be between …") must still reach the user as `400`. Pinned by `test_vital_range_error_is_bad_request` (Task 3).

---

### Task 1: `app/errors.py` — error types and handlers

**Files:**
- Create: `app/errors.py`
- Test: `tests/unit/test_errors.py`

**Interfaces:**
- Produces: `AppError(status_code: int, detail: str, code: Optional[str] = None, headers: Optional[Dict[str, str]] = None)` (subclass of `fastapi.HTTPException`); `BadRequestError(detail, code=None)` 400; `ForbiddenError` 403; `NotFoundError` 404; `ConflictError` 409; `ServiceUnavailableError` 503; `register_error_handlers(app: FastAPI) -> None`; constants `GENERIC_SERVER_ERROR = "An unexpected error occurred"`, `VALIDATION_FAILED = "Request validation failed"`, `STATUS_CODES: Dict[int, str]`; `error_body(status, detail, code=None, errors=None) -> Dict[str, Any]`.

- [ ] **Step 1: Write the failing test** — create `tests/unit/test_errors.py`:

```python
import logging

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError

from app.errors import (
    GENERIC_SERVER_ERROR,
    AppError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ServiceUnavailableError,
    register_error_handlers,
)

ORIGIN = "http://frontend.test"


class Item(BaseModel):
    name: str
    nric: str


@pytest.fixture
def client():
    app = FastAPI()
    register_error_handlers(app)
    app.add_middleware(
        CORSMiddleware, allow_origins=[ORIGIN], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )

    @app.get("/http/{status}")
    def plain_http(status: int):
        raise HTTPException(status_code=status, detail=f"plain {status}")

    @app.get("/app-error/{kind}")
    def app_error(kind: str):
        errors = {
            "bad": BadRequestError("bad input"),
            "forbidden": ForbiddenError("not allowed"),
            "missing": NotFoundError("no such thing"),
            "conflict": ConflictError("already exists"),
            "unavailable": ServiceUnavailableError("try later"),
            "custom": ConflictError("dupe", code="DUPLICATE_RECORD"),
        }
        raise errors[kind]

    @app.get("/server-detail")
    def server_detail():
        raise HTTPException(status_code=500, detail="secret: connection string")

    @app.get("/unhandled")
    def unhandled():
        raise RuntimeError("secret: stack internals")

    @app.get("/database")
    def database():
        raise OperationalError("SELECT secret", {"nric": "S1234567A"}, Exception("db down"))

    @app.get("/auth")
    def auth():
        raise HTTPException(status_code=401, detail="bad token", headers={"WWW-Authenticate": "Bearer"})

    @app.get("/non-string")
    def non_string():
        raise HTTPException(status_code=400, detail={"field": "x"})

    @app.post("/items")
    def create_item(item: Item):
        return item

    return TestClient(app, raise_server_exceptions=False)


def test_plain_http_exception_gets_standard_shape(client):
    response = client.get("/http/404")
    assert response.status_code == 404
    assert response.json() == {"detail": "plain 404", "code": "NOT_FOUND", "status": 404}


@pytest.mark.parametrize(
    "kind,status,code",
    [
        ("bad", 400, "BAD_REQUEST"),
        ("forbidden", 403, "FORBIDDEN"),
        ("missing", 404, "NOT_FOUND"),
        ("conflict", 409, "CONFLICT"),
        ("unavailable", 503, "SERVICE_UNAVAILABLE"),
        ("custom", 409, "DUPLICATE_RECORD"),
    ],
)
def test_app_errors_map_to_status_and_code(client, kind, status, code):
    response = client.get(f"/app-error/{kind}")
    assert response.status_code == status
    assert response.json()["code"] == code
    assert response.json()["status"] == status


def test_app_error_is_an_http_exception():
    assert issubclass(AppError, HTTPException)


def test_unknown_status_falls_back_to_error_code(client):
    assert client.get("/http/418").json()["code"] == "ERROR"


def test_explicit_500_detail_is_masked_and_logged(client, caplog):
    with caplog.at_level(logging.ERROR, logger="app.errors"):
        response = client.get("/server-detail")
    assert response.status_code == 500
    assert response.json() == {"detail": GENERIC_SERVER_ERROR, "code": "INTERNAL_ERROR", "status": 500}
    assert "secret: connection string" in caplog.text


def test_unhandled_exception_is_masked_and_logged(client, caplog):
    with caplog.at_level(logging.ERROR, logger="app.errors"):
        response = client.get("/unhandled")
    assert response.status_code == 500
    assert response.json() == {"detail": GENERIC_SERVER_ERROR, "code": "INTERNAL_ERROR", "status": 500}
    assert "secret" not in response.text
    assert "secret: stack internals" in caplog.text


def test_unhandled_500_keeps_cors_headers(client):
    response = client.get("/unhandled", headers={"Origin": ORIGIN})
    assert response.status_code == 500
    assert response.headers.get("access-control-allow-origin") == ORIGIN


def test_database_error_is_masked(client):
    response = client.get("/database")
    assert response.status_code == 500
    assert response.json()["detail"] == GENERIC_SERVER_ERROR
    assert "S1234567A" not in response.text


def test_validation_error_is_422_with_fields_and_no_input_echo(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        response = client.post("/items", json={"nric": "S1234567A"})
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Request validation failed"
    assert body["code"] == "VALIDATION_ERROR"
    assert body["errors"] == [{"field": "body.name", "message": "Field required"}]
    assert "S1234567A" not in response.text
    assert "S1234567A" not in caplog.text


def test_headers_are_preserved(client):
    response = client.get("/auth")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["code"] == "UNAUTHORIZED"


def test_unknown_route_and_wrong_method(client):
    missing = client.get("/no-such-route")
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"
    wrong_method = client.delete("/items")
    assert wrong_method.status_code == 405
    assert wrong_method.json()["code"] == "METHOD_NOT_ALLOWED"


def test_non_string_detail_is_coerced(client):
    assert client.get("/non-string").json()["detail"] == "{'field': 'x'}"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `$ENV python -m pytest tests/unit/test_errors.py -q`
Expected: collection error `ModuleNotFoundError: No module named 'app.errors'`.

- [ ] **Step 3: Implement** — create `app/errors.py`:

```python
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
```

- [ ] **Step 4: Run it to verify it passes**

Run: `$ENV python -m pytest tests/unit/test_errors.py -q`
Expected: `17 passed`.

- [ ] **Step 5: Commit**

```bash
git add app/errors.py tests/unit/test_errors.py
git commit -m "Add standard error types and handlers"
```

### Task 2: Wire the handlers into `main.py`

**Files:**
- Modify: `app/main.py:8-12` (imports), `app/main.py:200-247` (app setup and the two old handlers)
- Test: `tests/unit/test_main_error_wiring.py`

**Interfaces:**
- Consumes: `register_error_handlers(app)` from Task 1.

- [ ] **Step 1: Write the failing test** — create `tests/unit/test_main_error_wiring.py`:

```python
"""Checks main.py installs the standard error handlers in the right order.

Importing app.main is safe here: TestClient is not used as a context manager,
so the lifespan (outbox processor, consumers) never starts.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

ORIGIN = "http://localhost:5173"  # in main.py's allowed origins


@pytest.fixture(scope="module")
def client():
    def boom():
        raise RuntimeError("wiring test failure")

    app.add_api_route("/__error-wiring-test", boom, methods=["GET"])
    yield TestClient(app, raise_server_exceptions=False)
    app.router.routes[:] = [
        r for r in app.router.routes if getattr(r, "path", None) != "/__error-wiring-test"
    ]


def test_unknown_route_uses_standard_shape(client):
    response = client.get("/__no-such-route")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found", "code": "NOT_FOUND", "status": 404}


def test_validation_errors_are_422(client):
    response = client.post("/api/v1/patients/add", json={})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "body" not in response.json()


def test_unhandled_error_in_real_app_keeps_cors_headers(client):
    response = client.get("/__error-wiring-test", headers={"Origin": ORIGIN})
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert response.headers.get("access-control-allow-origin") == ORIGIN
```

- [ ] **Step 2: Run it to verify it fails**

Run: `$ENV python -m pytest tests/unit/test_main_error_wiring.py -q`
Expected: 3 failed — e.g. `assert {'detail': 'Not Found'} == {...}`, validation returns `400`, and the unhandled route has no CORS header.

- [ ] **Step 3: Implement** — in `app/main.py`:

1. Delete the two old handlers: lines 229-247, from `@app.exception_handler(RequestValidationError)` through the closing `)` of the `SQLAlchemyError` handler's `return JSONResponse(...)`, including the `# Exception handler for database errors` comment.
2. Directly after the `app = FastAPI(...)` call (ends line 207) and **before** `origins = [` / `app.add_middleware(CORSMiddleware, ...)`, add:

```python
# Must run before CORSMiddleware is added so CORS wraps the catch-all
# middleware (see app/errors.py).
register_error_handlers(app)
```

3. Add the import next to the other `app.` imports:

```python
from app.errors import register_error_handlers
```

4. Remove the imports used only by the deleted handlers: line 9 `from fastapi.exceptions import RequestValidationError`, line 11 `from fastapi.responses import JSONResponse`, line 12 `from sqlalchemy.exc import SQLAlchemyError`, and change line 8 to `from fastapi import FastAPI`. Confirm with `grep -n "JSONResponse\|Request\b\|SQLAlchemyError" app/main.py` → no output.

- [ ] **Step 4: Run the new test and the full suite**

Run: `$ENV python -m pytest tests/unit/test_main_error_wiring.py -q` → `3 passed`
Run: `$ENV python -m pytest tests/unit -q` → `481 passed` (461 + 17 + 3).

- [ ] **Step 5: Commit**

```bash
git add app/main.py tests/unit/test_main_error_wiring.py
git commit -m "Use standard error handlers in main app; validation errors return 422"
```

### Task 3: Remove exception text from responses and stop swallowing HTTP errors (spec §8.B, §8.C)

**Files:**
- Modify: the 27 CRUD sites listed in Step 3a; `app/crud/patient_vital_crud.py:138,141,239,245`; `app/routers/integrity_router.py:63,116,166,215,264,290`; `app/routers/patient_assigned_dementia_list_router.py:41-46`
- Test: create `tests/unit/test_error_conventions.py`; add two behaviour tests to `tests/unit/test_patient_dementia_stage_list.py` and `tests/unit/test_patient_vital.py`

**Interfaces:**
- Consumes: `BadRequestError` from Task 1.

- [ ] **Step 1: Write the failing guard tests** — create `tests/unit/test_error_conventions.py`:

```python
"""Guards the error conventions in docs/specs/2026-10-04-api-error-format-design.md.

Parses app/ instead of importing it, so it needs no database or environment.
"""
import ast
import pathlib

APP = pathlib.Path(__file__).resolve().parents[2] / "app"
SKIP_DIRS = {"messaging"}
CAUGHT_NAMES = {"e", "ex", "exc", "error", "err"}
ERROR_CALLS = {
    "HTTPException", "AppError", "BadRequestError", "NotFoundError",
    "ConflictError", "ForbiddenError", "ServiceUnavailableError",
}
NON_DETAIL_KEYWORDS = {"status_code", "code", "headers"}
# Our own ValueError range checks ("Temperature must be between ...") are
# deliberately shown to the user as BadRequestError(str(e)) (spec section 5.B).
# Only BadRequestError raises in these functions are exempt.
LEAK_ALLOWLIST = {
    ("crud/patient_vital_crud.py", "create_vital"),
    ("crud/patient_vital_crud.py", "update_vital"),
}


def _sources():
    for path in sorted(APP.rglob("*.py")):
        rel = path.relative_to(APP).as_posix()
        if rel.split("/")[0] in SKIP_DIRS:
            continue
        yield rel, ast.parse(path.read_text(encoding="utf-8"))


def _call_name(call):
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _error_raises(tree):
    """Yield (enclosing function name, raise node, call) once per raised error call."""
    seen = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if (
                isinstance(node, ast.Raise)
                and isinstance(node.exc, ast.Call)
                and _call_name(node.exc) in ERROR_CALLS
                and node.lineno not in seen
            ):
                seen.add(node.lineno)
                yield fn.name, node, node.exc


def _detail_parts(call):
    parts = [kw.value for kw in call.keywords if kw.arg not in NON_DETAIL_KEYWORDS]
    args = list(call.args)
    if _call_name(call) in {"HTTPException", "AppError"}:
        args = args[1:]  # first positional is the status code
    return parts + args


def test_error_detail_never_contains_caught_exception_text():
    offenders = []
    for rel, tree in _sources():
        for fn_name, node, call in _error_raises(tree):
            if (rel, fn_name) in LEAK_ALLOWLIST and _call_name(call) == "BadRequestError":
                continue
            names = {
                n.id for part in _detail_parts(call)
                for n in ast.walk(part) if isinstance(n, ast.Name)
            }
            if names & CAUGHT_NAMES:
                offenders.append(f"{rel}:{node.lineno}")
    assert offenders == [], "Exception text in error detail:\n" + "\n".join(offenders)


def test_catch_all_handlers_do_not_swallow_http_errors():
    offenders = []
    for rel, tree in _sources():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            body_raises_http = any(
                isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call)
                and _call_name(x.exc) in ERROR_CALLS
                for stmt in node.body for x in ast.walk(stmt)
            )
            router_calls_crud = rel.startswith("routers/") and any(
                isinstance(x, ast.Call) and "crud" in ast.unparse(x.func).lower()
                for stmt in node.body for x in ast.walk(stmt)
            )
            if not (body_raises_http or router_calls_crud):
                continue
            for handler in node.handlers:
                caught = ast.unparse(handler.type) if handler.type else "BaseException"
                if "HTTPException" in caught:
                    break  # HTTP errors are passed through before any catch-all
                if caught in {"Exception", "BaseException"}:
                    if any(isinstance(x, ast.Raise) and x.exc is not None for x in ast.walk(handler)):
                        offenders.append(f"{rel}:{node.lineno}")
                    break
    assert offenders == [], "Catch-all converts HTTP errors:\n" + "\n".join(offenders)
```

Add to the end of `tests/unit/test_patient_dementia_stage_list.py` (uses the file's existing `db_session_mock` fixture):

```python
def test_empty_dementia_stage_list_returns_404(db_session_mock):
    from fastapi import HTTPException
    from app.crud.patient_dementia_stage_list_crud import get_all_dementia_stage_list_entries

    db_session_mock.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        get_all_dementia_stage_list_entries(db_session_mock)
    assert exc_info.value.status_code == 404
```

Add to the end of `tests/unit/test_patient_vital.py` (uses the file's existing `db_session_mock` and `vital_create` fixtures; validation runs before any DB call):

```python
def test_vital_range_error_is_bad_request(db_session_mock, vital_create):
    from fastapi import HTTPException

    from app.errors import BadRequestError

    out_of_range = vital_create.model_copy(update={"Temperature": 99.0})
    with pytest.raises(HTTPException) as exc_info:
        create_vital(db_session_mock, out_of_range, created_by="test_user", user_full_name="Test User")
    assert exc_info.value.status_code == 400
    assert "Temperature must be between" in exc_info.value.detail
    assert isinstance(exc_info.value, BadRequestError)
```

- [ ] **Step 2: Run to verify they fail**

Run: `$ENV python -m pytest tests/unit/test_error_conventions.py tests/unit/test_patient_dementia_stage_list.py::test_empty_dementia_stage_list_returns_404 tests/unit/test_patient_vital.py::test_vital_range_error_is_bad_request -q`
Expected: leak test lists **38** offenders; swallow test lists **4** (`crud/patient_crud.py:557`, `crud/patient_dementia_stage_list_crud.py:12`, `crud/patient_mobility_list_crud.py:20`, `routers/patient_assigned_dementia_list_router.py:41`); empty-list test gets `500` not `404`; vital test fails `isinstance(..., BadRequestError)`.

- [ ] **Step 3: Implement**

**3a. 27 CRUD sites — replace the `raise HTTPException(...)` line with a bare `raise`.** Leave everything above it in the `except` block (`db.rollback()`, `logger.error(...)`) unchanged; if the `except` block has a `db.rollback()`, it must stay above the `raise`. If `e` becomes unused, change `except Exception as e:` to `except Exception:` only when no other line in the block uses `e`.

- `app/crud/patient_crud.py:34` — `raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")`
- `app/crud/patient_crud.py:543` — `raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")`
- `app/crud/patient_crud.py:687` — `raise HTTPException(status_code=500, detail=f"Failed to update patient: {str(e)}")`
- `app/crud/patient_crud.py:813` — `raise HTTPException(status_code=500, detail=f"Failed to delete patient: {str(e)}")`
- `app/crud/patient_dementia_stage_list_crud.py:20` — `raise HTTPException(status_code=500, detail=f"Error querying dementia stage list: {str(e)}")`
- `app/crud/patient_highlight_crud.py:357` — `raise HTTPException(`
- `app/crud/patient_medication_crud.py:362` — `raise HTTPException(status_code=500, detail=f"Failed to create medication: {str(e)}")`
- `app/crud/patient_medication_crud.py:579` — `raise HTTPException(status_code=500, detail=f"Failed to update medication: {str(e)}")`
- `app/crud/patient_medication_crud.py:740` — `raise HTTPException(status_code=500, detail=f"Failed to delete medication: {str(e)}")`
- `app/crud/patient_mobility_list_crud.py:26` — `raise HTTPException(status_code=500, detail=f"Error querying mobility list: {str(e)}")`
- `app/crud/patient_mobility_mapping_crud.py:137` — `raise HTTPException(status_code=500, detail=f"Failed to create mobility entry: {str(e)}")`
- `app/crud/patient_personal_preference_crud.py:256` — `raise HTTPException(`
- `app/crud/patient_personal_preference_crud.py:398` — `raise HTTPException(`
- `app/crud/patient_personal_preference_crud.py:477` — `raise HTTPException(`
- `app/crud/patient_personal_preference_list_crud.py:141` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_personal_preference_list_crud.py:238` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_personal_preference_list_crud.py:292` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_prescription_crud.py:159` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_prescription_crud.py:275` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_prescription_crud.py:392` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_prescription_list_crud.py:89` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_problem_crud.py:185` — `raise HTTPException(status_code=500, detail=f"Failed to create problem: {str(e)}")`
- `app/crud/patient_problem_crud.py:320` — `raise HTTPException(status_code=500, detail=f"Failed to update problem: {str(e)}")`
- `app/crud/patient_problem_crud.py:403` — `raise HTTPException(status_code=500, detail=f"Failed to delete problem: {str(e)}")`
- `app/crud/patient_problem_list_crud.py:92` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_problem_list_crud.py:166` — `raise HTTPException(status_code=500, detail=str(e))`
- `app/crud/patient_problem_list_crud.py:215` — `raise HTTPException(status_code=500, detail=str(e))`

**3b. `app/crud/patient_vital_crud.py`** — add `from ..errors import BadRequestError` to the imports, then:

- lines 138 and 239: `raise HTTPException(status_code=400, detail=str(e))` → `raise BadRequestError(str(e))`
- lines 141 and 245: `raise HTTPException(status_code=500, detail=str(e))` → `raise` (the `db.rollback()` above each stays)

The `update_vital` block keeps its existing `except HTTPException: raise` between the two handlers.

**3c. `app/routers/integrity_router.py`** — add after the imports:

```python
import logging

logger = logging.getLogger(__name__)
```

and replace each of the six `except` blocks as follows (message text per site):

| Line | New block |
|---|---|
| 63 | `except Exception:` / `logger.exception("Patient integrity check failed")` / `raise HTTPException(status_code=500, detail="Patient integrity check failed")` |
| 116 | same pattern, message `"Patient medication integrity check failed"` |
| 166 | same pattern, message `"Patient allocation integrity check failed"` |
| 215 | same pattern, message `"Ref userconfig integrity check failed"` |
| 264 | same pattern, message `"Integrity summary failed"` |
| 290 | same pattern, status `503`, message `"Integrity health check failed"` |

Example for line 63:

```python
    except Exception:
        logger.exception("Patient integrity check failed")
        raise HTTPException(status_code=500, detail="Patient integrity check failed")
```

**3d. `app/routers/patient_assigned_dementia_list_router.py:41-46`** — remove the `try`/`except` and the `print`, so the body is:

```python
    return crud_dementia_list.create_dementia_list_entry(db, dementia_list_data, user_id, user_full_name)
```

(CRUD `HTTPException`s now pass through; anything else becomes a generic `500` via the middleware.)

The 4 swallow sites are fixed by 3a/3d: `patient_crud.py:557` (its handler at line 684 is in the 3a list), `patient_dementia_stage_list_crud.py:12` (line 20), `patient_mobility_list_crud.py:20` (line 26), and the router in 3d.

- [ ] **Step 4: Run to verify they pass, then the full suite**

Run: `$ENV python -m pytest tests/unit/test_error_conventions.py tests/unit/test_patient_dementia_stage_list.py tests/unit/test_patient_vital.py -q` → all pass.
Run: `$ENV python -m pytest tests/unit -q` → `485 passed` (481 + 2 guard + 2 behaviour). No existing test should change in this task (verified: no test expects `HTTPException` from a DB failure at a leak site). If one fails, stop and investigate rather than editing it.

- [ ] **Step 5: Commit**

```bash
git add app/crud app/routers tests/unit
git commit -m "Stop returning exception text in error responses; pass HTTP errors through catch-alls"
```

### Task 4: Duplicates and uniqueness conflicts return 409 (spec §8.D)

**Files:**
- Modify: the 40 sites in Step 3 (18 CRUD files, 2 routers)
- Modify tests: the 29 tests listed in Step 3
- Test: add `test_conflicts_are_not_reported_as_400` to `tests/unit/test_error_conventions.py`

**Interfaces:**
- Consumes: `ConflictError` from Task 1.

- [ ] **Step 1: Write the failing guard test** — add to `tests/unit/test_error_conventions.py`:

```python
CONFLICT_PHRASES = (
    "already exist", "duplicate", "conflicts with", "must be unique",
    "already has this", "already has an ", "already has a ",
    "already assigned", "already been", "record exists",
)


def _status(call):
    name = _call_name(call)
    if name == "BadRequestError":
        return 400
    node = next((kw.value for kw in call.keywords if kw.arg == "status_code"), None)
    if node is None and name in {"HTTPException", "AppError"} and call.args:
        node = call.args[0]
    text = ast.unparse(node) if node is not None else ""
    return 400 if text in {"400", "status.HTTP_400_BAD_REQUEST"} else None


def test_conflicts_are_not_reported_as_400():
    offenders = []
    for rel, tree in _sources():
        for _, node, call in _error_raises(tree):
            if _status(call) != 400:
                continue
            text = " ".join(ast.unparse(p) for p in _detail_parts(call)).lower()
            if any(phrase in text for phrase in CONFLICT_PHRASES):
                offenders.append(f"{rel}:{node.lineno}")
    assert offenders == [], "Use ConflictError (409) for:\n" + "\n".join(offenders)
```

(Capacity rules — "already has the maximum of …", "must have at least …" — intentionally stay `400` and do not match these phrases.)

- [ ] **Step 2: Run to verify it fails**

Run: `$ENV python -m pytest tests/unit/test_error_conventions.py::test_conflicts_are_not_reported_as_400 -q`
Expected: FAIL listing **40** offenders.

- [ ] **Step 3: Implement**

In each file below, add `from ..errors import ConflictError` to the imports, then replace each listed raise. Keep the message text and indentation exactly; multi-line raises collapse to the single call shown.

**`app/crud/patient_allergy_mapping_crud.py`**

- line 178: `raise HTTPException( status_code=400, detail="Patient already has this allergy and reaction combination", )` → `raise ConflictError("Patient already has this allergy and reaction combination")`
- line 304: `raise HTTPException(status_code=400, detail="Patient allergy record exists for the specified allergy type and reaction")` → `raise ConflictError("Patient allergy record exists for the specified allergy type and reaction")`

**`app/crud/patient_assigned_dementia_mapping_crud.py`**

- line 179: `raise HTTPException( status_code=400, detail="Patient already assigned this dementia type" )` → `raise ConflictError("Patient already assigned this dementia type")`

**`app/crud/patient_crud.py`**

- line 298: `raise HTTPException(status_code=400, detail="NRIC must be unique for active records")` → `raise ConflictError("NRIC must be unique for active records")`
- line 312: `raise HTTPException( status_code=400, detail="Patient NRIC conflicts with an existing active guardian record" )` → `raise ConflictError("Patient NRIC conflicts with an existing active guardian record")`
- line 577: `raise HTTPException(status_code=400, detail="NRIC must be unique for active records")` → `raise ConflictError("NRIC must be unique for active records")`
- line 591: `raise HTTPException( status_code=400, detail="Patient NRIC conflicts with an existing active guardian record" )` → `raise ConflictError("Patient NRIC conflicts with an existing active guardian record")`

**`app/crud/patient_dementia_stage_list_crud.py`**

- line 51: `raise HTTPException( status_code=400, detail=f"Dementia stage '{uppercase_stage}' already exists." )` → `raise ConflictError(f"Dementia stage '{uppercase_stage}' already exists.")`
- line 116: `raise HTTPException( status_code=400, detail=f"Dementia stage '{uppercase_stage}' already exists." )` → `raise ConflictError(f"Dementia stage '{uppercase_stage}' already exists.")`

**`app/crud/patient_guardian_crud.py`**

- line 47: `raise HTTPException( status_code=400, detail="Guardian NRIC conflicts with an existing active patient record" )` → `raise ConflictError("Guardian NRIC conflicts with an existing active patient record")`
- line 59: `raise HTTPException( status_code=400, detail="A guardian with this NRIC already exists" )` → `raise ConflictError("A guardian with this NRIC already exists")`
- line 105: `raise HTTPException( status_code=400, detail="Guardian NRIC conflicts with an existing active patient record" )` → `raise ConflictError("Guardian NRIC conflicts with an existing active patient record")`
- line 122: `raise HTTPException( status_code=400, detail="A guardian with this NRIC already exists" )` → `raise ConflictError("A guardian with this NRIC already exists")`

**`app/crud/patient_highlight_type_crud.py`**

- line 99: `raise HTTPException( status_code=400, detail=f"Highlight type with code '{uppercase_type_code}' already exists" )` → `raise ConflictError(f"Highlight type with code '{uppercase_type_code}' already exists")`
- line 164: `raise HTTPException( status_code=400, detail=f"Highlight type with code '{update_data['TypeCode']}' already exists" )` → `raise ConflictError(f"Highlight type with code '{update_data['TypeCode']}' already exists")`

**`app/crud/patient_list_language_crud.py`**

- line 33: `raise HTTPException(status_code=400, detail="Language value already exists")` → `raise ConflictError("Language value already exists")`
- line 78: `raise HTTPException(status_code=400, detail="Language value already exists")` → `raise ConflictError("Language value already exists")`

**`app/crud/patient_medical_diagnosis_list_crud.py`**

- line 49: `raise HTTPException( status_code=400, detail="A medical diagnosis with this name already exists" )` → `raise ConflictError("A medical diagnosis with this name already exists")`
- line 118: `raise HTTPException( status_code=400, detail="A medical diagnosis with this name already exists" )` → `raise ConflictError("A medical diagnosis with this name already exists")`

**`app/crud/patient_medical_history_crud.py`**

- line 55: `raise HTTPException( status_code=400, detail="This patient already has a medical history record for this diagnosis" )` → `raise ConflictError("This patient already has a medical history record for this diagnosis")`
- line 131: `raise HTTPException( status_code=400, detail="This patient already has a medical history record for this diagnosis" )` → `raise ConflictError("This patient already has a medical history record for this diagnosis")`

**`app/crud/patient_medication_crud.py`**

- line 236: `raise HTTPException( status_code=400, detail=f"Patient already has an active medication for this prescription" )` → `raise ConflictError(f"Patient already has an active medication for this prescription")`
- line 407: `raise HTTPException( status_code=400, detail=f"Another active medication with this prescription already exists for this patient" )` → `raise ConflictError(f"Another active medication with this prescription already exists for this patient")`

**`app/crud/patient_mobility_mapping_crud.py`**

- line 84: `raise HTTPException(status_code=400, detail="Patient already has an existing mobility aid.")` → `raise ConflictError("Patient already has an existing mobility aid.")`

**`app/crud/patient_personal_preference_crud.py`**

- line 193: `raise HTTPException( status_code=400, detail="Patient already has this personal preference recorded", )` → `raise ConflictError("Patient already has this personal preference recorded")`
- line 327: `raise HTTPException( status_code=400, detail="Another personal preference record with this preference already exists for this patient", )` → `raise ConflictError("Another personal preference record with this preference already exists for this patient")`

**`app/crud/patient_personal_preference_list_crud.py`**

- line 97: `raise HTTPException( status_code=400, detail=f"A preference list entry with type '{preference_list.PreferenceType}' " f"and name '{uppercase_preference_name}' already exists", )` → `raise ConflictError(f"A preference list entry with type '{preference_list.PreferenceType}' " f"and name '{uppercase_preference_name}' already exists")`
- line 191: `raise HTTPException( status_code=400, detail=f"Another preference list entry with type '{new_type}' " f"and name '{new_name}' already exists", )` → `raise ConflictError(f"Another preference list entry with type '{new_type}' " f"and name '{new_name}' already exists")`

**`app/crud/patient_photo_list_album_crud.py`**

- line 41: `raise HTTPException( status_code=400, detail=f"Photo list album with name '{uppercase_value}' already exists" )` → `raise ConflictError(f"Photo list album with name '{uppercase_value}' already exists")`
- line 106: `raise HTTPException( status_code=400, detail=f"Photo list album with name '{uppercase_value}' already exists" )` → `raise ConflictError(f"Photo list album with name '{uppercase_value}' already exists")`

**`app/crud/patient_prescription_crud.py`**

- line 80: `raise HTTPException(status_code=400, detail="Duplicate prescription for the same patient and prescription list.")` → `raise ConflictError("Duplicate prescription for the same patient and prescription list.")`
- line 195: `raise HTTPException( status_code=400, detail="Another prescription with this name already exists for this patient." )` → `raise ConflictError("Another prescription with this name already exists for this patient.")`

**`app/crud/patient_prescription_list_crud.py`**

- line 49: `raise HTTPException( status_code=400, detail="A prescription list record with this name already exists" )` → `raise ConflictError("A prescription list record with this name already exists")`
- line 125: `raise HTTPException( status_code=400, detail="A prescription list record with this name already exists" )` → `raise ConflictError("A prescription list record with this name already exists")`

**`app/crud/patient_problem_crud.py`**

- line 229: `raise HTTPException( status_code=400, detail=f"Another problem record with this condition already exists for this patient" )` → `raise ConflictError(f"Another problem record with this condition already exists for this patient")`
- line 112: `raise HTTPException( status_code=400, detail=f"Patient already has this problem recorded" )` → `raise ConflictError(f"Patient already has this problem recorded")`

**`app/crud/patient_problem_list_crud.py`**

- line 52: `raise HTTPException( status_code=400, detail="A problem list entry with this name already exists" )` → `raise ConflictError("A problem list entry with this name already exists")`
- line 125: `raise HTTPException( status_code=400, detail="A problem list entry with this name already exists" )` → `raise ConflictError("A problem list entry with this name already exists")`

**`app/routers/patient_allocation_router.py`**

- line 83: `raise HTTPException(status_code=400, detail="Patient already has an allocation")` → `raise ConflictError("Patient already has an allocation")`

**`app/routers/patient_guardian_router.py`**

- line 96: `raise HTTPException(status_code=400, detail="Guardian is already assigned to this patient")` → `raise ConflictError("Guardian is already assigned to this patient")`

Update these 29 existing tests from `400` to `409` (change `status_code == 400` to `status_code == 409`; where the test name ends `_raises_400`, rename it to `_raises_409`; message assertions stay as they are):

- `tests/integration/test_patient_outbox_integration.py::test_duplicate_patient_fails_atomically`
- `tests/unit/test_patient_dementia_stage_list.py::test_create_dementia_stage_duplicate_check_case_insensitive`
- `tests/unit/test_patient_dementia_stage_list.py::test_update_dementia_stage_duplicate_check`
- `tests/unit/test_patient_guardian.py::test_create_guardian_nric_conflicts_with_active_patient`
- `tests/unit/test_patient_guardian.py::test_create_guardian_nric_conflicts_with_existing_guardian`
- `tests/unit/test_patient_guardian.py::test_update_guardian_nric_conflicts_with_active_patient`
- `tests/unit/test_patient_guardian.py::test_update_guardian_nric_conflicts_with_existing_guardian`
- `tests/unit/test_patient_highlight_type.py::test_create_highlight_type_duplicate_typecode_raises_400`
- `tests/unit/test_patient_list_language.py::test_create_language_duplicate_raises_400`
- `tests/unit/test_patient_list_language.py::test_update_language_duplicate_raises_400`
- `tests/unit/test_patient_medical_diagnosis_list.py::test_create_diagnosis_duplicate_check_case_insensitive`
- `tests/unit/test_patient_medical_history.py::test_create_medical_history_duplicate_raises_400`
- `tests/unit/test_patient_medical_history.py::test_update_medical_history_duplicate_raises_400_when_diagnosis_changes`
- `tests/unit/test_patient_medication.py::test_create_medication_fails_duplicate_exists`
- `tests/unit/test_patient_medication.py::test_update_medication_fails_duplicate_exists`
- `tests/unit/test_patient_patient_guardian.py::test_assign_guardian_to_patient_already_assigned`
- `tests/unit/test_patient_personal_preference.py::test_create_preference_duplicate_raises_400`
- `tests/unit/test_patient_personal_preference.py::test_update_preference_duplicate_raises_400`
- `tests/unit/test_patient_personal_preference_list.py::test_create_preference_list_duplicate_case_insensitive`
- `tests/unit/test_patient_personal_preference_list.py::test_update_preference_list_duplicate_check`
- `tests/unit/test_patient_photo_list_album.py::test_create_photo_list_album_duplicate_check_case_insensitive`
- `tests/unit/test_patient_photo_list_album.py::test_update_photo_list_album_duplicate_check`
- `tests/unit/test_patient_prescription.py::test_update_prescription_duplicate_error`
- `tests/unit/test_patient_prescription_list.py::test_create_prescription_list_duplicate_check`
- `tests/unit/test_patient_prescription_list.py::test_create_prescription_list_duplicate_case_insensitive`
- `tests/unit/test_patient_problem.py::test_create_problem_fails_duplicate_exists`
- `tests/unit/test_patient_problem.py::test_update_problem_fails_duplicate_exists`
- `tests/unit/test_patient_problem_list.py::test_create_problem_list_duplicate_check_case_insensitive`
- `tests/unit/test_patient_problem_list.py::test_update_problem_list_duplicate_check`

(The integration test runs only in CI against a real DB.)

- [ ] **Step 4: Run to verify, then the full suite**

Run: `$ENV python -m pytest tests/unit/test_error_conventions.py -q` → `3 passed`.
Run: `$ENV python -m pytest tests/unit -q` → `486 passed`. Any failure outside the 29 listed tests is a defect in this task.

- [ ] **Step 5: Commit**

```bash
git add app/crud app/routers tests
git commit -m "Return 409 Conflict for duplicate and uniqueness errors"
```

### Task 5: Verify and open the draft PR

**Files:** none changed.

- [ ] **Step 1: Re-check the inventory against the code**

Run: `$ENV python -m pytest tests/unit -q` → `486 passed`, 0 failed.
Run: `python -c "from app.main import app"` with `$ENV` → imports without error.
Run: `grep -rn "detail=str(e)\|{str(e)}" app/crud app/routers` → no output.

- [ ] **Step 2: Review the diff for scope**

Run: `git diff --stat origin/staging...HEAD` — only `app/errors.py`, `app/main.py`, files named in Tasks 3-4, tests, and `docs/specs/*`. No changes under `app/messaging/` or to `app/crud/ref_user_crud.py`.

- [ ] **Step 3: Push and open a draft PR**

```bash
git push -u origin feature/standardize-error-responses
gh pr create --draft --base staging --head feature/standardize-error-responses \
  --title "Standardise API error responses" \
  --body-file docs/specs/2026-10-04-api-error-format-design.md
```

Then edit the PR body down to: summary, the error shape, status-code changes (`400`→`422` validation, `400`→`409` conflicts), "no WebFE change needed", and the staging checks from spec §7.

- [ ] **Step 4: After merge and deploy to staging** (manual, NTU VPN): add a duplicate dementia stage → UI shows the message, response `409`; open a patient with no allergies → `404` handling unchanged; tell the Activity Service owner about the nested error body in `services/patient_service.py:24,40`.
