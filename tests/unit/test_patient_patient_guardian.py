from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.crud.patient_patient_guardian_crud import (
    create_patient_patient_guardian,
    delete_patient_patient_guardian_by_guardianId,
    delete_relationship,
    get_all_patient_guardian_by_patientId,
    get_all_patient_patient_guardian_by_guardianId,
    get_all_patient_patient_guardian_by_guardianNRIC,
    update_patient_patient_guardian,
)
from app.routers.patient_guardian_router import (
    assign_guardian_to_patient,
    get_patient_guardian_by_nric,
    unassign_guardian_from_patient,
)
from app.schemas.patient_patient_guardian import (
    PatientPatientGuardianAssign,
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


def test_get_by_guardian_nric_not_found(db_session_mock):
    """No guardian at all with this NRIC - the join query and the fallback lookup both come up empty."""
    mock_join_query = MagicMock()
    mock_join_query.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []

    mock_fallback_query = MagicMock()
    mock_fallback_query.filter.return_value.first.return_value = None

    db_session_mock.query.side_effect = [mock_join_query, mock_fallback_query]

    result = get_all_patient_patient_guardian_by_guardianNRIC(db_session_mock, "S9999999Z")

    assert result is None


def test_get_by_guardian_nric_exists_no_patients(db_session_mock):
    """Guardian exists but isn't linked to any patient yet - should return the guardian with an empty patients list, not None."""
    mock_join_query = MagicMock()
    mock_join_query.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []

    mock_guardian_raw = MagicMock(id=1, firstName="Test", nric="S1234567Z")

    mock_fallback_query = MagicMock()
    mock_fallback_query.filter.return_value.first.return_value = mock_guardian_raw

    db_session_mock.query.side_effect = [mock_join_query, mock_fallback_query]

    with patch("app.crud.patient_patient_guardian_crud.PatientGuardianModel") as mock_guardian_model:
        mock_guardian_model.from_orm.return_value = MagicMock()

        result = get_all_patient_patient_guardian_by_guardianNRIC(db_session_mock, "S1234567Z")

    assert result is not None
    assert result["patients"] == []


def test_get_by_guardian_nric_with_relationships(db_session_mock):
    """Guardian exists and already has patients linked - should return the guardian with a populated patients list."""
    mock_relationship = MagicMock()
    mock_relationship.relationship.relationshipName = "Mother"
    mock_relationship.patient_guardian = MagicMock()
    mock_relationship.patient = MagicMock()

    mock_join_query = MagicMock()
    mock_join_query.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
        mock_relationship
    ]
    db_session_mock.query.return_value = mock_join_query

    with patch("app.crud.patient_patient_guardian_crud.PatientModel") as mock_patient_model, \
         patch("app.crud.patient_patient_guardian_crud.PatientGuardianModel") as mock_guardian_model, \
         patch("app.crud.patient_patient_guardian_crud.PatientWithRelationshipModel") as mock_pwr:
        mock_patient_model.from_orm.return_value = MagicMock()
        mock_guardian_model.from_orm.return_value = MagicMock()
        mock_pwr.return_value = MagicMock()

        result = get_all_patient_patient_guardian_by_guardianNRIC(db_session_mock, "S1234567Z")

    assert result is not None
    assert len(result["patients"]) == 1


def test_get_patient_guardian_by_nric_not_found(db_session_mock):
    """Router: no guardian with this NRIC - should 404 before even calling the relationship lookup."""
    with patch("app.routers.patient_guardian_router.crud_guardian.get_guardian_by_nric", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            get_patient_guardian_by_nric(nric="S9999999Z", db=db_session_mock)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Guardian not found"


def test_get_patient_guardian_by_nric_success(db_session_mock):
    """Router: guardian exists - returns the combined guardian + patients payload."""
    mock_guardian = MagicMock(id=1, nric="S1234567Z")
    mock_response = {"patient_guardian": mock_guardian, "patients": []}

    with patch("app.routers.patient_guardian_router.crud_guardian.get_guardian_by_nric", return_value=mock_guardian), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "get_all_patient_patient_guardian_by_guardianNRIC",
             return_value=mock_response,
         ):
        result = get_patient_guardian_by_nric(nric="S1234567Z", db=db_session_mock)

    assert result is mock_response


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


def test_assign_guardian_to_patient_success(db_session_mock, ppg_assign):
    mock_patient = MagicMock(id=1)
    mock_guardian = MagicMock(id=1)
    mock_relationship = MagicMock(id=1)
    mock_link = MagicMock(id=1, patientId=1, guardianId=1)

    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=mock_patient), \
         patch("app.routers.patient_guardian_router.crud_guardian.get_guardian", return_value=mock_guardian), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "get_patient_patient_guardian_by_guardianId_and_patientId",
             return_value=None,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_patients_for_guardian",
             return_value=0,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_guardians_for_patient",
             return_value=0,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_relationship.get_relationshipId_by_relationshipName",
             return_value=mock_relationship,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian.create_patient_patient_guardian",
             return_value=mock_link,
         ) as mock_create:

        result = assign_guardian_to_patient(ppg_assign, db_session_mock)

        assert result is mock_link
        mock_create.assert_called_once()


def test_assign_guardian_to_patient_patient_not_found(db_session_mock, ppg_assign):
    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            assign_guardian_to_patient(ppg_assign, db_session_mock)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient not found"


