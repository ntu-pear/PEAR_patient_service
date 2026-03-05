from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.crud.patient_guardian_crud import (
    create_guardian,
    delete_guardian,
    get_guardian,
    get_guardian_by_id_list,
    get_guardian_by_nric,
    update_guardian,
)
from app.models.patient_guardian_model import PatientGuardian
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.schemas.patient_guardian import PatientGuardianCreate, PatientGuardianUpdate
from tests.utils.mock_db import get_db_session_mock


def test_get_guardian(db_session_mock):
    """Test case for retrieving a guardian by ID."""
    mock_guardian = get_mock_patient_guardian()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    result = get_guardian(db_session_mock, 1)
    
    assert result == mock_guardian
    db_session_mock.query.assert_called_with(PatientGuardian)


def test_get_guardian_soft_deleted(db_session_mock):
    """Test that retrieving a soft-deleted guardian returns None."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    result = get_guardian(db_session_mock, 1)
    
    assert result is None


def test_get_guardian_inactive(db_session_mock):
    """Test that retrieving an inactive guardian returns None."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    result = get_guardian(db_session_mock, 1)
    
    assert result is None


def test_get_guardian_by_id_list(db_session_mock):
    """Test case for retrieving multiple guardians by a list of IDs."""
    mock_guardian_1 = get_mock_patient_guardian()
    mock_guardian_1.id = 1
    mock_guardian_2 = get_mock_patient_guardian()
    mock_guardian_2.id = 2
    mock_guardians = [mock_guardian_1, mock_guardian_2]
    
    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_guardians
    
    result = get_guardian_by_id_list(db_session_mock, [1, 2])
    
    assert len(result) == 2
    assert result == mock_guardians


def test_get_guardian_by_nric(db_session_mock):
    """Test case for retrieving a guardian by NRIC."""
    mock_guardian = get_mock_patient_guardian()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    result = get_guardian_by_nric(db_session_mock, "S1234567Z")
    
    assert result == mock_guardian


def test_create_guardian(db_session_mock):
    """Test case for creating a new guardian."""
    guardian_create = patient_guardian_create()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    with patch('app.crud.patient_guardian_crud.PatientGuardian') as mock_guardian_class:
        mock_guardian_class.return_value = mock_guardian
        
        result = create_guardian(db_session_mock, guardian_create)
        
        db_session_mock.add.assert_called_once_with(mock_guardian)
        db_session_mock.commit.assert_called_once()
        db_session_mock.refresh.assert_called_once_with(mock_guardian)
        assert result == mock_guardian


def test_update_guardian_success(db_session_mock):
    """Test case for successfully updating a guardian with valid relationship."""
    guardian_update = patient_guardian_update()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    mock_relationship = get_patient_guardian_relationship_mapping()
    mock_relationship.id = 1
    mock_relationship.relationshipName = "Husband"
    mock_relationship.isDeleted = "0"
    
    mock_patient_guardian_relationship = get_patient_patient_guardian()
    mock_patient_guardian_relationship.relationshipId = 1
    
    # 1. NRIC Patient check (returns None)
    # 2. Guardian fetch (returns mock_guardian)
    # 3. PatientGuardian relationship fetch (returns mock_patient_guardian_relationship)
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None,  
        mock_guardian,  
        mock_patient_guardian_relationship  
    ]
    
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        result = update_guardian(db_session_mock, 1, guardian_update)
        
        assert result == mock_guardian
        assert db_session_mock.commit.call_count >= 1
        assert db_session_mock.refresh.call_count >= 1


def test_update_guardian_not_found(db_session_mock):
    """Test case for updating a guardian that doesn't exist."""
    guardian_update = patient_guardian_update()
    
    # 1. NRIC Patient check (returns None)
    # 2. Guardian fetch (returns None -> triggers 404)
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None, 
        None  
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        update_guardian(db_session_mock, 999, guardian_update)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Guardian not found"


