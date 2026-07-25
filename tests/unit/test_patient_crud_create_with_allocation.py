from datetime import datetime
from unittest.mock import MagicMock, patch, call

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.patient import PatientCreateWithAllocation
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db():
    return get_db_session_mock()


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
        guardianId=1,
    )


def _setup_nric_clean(db):
    """NRIC checks pass (no conflicts)."""
    db.query.return_value.filter.return_value.first.return_value = None


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_happy_path_auto_assign(mock_least, mock_outbox, mock_log, db, patient_data):
    mock_least.side_effect = lambda role, db_, api_key: {
        "DOCTOR": "D001", "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]

    _setup_nric_clean(db)

    guardian_mock = MagicMock()
    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None,           # NRIC check (patient)
        None,           # NRIC check (guardian conflict)
        guardian_mock,  # guardianId exists check
        new_patient_mock,  # get new_patient after insert
    ]

    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    from app.crud.patient_crud import create_patient
    result = create_patient(
        db, patient_data, user="SUP1", user_full_name="Supervisor",
        api_key="key", supervisor_id="SUP1"
    )

    db.commit.assert_called_once()
    db.add.assert_called()


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_explicit_ids_skip_user_service(mock_least, mock_outbox, mock_log, db, patient_data):
    patient_data.doctorId = "D_EXPLICIT"
    patient_data.gameTherapistId = "GT_EXPLICIT"
    patient_data.caregiverId = "CG_EXPLICIT"

    guardian_mock = MagicMock()
    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None, None, guardian_mock, new_patient_mock
    ]
    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    from app.crud.patient_crud import create_patient
    create_patient(
        db, patient_data, user="SUP1", user_full_name="Supervisor",
        api_key="key", supervisor_id="SUP1"
    )

    mock_least.assert_not_called()


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_partial_explicit_ids(mock_least, mock_outbox, mock_log, db, patient_data):
    patient_data.doctorId = "D_EXPLICIT"

    mock_least.side_effect = lambda role, db_, api_key: {
        "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]

    guardian_mock = MagicMock()
    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None, None, guardian_mock, new_patient_mock
    ]
    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    from app.crud.patient_crud import create_patient
    create_patient(
        db, patient_data, user="SUP1", user_full_name="Supervisor",
        api_key="key", supervisor_id="SUP1"
    )

    called_roles = [c.args[0] for c in mock_least.call_args_list]
    assert "DOCTOR" not in called_roles
    assert "GAME THERAPIST" in called_roles
    assert "CAREGIVER" in called_roles


def test_doctor2_same_as_doctor(db, patient_data):
    patient_data.doctorId = "D001"
    patient_data.doctor2Id = "D001"

    guardian_mock = MagicMock()
    db.query.return_value.filter.return_value.first.side_effect = [
        None,           # NRIC check (patient)
        None,           # NRIC check (guardian conflict)
        guardian_mock,  # guardianId exists
    ]

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 400


def test_supervisor2_same_as_supervisor(db, patient_data):
    patient_data.supervisor2Id = "SUP1"

    guardian_mock = MagicMock()
    db.query.return_value.filter.return_value.first.side_effect = [
        None,           # NRIC check (patient)
        None,           # NRIC check (guardian conflict)
        guardian_mock,  # guardianId exists
    ]

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 400


def test_guardian_not_found(db, patient_data):
    db.query.return_value.filter.return_value.first.side_effect = [
        None,   # NRIC check (patient)
        None,   # NRIC check (guardian conflict)
        None,   # guardianId check -> not found
    ]

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 400


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_user_service_unreachable_raises_503(mock_least, mock_outbox, mock_log, db, patient_data):
    mock_least.side_effect = HTTPException(status_code=503, detail="unreachable")

    guardian_mock = MagicMock()
    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None, None, guardian_mock, new_patient_mock
    ]

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 503
    db.rollback.assert_called()


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_allocation_insert_fail_rolls_back(mock_least, mock_outbox, mock_log, db, patient_data):
    mock_least.side_effect = lambda role, db_, api_key: "X001"

    guardian_mock = MagicMock()
    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None, None, guardian_mock, new_patient_mock
    ]
    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    # First flush (patient) succeeds, second flush (allocation) fails
    db.flush.side_effect = [None, SQLAlchemyError("allocation insert failed")]

    from app.crud.patient_crud import create_patient
    with pytest.raises((SQLAlchemyError, HTTPException)):
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    db.rollback.assert_called()


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_doctor2_same_as_auto_assigned_doctor(mock_least, mock_outbox, mock_log, db, patient_data):
    patient_data.doctor2Id = "D001"
    mock_least.side_effect = lambda role, db_, api_key: {
        "DOCTOR": "D001", "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]

    guardian_mock = MagicMock()
    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None, None, guardian_mock, new_patient_mock
    ]
    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 400
    db.rollback.assert_called()
