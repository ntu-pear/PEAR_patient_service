from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.crud.patient_allocation_crud import (
    create_allocation,
    delete_allocation,
    get_all_allocations,
    get_allocation_by_id,
    get_allocation_by_patient,
    get_guardian_id_by_patient,
    update_allocation,
)
from app.schemas.patient_allocation import PatientAllocationCreate, PatientAllocationUpdate
from tests.utils.mock_db import get_db_session_mock


def test_get_allocation_by_id_found(db_session_mock):
    mock_allocation = MagicMock(id=1, patientId=1, active="Y")
    mock_guardian_user_id = "guardian-user-123"
    db_session_mock.query.return_value.join.return_value.filter.return_value.first.return_value = (
        mock_allocation, mock_guardian_user_id
    )

    result = get_allocation_by_id(db_session_mock, 1)

    assert result is not None
    assert result["guardianApplicationUserId"] == mock_guardian_user_id


def test_get_allocation_by_id_not_found(db_session_mock):
    db_session_mock.query.return_value.join.return_value.filter.return_value.first.return_value = None

    result = get_allocation_by_id(db_session_mock, 999)

    assert result is None


def test_get_allocation_by_patient_found(db_session_mock):
    mock_allocation = MagicMock(id=1, patientId=1, active="Y")
    mock_guardian_user_id = "guardian-user-123"
    db_session_mock.query.return_value.join.return_value.filter.return_value.first.return_value = (
        mock_allocation, mock_guardian_user_id
    )

    result = get_allocation_by_patient(db_session_mock, 1)

    assert result is not None
    assert result["guardianApplicationUserId"] == mock_guardian_user_id


def test_get_allocation_by_patient_not_found(db_session_mock):
    db_session_mock.query.return_value.join.return_value.filter.return_value.first.return_value = None

    result = get_allocation_by_patient(db_session_mock, 999)

    assert result is None


def test_get_guardian_id_by_patient_found(db_session_mock):
    db_session_mock.query.return_value.join.return_value.filter.return_value.first.return_value = ("guardian-user-123",)

    result = get_guardian_id_by_patient(db_session_mock, 1)

    assert result == "guardian-user-123"


def test_get_all_allocations_returns_list(db_session_mock):
    mock_a = MagicMock(id=1, patientId=1, active="Y")
    db_session_mock.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
        (mock_a, "guardian-user-123")
    ]

    result = get_all_allocations(db_session_mock)

    assert result is not None
    assert len(result) == 1
    assert result[0]["guardianApplicationUserId"] == "guardian-user-123"


def test_get_all_allocations_empty(db_session_mock):
    db_session_mock.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    result = get_all_allocations(db_session_mock)

    assert result is None


@patch("app.crud.patient_allocation_crud.get_allocation_by_patient", return_value=None)
@patch("app.crud.patient_allocation_crud.get_outbox_service")
@patch("app.crud.patient_allocation_crud.log_crud_action")
def test_create_allocation_happy_path(mock_log, mock_outbox_fn, mock_get_alloc, db_session_mock, allocation_create):
    result = create_allocation(db_session_mock, allocation_create, "user1", "User One")

    db_session_mock.add.assert_called_once()
    db_session_mock.flush.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()


@patch("app.crud.patient_allocation_crud.get_allocation_by_patient", return_value={"id": 1, "patientId": 1})
def test_create_allocation_duplicate_raises(mock_get_alloc, db_session_mock, allocation_create):
    with pytest.raises(ValueError, match="Patient already has an active allocation"):
        create_allocation(db_session_mock, allocation_create, "user1", "User One")


@patch("app.crud.patient_allocation_crud.get_outbox_service")
@patch("app.crud.patient_allocation_crud.log_crud_action")
def test_update_allocation_found(mock_log, mock_outbox_fn, db_session_mock, allocation_update):
    mock_allocation = MagicMock(id=1, patientId=1, active="Y", doctorId="old-doctor")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_allocation

    result = update_allocation(db_session_mock, 1, allocation_update, "user1", "User One")

    db_session_mock.commit.assert_called_once()
    assert result is mock_allocation


def test_update_allocation_not_found(db_session_mock, allocation_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = update_allocation(db_session_mock, 999, allocation_update, "user1", "User One")

    assert result is None


def test_update_allocation_inactive_raises(db_session_mock, allocation_update):
    mock_allocation = MagicMock(id=1, patientId=1, active="N")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_allocation

    with pytest.raises(ValueError, match="Cannot update inactive allocation"):
        update_allocation(db_session_mock, 1, allocation_update, "user1", "User One")


@patch("app.crud.patient_allocation_crud.get_outbox_service")
@patch("app.crud.patient_allocation_crud.log_crud_action")
def test_delete_allocation_happy_path(mock_log, mock_outbox_fn, db_session_mock):
    mock_allocation = MagicMock(id=1, patientId=1, active="Y")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_allocation

    result = delete_allocation(db_session_mock, 1, "user1", "User One")

    assert mock_allocation.isDeleted == "1"
    db_session_mock.commit.assert_called_once()
    assert result is mock_allocation


def test_delete_allocation_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_allocation(db_session_mock, 999, "user1", "User One")

    assert result is None


def test_delete_allocation_already_inactive_raises(db_session_mock):
    mock_allocation = MagicMock(id=1, patientId=1, active="N")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_allocation

    with pytest.raises(ValueError, match="Allocation is already inactive"):
        delete_allocation(db_session_mock, 1, "user1", "User One")


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def allocation_create():
    return PatientAllocationCreate(
        patientId=1,
        guardianId=1,
        doctorId="doctor-1",
        CreatedById="1",
        ModifiedById="1",
    )


@pytest.fixture
def allocation_update():
    return PatientAllocationUpdate(
        patientId=1,
        guardianId=1,
        doctorId="doctor-2",
        ModifiedById="1",
    )