def test_update_guardian_invalid_relationship_name(db_session_mock):
    """Test case for updating guardian with invalid relationshipName."""
    guardian_update = patient_guardian_update()
    guardian_update.relationshipName = "InvalidRelationship"
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    # 1. NRIC Patient check (None)
    # 2. Guardian check (mock_guardian)
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None,  
        mock_guardian  
    ]
    
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            update_guardian(db_session_mock, 1, guardian_update)
        
        assert exc_info.value.status_code == 400
        assert "Invalid relationshipName" in exc_info.value.detail


def test_update_guardian_inactive_relationship(db_session_mock):
    """Test case for updating guardian with inactive relationshipName."""
    guardian_update = patient_guardian_update()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    # 1. NRIC Patient check (None)
    # 2. Guardian check (mock_guardian)
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None, 
        mock_guardian 
    ]
    
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            update_guardian(db_session_mock, 1, guardian_update)
        
        assert exc_info.value.status_code == 400
        assert "Invalid relationshipName" in exc_info.value.detail


def test_update_guardian_no_patient_relationship(db_session_mock):
    """Test case for updating guardian when no patient-guardian relationship exists."""
    guardian_update = patient_guardian_update()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    mock_relationship = get_patient_guardian_relationship_mapping()
    mock_relationship.isDeleted = "0"
    
    # 1. Patient check (None)
    # 2. Guardian fetch (mock_guardian)
    # 3. Relationship fetch (None)
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None,  
        mock_guardian,  
        None  
    ]
    
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        with pytest.raises(HTTPException) as exc_info:
            update_guardian(db_session_mock, 1, guardian_update)
        
        assert exc_info.value.status_code == 404
        assert "No relationship found" in exc_info.value.detail


def test_update_guardian_relationship_changed(db_session_mock):
    """Test case for updating guardian when relationship type changes."""
    guardian_update = patient_guardian_update()
    guardian_update.relationshipName = "Wife"
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    mock_relationship = get_patient_guardian_relationship_mapping()
    mock_relationship.id = 2
    mock_relationship.relationshipName = "Wife"
    mock_relationship.isDeleted = "0"
    
    mock_patient_guardian_relationship = get_patient_patient_guardian()
    mock_patient_guardian_relationship.relationshipId = 1
    
    # Sequence: 1. Patient NRIC check, 2. Guardian Check, 3. Relationship check
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None, 
        mock_guardian,  
        mock_patient_guardian_relationship  
    ]
    
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        result = update_guardian(db_session_mock, 1, guardian_update)
        
        assert result == mock_guardian
        assert mock_patient_guardian_relationship.relationshipId == 2
        assert db_session_mock.commit.call_count >= 1


def test_delete_guardian(db_session_mock):
    """Test case for soft deleting a guardian."""
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    mock_guardian.isDeleted = "0"
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    result = delete_guardian(db_session_mock, 1)
    
    assert result.isDeleted == "1"
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_guardian)


