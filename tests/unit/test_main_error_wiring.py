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
