"""X-Request-ID is forwarded on Patient's outbound calls only when ops logging provides one."""
from unittest.mock import MagicMock

import httpx
import pytest

from app.auth import token_verifier
from app.services import user_service


@pytest.fixture
def captured(monkeypatch):
    seen = {}

    def fake_get(url, headers=None, timeout=None, **kwargs):
        seen["url"], seen["headers"] = url, headers
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"users": [{"id": "U1", "role": "DOCTOR"}]}
        return response

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setenv("USER_SERVICE_URL", "http://user-service")
    return seen


def test_staff_lookup_headers_unchanged_when_ops_logging_is_off(captured):
    user_service.get_active_staff_by_role("DOCTOR", api_key="k")
    assert captured["headers"] == {"X-Api-Key": "k"}


def test_staff_lookup_forwards_request_id(captured, monkeypatch):
    monkeypatch.setattr(user_service, "outbound_headers", lambda: {"X-Request-ID": "rid-1"})
    user_service.get_active_staff_by_role("DOCTOR", api_key="k")
    assert captured["headers"] == {"X-Api-Key": "k", "X-Request-ID": "rid-1"}


def test_nric_check_forwards_request_id(captured, monkeypatch):
    monkeypatch.setattr(user_service, "outbound_headers", lambda: {"X-Request-ID": "rid-2"})
    user_service.check_nric_exists("S1234567A", api_key="k")
    assert captured["headers"] == {"X-Api-Key": "k", "X-Request-ID": "rid-2"}


def test_token_verification_call_headers(captured, monkeypatch):
    token_verifier._call_user_service("http://user-service", "tok")
    assert captured["headers"] == {"Authorization": "Bearer tok"}
    monkeypatch.setattr(token_verifier, "outbound_headers", lambda: {"X-Request-ID": "rid-3"})
    token_verifier._call_user_service("http://user-service", "tok")
    assert captured["headers"] == {"Authorization": "Bearer tok", "X-Request-ID": "rid-3"}