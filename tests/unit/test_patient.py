from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.crud.patient_crud import (
    create_patient,
    delete_patient,
    get_patient,
    get_patients,
    get_patients_by_doctor,
    update_patient,
)
from app.schemas.patient import PatientCreate, PatientUpdate
from tests.utils.mock_db import get_db_session_mock


def test_get_patient_found(db_session_mock):
    mock_patient = MagicMock(id=1, name="John Doe", nric="S1234567A", isDeleted=0)
    mock_patient.mask_nric = "SXXXXX67A"
    db_session_mock.query.return_value.options.return_value.filter.return_value.first.return_value = mock_patient

    result = get_patient(db_session_mock, 1)

    assert result is mock_patient
    assert result.nric == "SXXXXX67A"


def test_get_patient_not_found(db_session_mock):
    db_session_mock.query.return_value.options.return_value.filter.return_value.first.return_value = None

    result = get_patient(db_session_mock, 999)

    assert result is None


def test_get_patients_returns_list(db_session_mock):
    mock_patient = MagicMock(id=1, name="John Doe", nric="S1234567A")
    mock_patient.mask_nric = "SXXXXX67A"

    mock_patient_query = MagicMock()
    mock_patient_query.options.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_patient]

    mock_count_query = MagicMock()
    mock_count_query.select_from.return_value.filter.return_value.scalar.return_value = 1

    db_session_mock.query.side_effect = [mock_patient_query, mock_count_query]

    patients, total_records, total_pages = get_patients(db_session_mock)

    assert len(patients) == 1
    assert total_records == 1
    assert total_pages == 1


def test_get_patients_by_doctor_returns_list(db_session_mock):
    mock_patient = MagicMock(id=1, name="Jane Doe", nric="S7654321B")
    mock_patient.mask_nric = "SXXXXX21B"

    mock_filter = (
        db_session_mock.query.return_value
        .options.return_value
        .join.return_value
        .filter.return_value
    )
    mock_filter.count.return_value = 1
    mock_filter.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_patient]

    patients, total_records, total_pages = get_patients_by_doctor(db_session_mock, "doctor-1")

    assert len(patients) == 1
    assert total_records == 1
    assert total_pages == 1


@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.log_crud_action")
def test_create_patient(mock_log, mock_outbox_fn, db_session_mock, patient_create):
    mock_new_patient = MagicMock(id=1, name=patient_create.name, nric=patient_create.nric)

    mock_nric_check = MagicMock()
    mock_nric_check.filter.return_value.first.return_value = None

    mock_guardian_check = MagicMock()
    mock_guardian_check.filter.return_value.first.return_value = None

    mock_fetch = MagicMock()
    mock_fetch.filter.return_value.first.return_value = mock_new_patient

    db_session_mock.query.side_effect = [mock_nric_check, mock_guardian_check, mock_fetch]

    result = create_patient(db_session_mock, patient_create, "user1", "User One")

    db_session_mock.execute.assert_called_once()
    db_session_mock.flush.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert result is mock_new_patient


@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.log_crud_action")
def test_update_patient_found(mock_log, mock_outbox_fn, db_session_mock, patient_update):
    mock_patient = MagicMock(id=1, nric="S1234567A", isDeleted=0, name="Old Name")

    mock_fetch = MagicMock()
    mock_fetch.filter.return_value.first.return_value = mock_patient

    mock_nric_check = MagicMock()
    mock_nric_check.filter.return_value.first.return_value = None

    mock_guardian_check = MagicMock()
    mock_guardian_check.filter.return_value.first.return_value = None

    db_session_mock.query.side_effect = [mock_fetch, mock_nric_check, mock_guardian_check]

    result = update_patient(db_session_mock, 1, patient_update, "user1", "User One")

    assert result is mock_patient


def test_update_patient_not_found(db_session_mock, patient_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_patient(db_session_mock, 999, patient_update, "user1", "User One")

    assert exc_info.value.status_code == 404


@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.log_crud_action")
def test_delete_patient_soft_delete(mock_log, mock_outbox_fn, db_session_mock):
    mock_patient = MagicMock(id=1, name="John Doe", isDeleted=0)
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_patient

    delete_patient(db_session_mock, 1, "user1", "User One")

    assert mock_patient.isDeleted == "1"
    db_session_mock.commit.assert_called_once()


def test_delete_patient_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_patient(db_session_mock, 999, "user1", "User One")

    assert exc_info.value.status_code == 404


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def patient_create():
    return PatientCreate(
        name="John Doe",
        nric="S1234567A",
        gender="M",
        dateOfBirth=datetime(1990, 1, 1),
        isApproved="1",
        preferredLanguageId=1,
        updateBit="1",
        autoGame="0",
        startDate=datetime.now(),
        isActive="1",
        isRespiteCare="0",
        privacyLevel=0,
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )


@pytest.fixture
def patient_update():
    return PatientUpdate(
        name="John Doe Updated",
        nric="S1234567A",
        gender="M",
        dateOfBirth=datetime(1990, 1, 1),
        isApproved="1",
        preferredLanguageId=1,
        updateBit="1",
        autoGame="0",
        startDate=datetime.now(),
        isActive="1",
        isRespiteCare="0",
        privacyLevel=0,
        modifiedDate=datetime.now(),
        ModifiedById="1",
    )
