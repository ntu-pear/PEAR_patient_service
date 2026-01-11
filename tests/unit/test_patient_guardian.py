import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.crud.patient_guardian_crud import (
    get_guardian,
    get_guardian_by_id_list,
    get_guardian_by_nric,
    create_guardian,
    update_guardian,
    delete_guardian,
)
from app.schemas.patient_guardian import PatientGuardianCreate, PatientGuardianUpdate
from app.models.patient_guardian_model import PatientGuardian
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


def test_get_guardian(db_session_mock):
    """Test case for retrieving a guardian by ID."""
    mock_guardian = get_mock_patient_guardian()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    result = get_guardian(db_session_mock, 1)
    
    assert result == mock_guardian
    db_session_mock.query.assert_called_once_with(PatientGuardian)


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
    db_session_mock.query.assert_called_once_with(PatientGuardian)


def test_get_guardian_by_nric(db_session_mock):
    """Test case for retrieving a guardian by NRIC."""
    mock_guardian = get_mock_patient_guardian()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    result = get_guardian_by_nric(db_session_mock, "S1234567Z")
    
    assert result == mock_guardian
    db_session_mock.query.assert_called_once_with(PatientGuardian)


def test_create_guardian(db_session_mock):
    """Test case for creating a new guardian."""
    guardian_create = patient_guardian_create()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    # Mocking the PatientGuardian instantiation
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
    
    # Mock the query for guardian
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_guardian,  # First call: get guardian
        mock_patient_guardian_relationship  # Second call: get patient_guardian relationship
    ]
    
    # Mock the relationship mapping lookup
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        result = update_guardian(db_session_mock, 1, guardian_update)
        
        assert result == mock_guardian
        assert db_session_mock.commit.call_count >= 1
        assert db_session_mock.refresh.call_count >= 1


def test_update_guardian_not_found(db_session_mock):
    """Test case for updating a guardian that doesn't exist."""
    guardian_update = patient_guardian_update()
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
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
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    # Mock the relationship mapping lookup to return None (invalid)
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_guardian(db_session_mock, 1, guardian_update)
        
        assert exc_info.value.status_code == 400
        assert "Invalid relationshipName" in exc_info.value.detail
        assert "InvalidRelationship" in exc_info.value.detail


def test_update_guardian_inactive_relationship(db_session_mock):
    """Test case for updating guardian with inactive relationshipName."""
    guardian_update = patient_guardian_update()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    mock_relationship = get_patient_guardian_relationship_mapping()
    mock_relationship.isDeleted = "1"  # Inactive relationship
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_guardian
    
    # Mock the relationship mapping lookup
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        with pytest.raises(HTTPException) as exc_info:
            update_guardian(db_session_mock, 1, guardian_update)
        
        assert exc_info.value.status_code == 400
        assert "Inactive relationshipName" in exc_info.value.detail


def test_update_guardian_no_patient_relationship(db_session_mock):
    """Test case for updating guardian when no patient-guardian relationship exists."""
    guardian_update = patient_guardian_update()
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    mock_relationship = get_patient_guardian_relationship_mapping()
    mock_relationship.isDeleted = "0"
    
    # Mock guardian exists, but patient-guardian relationship doesn't
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_guardian,  # First call: get guardian
        None  # Second call: get patient_guardian relationship (not found)
    ]
    
    # Mock the relationship mapping lookup
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_guardian(db_session_mock, 1, guardian_update)
        
        assert exc_info.value.status_code == 404
        assert "No relationship found between guardian" in exc_info.value.detail


def test_update_guardian_relationship_changed(db_session_mock):
    """Test case for updating guardian when relationship type changes."""
    guardian_update = patient_guardian_update()
    guardian_update.relationshipName = "Wife"  # Changed from "Husband"
    mock_guardian = get_mock_patient_guardian()
    mock_guardian.id = 1
    
    mock_relationship = get_patient_guardian_relationship_mapping()
    mock_relationship.id = 2  # Different relationship ID
    mock_relationship.relationshipName = "Wife"
    mock_relationship.isDeleted = "0"
    
    mock_patient_guardian_relationship = get_patient_patient_guardian()
    mock_patient_guardian_relationship.relationshipId = 1  # Old relationship ID
    
    # Mock queries
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_guardian,  # First call: get guardian
        mock_patient_guardian_relationship  # Second call: get patient_guardian relationship
    ]
    
    # Mock the relationship mapping lookup
    with patch('app.crud.patient_guardian_crud.patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName') as mock_get_relationship:
        mock_get_relationship.return_value = mock_relationship
        
        result = update_guardian(db_session_mock, 1, guardian_update)
        
        assert result == mock_guardian
        assert mock_patient_guardian_relationship.relationshipId == 2
        # Should commit twice: once for guardian, once for relationship
        assert db_session_mock.commit.call_count == 2


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