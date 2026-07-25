import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def api_key():
    return "test-service-key"


# --- get_active_staff_by_role tests ---

def test_get_active_staff_by_role_missing_key():
    from app.services.user_service import get_active_staff_by_role
    with pytest.raises(HTTPException) as exc:
        get_active_staff_by_role("DOCTOR", api_key=None)
    assert exc.value.status_code == 500


def test_get_active_staff_by_role_returns_filtered_list(api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "users": [
            {"id": "U001", "role": "DOCTOR"},
            {"id": "U002", "role": "CAREGIVER"},
            {"id": "U003", "role": "DOCTOR"},
        ]
    }
    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        result = user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
    assert result == ["U001", "U003"]


def test_get_active_staff_by_role_wrong_key(api_key):
    mock_response = MagicMock()
    mock_response.status_code = 403
    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        with pytest.raises(HTTPException) as exc:
            user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
        assert exc.value.status_code == 403


def test_get_active_staff_by_role_unreachable(api_key):
    import httpx
    with patch("httpx.get", side_effect=httpx.ConnectError("unreachable")), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        with pytest.raises(HTTPException) as exc:
            user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
        assert exc.value.status_code == 503


def test_get_active_staff_by_role_empty_list(api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"users": []}
    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        with pytest.raises(HTTPException) as exc:
            user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
        assert exc.value.status_code == 503


def test_get_active_staff_by_role_malformed_response(api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"unexpected": "format"}
    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        with pytest.raises(HTTPException) as exc:
            user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
        assert exc.value.status_code == 503


# --- get_least_loaded_staff tests ---

def test_get_least_loaded_staff_returns_least_loaded(db_session_mock, api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "users": [
            {"id": "U001", "role": "DOCTOR"},
            {"id": "U002", "role": "DOCTOR"},
        ]
    }

    call_count = {"n": 0}

    def varying_count(*args, **kwargs):
        mock_q = MagicMock()
        call_count["n"] += 1
        count = 3 if call_count["n"] == 1 else 1
        mock_q.filter.return_value.filter.return_value.filter.return_value.count.return_value = count
        return mock_q

    db_session_mock.query.side_effect = varying_count

    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        result = user_service.get_least_loaded_staff("DOCTOR", db_session_mock, api_key=api_key)

    assert result == "U002"


def test_get_least_loaded_staff_tiebreak_lowest_id(db_session_mock, api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "users": [
            {"id": "10", "role": "DOCTOR"},
            {"id": "2", "role": "DOCTOR"},
        ]
    }
    mock_q = MagicMock()
    mock_q.filter.return_value.filter.return_value.filter.return_value.count.return_value = 0
    db_session_mock.query.return_value = mock_q

    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        result = user_service.get_least_loaded_staff("DOCTOR", db_session_mock, api_key=api_key)

    assert result == "2"  # int("2") < int("10")


def test_get_active_staff_by_role_timeout(api_key):
    import httpx
    with patch("httpx.get", side_effect=httpx.TimeoutException("timed out")), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        with pytest.raises(HTTPException) as exc:
            user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
        assert exc.value.status_code == 503


def test_get_active_staff_by_role_skips_entries_missing_id(api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "users": [
            {"role": "DOCTOR"},
            {"id": "U003", "role": "DOCTOR"},
        ]
    }
    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        result = user_service.get_active_staff_by_role("DOCTOR", api_key=api_key)
    assert result == ["U003"]


def test_get_least_loaded_staff_mixed_id_formats(db_session_mock, api_key):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "users": [
            {"id": "abc-uuid", "role": "DOCTOR"},
            {"id": "2", "role": "DOCTOR"},
        ]
    }
    mock_q = MagicMock()
    mock_q.filter.return_value.filter.return_value.filter.return_value.count.return_value = 0
    db_session_mock.query.return_value = mock_q

    with patch("httpx.get", return_value=mock_response), \
         patch.dict(os.environ, {"USER_SERVICE_URL": "http://user-service"}):
        from app.services import user_service
        import importlib; importlib.reload(user_service)
        result = user_service.get_least_loaded_staff("DOCTOR", db_session_mock, api_key=api_key)

    assert result == "2"  # numeric IDs win over non-numeric on tie
