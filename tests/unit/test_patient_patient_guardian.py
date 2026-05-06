from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.crud.patient_patient_guardian_crud import (
    create_patient_patient_guardian,
    delete_patient_patient_guardian_by_guardianId,
    delete_relationship,
    get_all_patient_guardian_by_patientId,
    get_all_patient_patient_guardian_by_guardianId,
    update_patient_patient_guardian,
)
from app.schemas.patient_patient_guardian import (
    PatientPatientGuardianCreate,
    PatientPatientGuardianUpdate,
)
from tests.utils.mock_db import get_db_session_mock


def test_get_by_patient_id_with_relationships(db_session_mock):
    mock_relationship = MagicMock()
    mock_relationship.relationship.relationshipName = "Son"
    mock_relationship.patient_guardian = MagicMock()
    mock_relationship.patient = MagicMock()
    mock_relationship.patient.nric = "S1234567A"

    db_session_mock.query.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
        mock_relationship
    ]

    with patch("app.crud.patient_patient_guardian_crud.PatientModel") as mock_patient_model, \
         patch("app.crud.patient_patient_guardian_crud.PatientGuardianModel") as mock_guardian_model, \
         patch("app.crud.patient_patient_guardian_crud.GuardianWithRelationshipModel") as mock_gwr:
        mock_patient_model.from_orm.return_value = MagicMock()
        mock_guardian_model.from_orm.return_value = MagicMock()
        mock_gwr.return_value = MagicMock()

        result = get_all_patient_guardian_by_patientId(db_session_mock, 1)

    assert result is not None


def test_get_by_patient_id_no_relationships_patient_exists(db_session_mock):
    mock_patient_raw = MagicMock(id=1)

    mock_rel_query = MagicMock()
    mock_rel_query.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []

    mock_patient_query = MagicMock()
    mock_patient_query.filter.return_value.first.return_value = mock_patient_raw

    db_session_mock.query.side_effect = [mock_rel_query, mock_patient_query]

    with patch("app.crud.patient_patient_guardian_crud.PatientModel") as mock_model:
        mock_model.from_orm.return_value = MagicMock()
        result = get_all_patient_guardian_by_patientId(db_session_mock, 1)

    assert result["patient_guardians"] == []


def test_get_by_patient_id_no_relationships_no_patient(db_session_mock):
    mock_rel_query = MagicMock()
    mock_rel_query.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []

    mock_patient_query = MagicMock()
    mock_patient_query.filter.return_value.first.return_value = None

    db_session_mock.query.side_effect = [mock_rel_query, mock_patient_query]

    result = get_all_patient_guardian_by_patientId(db_session_mock, 999)

    assert result is None


def test_get_by_guardian_id_returns_list(db_session_mock):
    mock_relationship = MagicMock()
    mock_relationship.relationship.relationshipName = "Son"
    mock_relationship.patient_guardian = MagicMock()
    mock_relationship.patient = MagicMock()

    db_session_mock.query.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
        mock_relationship
    ]

    with patch("app.crud.patient_patient_guardian_crud.PatientModel") as mock_patient_model, \
         patch("app.crud.patient_patient_guardian_crud.PatientGuardianModel") as mock_guardian_model, \
         patch("app.crud.patient_patient_guardian_crud.PatientWithRelationshipModel") as mock_pwr:
        mock_patient_model.from_orm.return_value = MagicMock()
        mock_guardian_model.from_orm.return_value = MagicMock()
        mock_pwr.return_value = MagicMock()

        result = get_all_patient_patient_guardian_by_guardianId(db_session_mock, "guardian-user-id")

    assert result is not None


@patch("app.crud.patient_patient_guardian_crud.log_crud_action")
def test_create_patient_patient_guardian(mock_log, db_session_mock, ppg_create):
    result = create_patient_patient_guardian(db_session_mock, ppg_create)

    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)


@patch("app.crud.patient_patient_guardian_crud.log_crud_action")
def test_update_patient_patient_guardian_found(mock_log, db_session_mock, ppg_update):
    mock_rel = MagicMock(id=1, patientId=1, guardianId=1, isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_rel

    result = update_patient_patient_guardian(db_session_mock, 1, ppg_update)

    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_rel)
    assert result is mock_rel


def test_update_patient_patient_guardian_not_found(db_session_mock, ppg_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = update_patient_patient_guardian(db_session_mock, 999, ppg_update)

    assert result is None


@patch("app.crud.patient_patient_guardian_crud.log_crud_action")
def test_delete_by_guardian_id_found(mock_log, db_session_mock):
    mock_rel = MagicMock(id=1, guardianId=1, isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_rel

    result = delete_patient_patient_guardian_by_guardianId(db_session_mock, 1)

    assert mock_rel.isDeleted == "1"
    db_session_mock.commit.assert_called_once()
    assert result is mock_rel


def test_delete_by_guardian_id_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_patient_patient_guardian_by_guardianId(db_session_mock, 999)

    assert result is None


@patch("app.crud.patient_patient_guardian_crud.log_crud_action")
def test_delete_relationship_found(mock_log, db_session_mock):
    mock_rel = MagicMock(id=1, isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_rel

    result = delete_relationship(db_session_mock, 1)

    assert mock_rel.isDeleted == "1"
    db_session_mock.commit.assert_called_once()
    assert result is mock_rel


def test_delete_relationship_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_relationship(db_session_mock, 999)

    assert result is None


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def ppg_create():
    return PatientPatientGuardianCreate(
        isDeleted="0",
        patientId=1,
        guardianId=1,
        relationshipId=1,
        CreatedById="1",
        ModifiedById="1",
    )


@pytest.fixture
def ppg_update():
    return PatientPatientGuardianUpdate(
        isDeleted="0",
        patientId=1,
        guardianId=1,
        relationshipId=2,
        CreatedById="1",
        ModifiedById="1",
    )
