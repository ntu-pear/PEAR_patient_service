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
    assert body["detail"] == "Request validation failed: name: Field required"
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


def test_validation_detail_summarises_every_field_for_the_webfe(client):
    # The WebFE's mapBackendErrorToField / extractErrorMessage read a string
    # detail and match field keywords in it, so the summary must name fields.
    response = client.post("/items", json={})
    assert response.json()["detail"] == (
        "Request validation failed: name: Field required; nric: Field required"
    )


def test_validation_error_without_location_still_returns_422():
    from fastapi.exceptions import RequestValidationError

    app = FastAPI()
    register_error_handlers(app)

    @app.get("/no-loc")
    def no_loc():
        raise RequestValidationError([{"loc": (), "msg": "Invalid payload", "type": "value_error"}])

    response = TestClient(app, raise_server_exceptions=False).get("/no-loc")
    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed: Invalid payload"
