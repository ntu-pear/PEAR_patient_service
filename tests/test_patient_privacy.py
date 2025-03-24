import pytest
from unittest import mock
from datetime import datetime
from app.crud.patient_privacy_level_crud import get_privacy_level_by_patient, get_privacy_levels_by_patient, create_patient_privacy_level, update_patient_privacy_level, delete_patient_privacy_level
from app.schemas.patient_privacy_level import PatientPrivacyLevelCreate, PatientPrivacyLevelUpdate, PatientPrivacyLevel
from app.models.patient_privacy_level_model import PatientPrivacyLevel as PatientPrivacyLevelModel, PrivacyStatus

from fastapi import HTTPException, status

from tests.utils.mock_db import get_db_session_mock

def test_get_privacy_level_by_patient(db_session_mock, Read_Privacy_Level):
    """Test case for retrieving privacy level setting by ID."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.first.return_value = Read_Privacy_Level

    # Act
    result = get_privacy_level_by_patient(db_session_mock, Read_Privacy_Level.patientId)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientPrivacyLevelModel)
    db_session_mock.query.return_value.filter.assert_called_once()
    
    assert result.patientId == Read_Privacy_Level.patientId
    assert result.active == Read_Privacy_Level.active
    assert result.privacyLevelSensitive == Read_Privacy_Level.privacyLevelSensitive
    
def test_get_privacy_levels_by_patient(db_session_mock, Read_Privacy_Levels):
    """Test case for retrieving all privacy level settings by User"""
    # Arrange
    db_session_mock.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = Read_Privacy_Levels

    # Act
    result = get_privacy_levels_by_patient(db_session_mock)

    # Assert
    assert len(result) == len(Read_Privacy_Levels)
    assert result[0].patientId == Read_Privacy_Levels[0].patientId
    assert result[0].privacyLevelSensitive == Read_Privacy_Levels[0].privacyLevelSensitive
    assert result[1].patientId == Read_Privacy_Levels[1].patientId
    assert result[1].privacyLevelSensitive == Read_Privacy_Levels[1].privacyLevelSensitive
    
def test_create_patient_privacy_level(db_session_mock, Create_Privacy_Level):
    """Test Case for creating Privacy Level"""
    # Arrange
    patient_id = 1
    
    # Act
    result = create_patient_privacy_level(db_session_mock, patient_id, Create_Privacy_Level, 1)
    
    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)

    assert result.patientId == 1
    assert result.active == 1
    assert result.privacyLevelSensitive == PrivacyStatus.LOW
    
def test_update_patient_privacy_level(db_session_mock, Read_Privacy_Level, Update_Privacy_Level):
    """Test Case for updating Privacy Level"""

    # Arrange
    modified_by = 2
    mock_patient = Read_Privacy_Level
    mock_patient_id = Read_Privacy_Level.patientId
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_patient
    
    # Act
    result = update_patient_privacy_level(db_session_mock, mock_patient_id, Update_Privacy_Level, modified_by)
    
    #Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)

    assert result.active == 1
    assert result.privacyLevelSensitive == PrivacyStatus.LOW
    
def test_delete_patient_privacy_level(db_session_mock, Read_Privacy_Level):
    """Test case for deleting Privacy Level."""
    # Arrange
    mock_patient_id = Read_Privacy_Level.patientId
    db_session_mock.query.return_value.filter.return_value.first.return_value = Read_Privacy_Level
    
    # Act
    result = delete_patient_privacy_level(db_session_mock, mock_patient_id)
    
    #Assert
    assert result.patientId == mock_patient_id
    
@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

@pytest.fixture
def Read_Privacy_Level():
    """Fixture to provide a mock PatientPrivacyLevel Object."""
    return PatientPrivacyLevel(
        patientId=1,
        active=1,
        privacyLevelSensitive=1,
        createdById="1",
        modifiedById="1",
        createdDate=datetime.now(),
        modifiedDate=datetime.now()
    )

@pytest.fixture
def Read_Privacy_Levels():
    """Fixture to provide a list of mock PatientPrivacyLevel Objects."""
    return [
        PatientPrivacyLevel(
            patientId=1,
            active=1,
            privacyLevelSensitive=1,
            createdDate=datetime.now(),
            modifiedDate=datetime.now(),
            createdById="1",
            modifiedById="1"
        ),
        PatientPrivacyLevel(
            patientId=2,
            active=1,
            privacyLevelSensitive=2,
            createdDate=datetime.now(),
            modifiedDate=datetime.now(),
            createdById="1",
            modifiedById="1"
        )
    ]

@pytest.fixture
def Create_Privacy_Level():
    """Fixture to provide a mock PatientPrivacyLevelCreate Object."""
    return PatientPrivacyLevelCreate(
        active=1,
        privacyLevelSensitive=1
    )

@pytest.fixture
def Update_Privacy_Level():
    """Fixture to provide a mock PatientPrivacyLevelUpdate Object."""
    return PatientPrivacyLevelUpdate(
        active=1,
        privacyLevelSensitive=1
    )