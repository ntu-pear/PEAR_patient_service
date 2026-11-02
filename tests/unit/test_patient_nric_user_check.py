from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.crud.patient_crud import create_patient
from app.schemas.patient import PatientCreateWithAllocation
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db():
    db = get_db_session_mock()
    # No local patient or guardian holds the NRIC
    db.query.return_value.filter.return_value.first.return_value = None
    return db


@pytest.fixture
def patient_data():
    return PatientCreateWithAllocation(
        name="Test Patient",
        nric="S1234567A",
        gender="M",
        dateOfBirth=datetime(1950, 1, 1),
        isApproved="1",
        updateBit="1",
        autoGame="1",
        startDate=datetime(2026, 1, 1),
        isActive="1",
        isRespiteCare="0",
        privacyLevel=1,
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )


@patch("app.crud.patient_crud.check_nric_exists", return_value=True)
def test_nric_held_by_user_is_rejected(mock_check, db, patient_data):
    with pytest.raises(HTTPException) as exc:
        create_patient(db, patient_data, user="SUP1", user_full_name="Supervisor", api_key="key", supervisor_id="SUP1")

    assert exc.value.status_code == 409
    mock_check.assert_called_once_with("S1234567A", "key")
    db.execute.assert_not_called()
    db.commit.assert_not_called()


@patch("app.crud.patient_crud.check_nric_exists", side_effect=HTTPException(status_code=503, detail="unreachable"))
def test_user_service_unreachable_blocks_creation(mock_check, db, patient_data):
    with pytest.raises(HTTPException) as exc:
        create_patient(db, patient_data, user="SUP1", user_full_name="Supervisor", api_key="key", supervisor_id="SUP1")

    assert exc.value.status_code == 503
    db.execute.assert_not_called()
    db.commit.assert_not_called()


@patch("app.crud.patient_crud.check_nric_exists")
def test_local_nric_conflict_skips_user_service(mock_check, db, patient_data):
    db.query.return_value.filter.return_value.first.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        create_patient(db, patient_data, user="SUP1", user_full_name="Supervisor", api_key="key", supervisor_id="SUP1")

    assert exc.value.status_code == 409
    mock_check.assert_not_called()


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff", return_value="STAFF1")
@patch("app.crud.patient_crud.check_nric_exists", return_value=False)
def test_nric_not_held_by_user_creates_patient(mock_check, mock_least, mock_outbox, mock_log, db, patient_data):
    new_patient = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [None, None, new_patient]
    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    result = create_patient(db, patient_data, user="SUP1", user_full_name="Supervisor", api_key="key", supervisor_id="SUP1")

    mock_check.assert_called_once_with("S1234567A", "key")
    db.commit.assert_called_once()
    assert result is new_patient