def test_assign_guardian_to_patient_guardian_not_found(db_session_mock, ppg_assign):
    mock_patient = MagicMock(id=1)

    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=mock_patient), \
         patch("app.routers.patient_guardian_router.crud_guardian.get_guardian", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            assign_guardian_to_patient(ppg_assign, db_session_mock)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Guardian not found"


def test_assign_guardian_to_patient_already_assigned(db_session_mock, ppg_assign):
    mock_patient = MagicMock(id=1)
    mock_guardian = MagicMock(id=1)
    mock_existing_link = MagicMock(id=1)

    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=mock_patient), \
         patch("app.routers.patient_guardian_router.crud_guardian.get_guardian", return_value=mock_guardian), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "get_patient_patient_guardian_by_guardianId_and_patientId",
             return_value=mock_existing_link,
         ):
        with pytest.raises(HTTPException) as exc_info:
            assign_guardian_to_patient(ppg_assign, db_session_mock)

    assert exc_info.value.status_code == 400
    assert "already assigned" in exc_info.value.detail


def test_assign_guardian_to_patient_relationship_not_found(db_session_mock, ppg_assign):
    mock_patient = MagicMock(id=1)
    mock_guardian = MagicMock(id=1)

    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=mock_patient), \
         patch("app.routers.patient_guardian_router.crud_guardian.get_guardian", return_value=mock_guardian), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "get_patient_patient_guardian_by_guardianId_and_patientId",
             return_value=None,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_patients_for_guardian",
             return_value=0,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_guardians_for_patient",
             return_value=0,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_relationship.get_relationshipId_by_relationshipName",
             return_value=None,
         ):
        with pytest.raises(HTTPException) as exc_info:
            assign_guardian_to_patient(ppg_assign, db_session_mock)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Relationship not found"


def test_assign_guardian_to_patient_at_max_capacity(db_session_mock, ppg_assign):
    """A guardian already linked to 2 active patients cannot be assigned a 3rd."""
    mock_patient = MagicMock(id=1)
    mock_guardian = MagicMock(id=1)

    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=mock_patient), \
         patch("app.routers.patient_guardian_router.crud_guardian.get_guardian", return_value=mock_guardian), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "get_patient_patient_guardian_by_guardianId_and_patientId",
             return_value=None,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_patients_for_guardian",
             return_value=2,
         ):
        with pytest.raises(HTTPException) as exc_info:
            assign_guardian_to_patient(ppg_assign, db_session_mock)

    assert exc_info.value.status_code == 400
    assert "maximum of 2 patients" in exc_info.value.detail


def test_assign_guardian_to_patient_at_max_guardians(db_session_mock, ppg_assign):
    """A patient already linked to 2 active guardians cannot be assigned a 3rd."""
    mock_patient = MagicMock(id=1)
    mock_guardian = MagicMock(id=1)

    with patch("app.routers.patient_guardian_router.crud_patient.get_patient", return_value=mock_patient), \
         patch("app.routers.patient_guardian_router.crud_guardian.get_guardian", return_value=mock_guardian), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "get_patient_patient_guardian_by_guardianId_and_patientId",
             return_value=None,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_patients_for_guardian",
             return_value=0,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_guardians_for_patient",
             return_value=2,
         ):
        with pytest.raises(HTTPException) as exc_info:
            assign_guardian_to_patient(ppg_assign, db_session_mock)

    assert exc_info.value.status_code == 400
    assert "maximum of 2 guardians" in exc_info.value.detail


def test_unassign_guardian_from_patient_success(db_session_mock):
    mock_link = MagicMock(id=1, patientId=1, guardianId=1)
    mock_deleted = MagicMock(id=1, isDeleted="1")

    with patch(
        "app.routers.patient_guardian_router.crud_patient_patient_guardian."
        "get_patient_patient_guardian_by_guardianId_and_patientId",
        return_value=mock_link,
    ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_guardians_for_patient",
             return_value=2,
         ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian.delete_relationship",
             return_value=mock_deleted,
         ) as mock_delete:

        result = unassign_guardian_from_patient(patient_id=1, guardian_id=1, db=db_session_mock)

        assert result is mock_deleted
        mock_delete.assert_called_once_with(db_session_mock, mock_link.id)


def test_unassign_guardian_from_patient_at_min_guardians(db_session_mock):
    mock_link = MagicMock(id=1, patientId=1, guardianId=1)

    with patch(
        "app.routers.patient_guardian_router.crud_patient_patient_guardian."
        "get_patient_patient_guardian_by_guardianId_and_patientId",
        return_value=mock_link,
    ), \
         patch(
             "app.routers.patient_guardian_router.crud_patient_patient_guardian."
             "count_active_guardians_for_patient",
             return_value=1,
         ):
        with pytest.raises(HTTPException) as exc_info:
            unassign_guardian_from_patient(patient_id=1, guardian_id=1, db=db_session_mock)

    assert exc_info.value.status_code == 400
    assert "at least" in exc_info.value.detail


def test_unassign_guardian_from_patient_not_found(db_session_mock):
    with patch(
        "app.routers.patient_guardian_router.crud_patient_patient_guardian."
        "get_patient_patient_guardian_by_guardianId_and_patientId",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            unassign_guardian_from_patient(patient_id=1, guardian_id=999, db=db_session_mock)

    assert exc_info.value.status_code == 404
    assert "No active guardian assignment found" in exc_info.value.detail


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def ppg_assign():
    return PatientPatientGuardianAssign(
        patientId=1,
        guardianId=1,
        relationshipName="Husband",
        CreatedById="1",
        ModifiedById="1",
    )


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
