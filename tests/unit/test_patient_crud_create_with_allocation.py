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
        guardianRelationshipName="Husband",
    )


def _setup_nric_clean(db):
    """NRIC checks pass (no conflicts)."""
    db.query.return_value.filter.return_value.first.return_value = None


@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_happy_path_auto_assign(mock_least, mock_outbox, mock_log, mock_rel, mock_count, mock_link, db, patient_data):
    mock_least.side_effect = lambda role, db_, api_key: {
        "DOCTOR": "D001", "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_explicit_ids_skip_user_service(mock_least, mock_outbox, mock_log, mock_rel, mock_count, mock_link, db, patient_data):
    patient_data.doctorId = "D_EXPLICIT"
    patient_data.gameTherapistId = "GT_EXPLICIT"
    patient_data.caregiverId = "CG_EXPLICIT"
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_partial_explicit_ids(mock_least, mock_outbox, mock_log, mock_rel, mock_count, mock_link, db, patient_data):
    patient_data.doctorId = "D_EXPLICIT"

    mock_least.side_effect = lambda role, db_, api_key: {
        "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
def test_doctor2_same_as_doctor(mock_rel, mock_count, db, patient_data):
    patient_data.doctorId = "D001"
    patient_data.doctor2Id = "D001"
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
def test_supervisor2_same_as_supervisor(mock_rel, mock_count, db, patient_data):
    patient_data.supervisor2Id = "SUP1"
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
def test_guardian_not_found(mock_rel, db, patient_data):
    mock_rel.return_value = MagicMock(id=1)
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


def test_guardian_relationship_name_required(db, patient_data):
    """guardianId without guardianRelationshipName is rejected before touching the DB."""
    patient_data.guardianRelationshipName = None
    _setup_nric_clean(db)

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 400
    assert "guardianRelationshipName" in exc.value.detail


def test_guardian_id_and_new_guardian_mutually_exclusive(db, patient_data):
    from app.schemas.patient import NewGuardianInline
    patient_data.newGuardian = NewGuardianInline(
        firstName="New", lastName="Guardian", contactNo="91234567",
        nric="S7654321B", dateOfBirth=datetime(1970, 1, 1),
    )
    _setup_nric_clean(db)

    from app.crud.patient_crud import create_patient
    with pytest.raises(HTTPException) as exc:
        create_patient(
            db, patient_data, user="SUP1", user_full_name="Supervisor",
            api_key="key", supervisor_id="SUP1"
        )
    assert exc.value.status_code == 400
    assert "not both" in exc.value.detail


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
@patch("app.crud.patient_crud.crud_guardian.create_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
def test_create_patient_with_new_guardian_inline(
    mock_rel, mock_link, mock_create_guardian, mock_least, mock_outbox, mock_log, db, patient_data
):
    """guardianId omitted, newGuardian given: guardian record + junction link created in the same call."""
    from app.schemas.patient import NewGuardianInline
    patient_data.guardianId = None
    patient_data.newGuardian = NewGuardianInline(
        firstName="New", lastName="Guardian", contactNo="91234567",
        nric="S7654321B", dateOfBirth=datetime(1970, 1, 1),
    )

    mock_rel.return_value = MagicMock(id=1)
    mock_least.side_effect = lambda role, db_, api_key: {
        "DOCTOR": "D001", "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]
    mock_create_guardian.return_value = MagicMock(id=77)

    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None,              # NRIC check (patient)
        None,              # NRIC check (guardian conflict)
        new_patient_mock,  # get new_patient after insert
    ]
    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    from app.crud.patient_crud import create_patient
    create_patient(
        db, patient_data, user="SUP1", user_full_name="Supervisor",
        api_key="key", supervisor_id="SUP1"
    )

    mock_create_guardian.assert_called_once()
    assert mock_create_guardian.call_args.kwargs.get("commit") is False
    mock_link.assert_called_once()
    linked_guardian_id = mock_link.call_args.args[1].guardianId
    assert linked_guardian_id == 77


@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_create_patient_without_guardian_skips_allocation(mock_least, mock_outbox, mock_log, db, patient_data):
    """Staff still auto-assigns with no guardian, but no PatientAllocation row is created
    (PATIENT_ALLOCATION.guardianId is NOT NULL) - guardian can be attached later via /Guardian/assign."""
    patient_data.guardianId = None

    mock_least.side_effect = lambda role, db_, api_key: {
        "DOCTOR": "D001", "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]

    new_patient_mock = MagicMock(id=42, nric="S1234567A")
    db.query.return_value.filter.return_value.first.side_effect = [
        None,              # NRIC check (patient)
        None,              # NRIC check (guardian conflict)
        new_patient_mock,  # get new_patient after insert
    ]

    mock_outbox.return_value.create_event.return_value = MagicMock(id=99)

    from app.crud.patient_crud import create_patient
    result = create_patient(
        db, patient_data, user="SUP1", user_full_name="Supervisor",
        api_key="key", supervisor_id="SUP1"
    )

    mock_least.assert_called()
    db.commit.assert_called_once()
    for add_call in db.add.call_args_list:
        assert add_call.args[0].__class__.__name__ != "PatientAllocation"


@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_user_service_unreachable_raises_503(mock_least, mock_outbox, mock_log, mock_rel, mock_count, mock_link, db, patient_data):
    mock_least.side_effect = HTTPException(status_code=503, detail="unreachable")
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_allocation_insert_fail_rolls_back(mock_least, mock_outbox, mock_log, mock_rel, mock_count, mock_link, db, patient_data):
    mock_least.side_effect = lambda role, db_, api_key: "X001"
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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


@patch("app.crud.patient_crud.crud_patient_patient_guardian.create_patient_patient_guardian")
@patch("app.crud.patient_crud.crud_patient_patient_guardian.count_active_patients_for_guardian")
@patch("app.crud.patient_crud.crud_relationship.get_relationshipId_by_relationshipName")
@patch("app.crud.patient_crud.log_crud_action")
@patch("app.crud.patient_crud.get_outbox_service")
@patch("app.crud.patient_crud.get_least_loaded_staff")
def test_doctor2_same_as_auto_assigned_doctor(mock_least, mock_outbox, mock_log, mock_rel, mock_count, mock_link, db, patient_data):
    patient_data.doctor2Id = "D001"
    mock_least.side_effect = lambda role, db_, api_key: {
        "DOCTOR": "D001", "GAME THERAPIST": "GT001", "CAREGIVER": "CG001"
    }[role]
    mock_rel.return_value = MagicMock(id=1)
    mock_count.return_value = 0

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
