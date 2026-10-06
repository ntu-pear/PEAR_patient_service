import base64
import json
import time

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.auth import jwt_utils, token_verifier
from app.auth.token_verifier import VerifiedUser


def _token(role="DOCTOR", user_id="U1"):
    sub = json.dumps({"userId": user_id, "fullName": "Dr Lim", "email": "lim@example.com",
                      "roleName": role, "sessionId": "S1"})
    payload = json.dumps({"sub": sub, "exp": int(time.time()) + 3600}).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"eyJhbGciOiJIUzI1NiJ9.{body}.sig"


def _request(token=None, query=b""):
    headers = [(b"authorization", f"Bearer {token}".encode())] if token else []
    return Request({"type": "http", "method": "GET", "path": "/api/v1/patients/1",
                    "query_string": query, "headers": headers})


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.delenv("AUTH_VERIFY_MODE", raising=False)
    token_verifier.reset_cache()


def test_shadow_forged_token_still_returns_claimed_payload(monkeypatch):
    calls = []
    monkeypatch.setattr(jwt_utils, "apply_verification", lambda **kw: calls.append(kw) or None)
    payload = jwt_utils.extract_jwt_payload(_request(_token(role="ADMIN")))
    assert payload.roleName == "ADMIN"
    assert calls[0]["claimed_role"] == "ADMIN" and calls[0]["endpoint"] == "/api/v1/patients/1"


def test_enforce_uses_verified_identity_and_keeps_session(monkeypatch):
    verified = VerifiedUser("U1", "Dr Lim (verified)", "DOCTOR", "lim@example.com")
    monkeypatch.setattr(jwt_utils, "apply_verification", lambda **kw: verified)
    payload = jwt_utils.extract_jwt_payload(_request(_token()))
    assert payload.fullName == "Dr Lim (verified)" and payload.sessionId == "S1"


def test_enforce_rejection_raises_when_auth_required(monkeypatch):
    def reject(**kw):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    monkeypatch.setattr(jwt_utils, "apply_verification", reject)
    with pytest.raises(HTTPException) as exc:
        jwt_utils.extract_jwt_payload(_request(_token()))
    assert exc.value.status_code == 401


def test_enforce_rejection_returns_none_when_auth_optional(monkeypatch):
    def reject(**kw):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    monkeypatch.setattr(jwt_utils, "apply_verification", reject)
    assert jwt_utils.extract_jwt_payload(_request(_token()), require_auth=False) is None


def test_explicit_require_auth_false_is_recorded(monkeypatch):
    seen = []
    monkeypatch.setattr(jwt_utils, "record_auth_bypass", lambda endpoint: seen.append(endpoint))
    monkeypatch.setattr(jwt_utils, "apply_verification", lambda **kw: None)
    jwt_utils.extract_jwt_payload(_request(_token(), query=b"require_auth=false"), require_auth=False)
    assert seen == ["/api/v1/patients/1"]
