import pytest
from unittest import mock
from tests.utils.mock_db import get_db_session_mock
from app.crud.patient_doctor_note_crud import create_doctor_note, update_doctor_note, delete_doctor_note, get_doctor_note_by_id
from app.schemas.patient_doctor_note import PatientDoctorNote, PatientDoctorNoteCreate, PatientDoctorNoteUpdate
from datetime import datetime

def test_get_doctor_note_by_id(db_session_mock, mock_doctor_note):
    note_id = 1
    db_session_mock.query().filter().first.return_value = mock_doctor_note
    result = get_doctor_note_by_id(db_session_mock, note_id)

    assert result == mock_doctor_note



def test_create_doctor_note(db_session_mock, doctor_note_create):
    result = create_doctor_note(db_session_mock, doctor_note_create)
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    
def test_update_doctor_note(db_session_mock, doctor_note_update):
    note_id = 1
    result = update_doctor_note(db_session_mock, note_id, doctor_note_update)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

@pytest.fixture
def doctor_note_create():
    return PatientDoctorNoteCreate(isDeleted='0', patientId=1, doctorId=1, doctorRemarks="Doctor Remarks", createdById=1 , modifiedById=1)

@pytest.fixture
def doctor_note_update():
    return PatientDoctorNoteUpdate(isDeleted='0', patientId=1, doctorId=1, doctorRemarks="Doctor Remarks", modifiedById=1)

@pytest.fixture
def mock_doctor_note():
    return PatientDoctorNote(id=1,isDeleted='0', patientId=1, doctorId=1, doctorRemarks="Doctor Remarks", createdById=1 , modifiedById=1, createdDate=datetime.now(), modifiedDate=datetime.now())