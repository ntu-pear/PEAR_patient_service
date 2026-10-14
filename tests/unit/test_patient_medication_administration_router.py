"""Role checks and actor handling on the administration endpoints. CRUD is stubbed.
Importing app.main is safe: TestClient is not used as a context manager, so the
lifespan (outbox processor, consumers) never starts."""
import base64
import json
import time
from datetime import date, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.auth import jwt_utils
from app.database import get_db
from app.main import app
from app.routers import patient_medication_administration_router as router_module

URL = "/api/v1/Medication/administration"
WHEN = datetime(2026, 10, 14, 0, 5)
ROW = SimpleNamespace(
    Id=1, MedicationId=7, PatientId=3, AdministerDate=date(2026, 10, 14), ScheduledTime="0800",
    ActualAdministerTime=WHEN, AdministeredById="U1", IsDeleted="0", CreatedDateTime=WHEN,
    UpdatedDateTime=WHEN, CreatedById="U1", ModifiedById="U1",
)
BODY = {"MedicationId": 7, "ScheduledTime": "0800", "AdministerDate": "2026-10-14"}
UNDO = {"medication_id": 7, "administer_date": "2026-10-14", "scheduled_time": "0800"}


def _auth(role):
    sub = json.dumps({"userId": "U1", "fullName": "Sam Lee", "email": "sam@example.com",
                      "roleName": role, "sessionId": "S1"})
    payload = json.dumps({"sub": sub, "exp": int(time.time()) + 3600}).encode()
    token = "eyJhbGciOiJIUzI1NiJ9." + base64.urlsafe_b64encode(payload).decode().rstrip("=") + ".sig"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(monkeypatch):
    calls = SimpleNamespace(mark=[], undo=[], undo_result=ROW)
    monkeypatch.setattr(jwt_utils, "apply_verification", lambda **kw: None)  # shadow mode, no User service

    def mark(db, body, user_id, full_name, role):
        calls.mark.append((body, user_id, full_name, role))
        return ROW, True

    def undo(db, medication_id, administer_date, scheduled_time, user_id, full_name, role):
        calls.undo.append((medication_id, administer_date, scheduled_time, user_id, role))
        return calls.undo_result

    monkeypatch.setattr(router_module.crud, "mark_administered", mark)
    monkeypatch.setattr(router_module.crud, "undo_administration", undo)
    app.dependency_overrides[get_db] = lambda: None
    yield TestClient(app, raise_server_exceptions=False), calls
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.parametrize("role", ["CAREGIVER", "SUPERVISOR"])
def test_care_roles_can_mark_a_dose_given(client, role):
    http, calls = client
    response = http.put(URL, json=BODY, headers=_auth(role))
    assert response.status_code == 200
    assert response.json()["data"]["Id"] == 1
    assert calls.mark[0][1:] == ("U1", "Sam Lee", role)


@pytest.mark.parametrize("role", ["DOCTOR", "GUARDIAN", "ADMIN", "GAME THERAPIST"])
def test_other_roles_cannot_mark(client, role):
    http, calls = client
    response = http.put(URL, json=BODY, headers=_auth(role))
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
    assert calls.mark == []


def test_no_token_is_401(client):
    http, calls = client
    assert http.put(URL, json=BODY).status_code == 401
    assert calls.mark == []


def test_require_auth_false_does_not_bypass(client):
    http, calls = client
    assert http.put(URL + "?require_auth=false", json=BODY).status_code == 401
    assert calls.mark == []


def test_actor_comes_from_the_token_not_the_body(client):
    http, calls = client
    http.put(URL, json={**BODY, "AdministeredById": "someone-else"}, headers=_auth("CAREGIVER"))
    assert calls.mark[0][1] == "U1"


def test_supervisor_can_undo(client):
    http, calls = client
    response = http.delete(URL, params=UNDO, headers=_auth("SUPERVISOR"))
    assert response.status_code == 200
    assert calls.undo == [(7, date(2026, 10, 14), "0800", "U1", "SUPERVISOR")]


@pytest.mark.parametrize("role", ["CAREGIVER", "DOCTOR", "ADMIN"])
def test_only_supervisor_can_undo(client, role):
    http, calls = client
    assert http.delete(URL, params=UNDO, headers=_auth(role)).status_code == 403
    assert calls.undo == []


def test_undo_with_nothing_live_returns_null(client):
    http, calls = client
    calls.undo_result = None
    response = http.delete(URL, params=UNDO, headers=_auth("SUPERVISOR"))
    assert response.status_code == 200
    assert response.json() == {"data": None}
