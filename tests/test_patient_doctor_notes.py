import pytest
from unittest import mock
from tests.utils.mock_db import get_db_session_mock
from app.crud.patient_doctor_note_crud import create_doctor_note, update_doctor_note, delete_doctor_note, get_doctor_note_by_id
from app.schemas.patient_doctor_note import PatientDoctorNote, PatientDoctorNoteCreate, PatientDoctorNoteUpdate
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
from app.models.allergy_type_model import AllergyType
from app.models.allergy_reaction_type_model import AllergyReactionType
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_doctor_note_model import PatientDoctorNote
from app.models.patient_photo_model import PatientPhoto
from app.models.patient_photo_list_model import PatientPhotoList
from app.models.patient_model import Patient
from app.models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from app.models.patient_assigned_dementia_mapping_model import PatientAssignedDementiaMapping
from app.models.patient_mobility_list_model import PatientMobilityList
from app.models.patient_mobility_mapping_model import PatientMobility
from app.models.patient_prescription_model import PatientPrescription
from app.models.patient_social_history_model import PatientSocialHistory
from app.models.patient_vital_model import PatientVital
from app.models.patient_highlight_model import PatientHighlight
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
from datetime import datetime

def test_get_doctor_note_by_id(db_session_mock, mock_doctor_note):
    note_id = 1
    db_session_mock.query().filter().first.return_value = mock_doctor_note
    result = get_doctor_note_by_id(db_session_mock, note_id)

    assert result == mock_doctor_note

def test_create_doctor_note(db_session_mock, doctor_note_create):
    result = create_doctor_note(db_session_mock, doctor_note_create, "user", user_full_name="TEST_NAME")
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)

def test_update_doctor_note(db_session_mock, doctor_note_update):
    note_id = 1
    result = update_doctor_note(db_session_mock, note_id, doctor_note_update, "user", user_full_name="TEST_NAME")
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

@pytest.fixture
def doctor_note_create():
    return PatientDoctorNoteCreate(isDeleted='0', patientId=1, doctorId="1", doctorRemarks="Doctor Remarks", CreatedById="1" , ModifiedById="1")

@pytest.fixture
def doctor_note_update():
    return PatientDoctorNoteUpdate(isDeleted='0', patientId=1, doctorId="1", doctorRemarks="Doctor Remarks", ModifiedById="1")

@pytest.fixture
def mock_doctor_note():
    return PatientDoctorNote(id=1,isDeleted='0', patientId=1, doctorId="1", doctorRemarks="Doctor Remarks", CreatedById="1" , ModifiedById="1", createdDate=datetime.now(), modifiedDate=datetime.now())