def test_delete_guardian_not_found(db_session_mock):
    """Test case for deleting a guardian that doesn't exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    result = delete_guardian(db_session_mock, 999)
    
    assert result is None
    db_session_mock.commit.assert_not_called()


def test_create_guardian_nric_match_patient_nric(db_session_mock):
    """Test that creating a guardian with the same NRIC as the patient raises a 400 error."""
    guardian_create = patient_guardian_create()
    guardian_create.nric = "S1234567A"
    
    mock_patient = MagicMock()
    mock_patient.nric = "S1234567A"
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_patient
    
    with pytest.raises(HTTPException) as exc_info:
        create_guardian(db_session_mock, guardian_create)
        
    assert exc_info.value.status_code == 400
    assert "Guardian NRIC cannot match the Patient's NRIC" in exc_info.value.detail


def test_update_guardian_nric_match_patient_nric(db_session_mock):
    """Test that updating a guardian to have the same NRIC as the patient raises a 400 error."""
    guardian_update = patient_guardian_update()
    guardian_update.nric = "S1234567A"
    
    mock_patient = MagicMock()
    mock_patient.nric = "S1234567A"
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_patient
    
    with pytest.raises(HTTPException) as exc_info:
        update_guardian(db_session_mock, 1, guardian_update)
        
    assert exc_info.value.status_code == 400
    assert "Guardian NRIC cannot match the Patient's NRIC" in exc_info.value.detail


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def get_mock_patient_guardian():
    """Return a mock PatientGuardian object."""
    return PatientGuardian(
        id=1,
        active="Y",
        firstName="Test",
        lastName="TestLastName",
        preferredName="Test",
        gender="M",
        contactNo="91234567",
        nric="S1234567Z",
        email="test@test.com",
        dateOfBirth=datetime.strptime("2024-10-23 15:45:30", "%Y-%m-%d %H:%M:%S"),
        address="123",
        tempAddress="123",
        status="Y",
        isDeleted="0",
        guardianApplicationUserId="B22698B8-42A2-4115-9631-1C2D1E2AC5F5",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )


def patient_guardian_update():
    return PatientGuardianUpdate(
        active="Y",
        firstName="Test",
        lastName="TestLastName",
        preferredName="Test",
        gender="M",
        contactNo="91234567",
        nric="S1234567Z",
        email="test@test.com",
        dateOfBirth=datetime.strptime("2024-10-23 15:45:30", "%Y-%m-%d %H:%M:%S"),
        address="123",
        tempAddress="123",
        status="Y",
        isDeleted="0",
        guardianApplicationUserId="B22698B8-42A2-4115-9631-1C2D1E2AC5F5",
        modifiedDate=datetime.now(),
        ModifiedById="1",
        patientId=1,
        relationshipName="Husband",
    )


def patient_guardian_create():
    return PatientGuardianCreate(
        active="Y",
        firstName="Test",
        lastName="TestLastName",
        preferredName="Test",
        gender="M",
        contactNo="91234567",
        nric="S1234567Z",
        email="test@test.com",
        dateOfBirth=datetime.strptime("2024-10-23 15:45:30", "%Y-%m-%d %H:%M:%S"),
        address="123",
        tempAddress="123",
        status="Y",
        isDeleted="0",
        guardianApplicationUserId="B22698B8-42A2-4115-9631-1C2D1E2AC5F5",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
        patientId=1,
        relationshipName="Husband",
    )


def get_patient_patient_guardian():
    return PatientPatientGuardian(
        id=1,
        patientId=1,
        guardianId=1,
        relationshipId=1,
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
        isDeleted="0",
    )


def get_patient_guardian_relationship_mapping():
    return PatientGuardianRelationshipMapping(
        id=1,
        isDeleted="0",
        relationshipName="Husband",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )

def test_create_guardian_nric_matches_active_patient(db_session_mock):
    """Should fail if NRIC matches an active patient."""
    from app.models.patient_model import Patient
    guardian_create = patient_guardian_create() # NRIC: S1234567Z
    
    mock_patient = MagicMock(spec=Patient)
    mock_patient.nric = "S1234567Z"
    mock_patient.isDeleted = "0"
    
    # Mocking the NRIC check query
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_patient
    
    with pytest.raises(HTTPException) as exc_info:
        create_guardian(db_session_mock, guardian_create)
    assert exc_info.value.status_code == 400

def test_create_guardian_nric_matches_deleted_patient(db_session_mock):
    """Should pass if the patient with matching NRIC is soft-deleted."""
    guardian_create = patient_guardian_create()
    
    # Query returns None because Patient.isDeleted == "0" filter excludes the deleted record
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    with patch('app.crud.patient_guardian_crud.PatientGuardian') as mock_guardian_class:
        mock_guardian_class.return_value = get_mock_patient_guardian()
        result = create_guardian(db_session_mock, guardian_create)
        assert result is not None
        db_session_mock.commit.assert_called_once()