# test_allergy_reaction_type.py

import pytest
from unittest import mock
from app.crud.allergy_reaction_type_crud import create_reaction_type, get_all_reaction_types, update_reaction_type,delete_reaction_type,get_reaction_type_by_id
from app.schemas.allergy_reaction_type import AllergyReactionTypeCreate,AllergyReactionTypeUpdate
from app.models.allergy_reaction_type_model import AllergyReactionType
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
from app.models.patient_doctor_note_model import PatientDoctorNote
from app.models.patient_photo_model import PatientPhoto
from app.models.patient_model import Patient
from app.models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from app.models.patient_assigned_dementia_mapping_model import PatientAssignedDementiaMapping
from app.models.patient_mobility_model import PatientMobility
from app.models.patient_prescription_model import PatientPrescription
from app.models.patient_social_history_model import PatientSocialHistory
from app.models.patient_vital_model import PatientVital
from app.models.patient_highlight_model import PatientHighlight
from app.models.allergy_type_model import AllergyType
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
from datetime import datetime
# Import your mock_db from tests/utils
from tests.utils.mock_db import get_db_session_mock

# Mocking the relevant models

def test_create_reaction_type(
    db_session_mock, 
    allergy_reaction_type_create
):
    """Test case for creating an allergy reaction type."""
    
    # Arrange
    created_by = 1

    # Act
    result = create_reaction_type(db_session_mock, allergy_reaction_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Mock 1"
    assert result.IsDeleted == "0"
    assert result.CreatedById == created_by

def test_get_all_reaction_types(db_session_mock):
    """Test case for getting all allergy reaction types."""
    
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_allergy_reaction_types() 

    # Act
    result = get_all_reaction_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Rashes"
    assert result[1].Value == "Sneezing"

def test_get_reaction_type_by_id(db_session_mock):
    """Test case for retrieving an allergy reaction type by ID."""
    # Arrange
    mock_reaction_type = AllergyReactionType(
        AllergyReactionTypeID=1,
        Value="Mock 1",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_reaction_type

    # Act
    result = get_reaction_type_by_id(db_session_mock, mock_reaction_type.AllergyReactionTypeID)

    # Assert
    db_session_mock.query.assert_called_once_with(AllergyReactionType)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.AllergyReactionTypeID == mock_reaction_type.AllergyReactionTypeID
    assert result.Value == mock_reaction_type.Value
    assert result.IsDeleted == mock_reaction_type.IsDeleted


def test_update_reaction_type(db_session_mock, allergy_reaction_type_create):
    """Test case for updating an allergy reaction type."""
    # Arrange
    modified_by = 2
    allergy_reaction_type_update = AllergyReactionTypeUpdate(Value="Updated Reaction", IsDeleted="0")
    mock_reaction_type = AllergyReactionType(
        AllergyReactionTypeID=1,
        Value="Mock 1",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_reaction_type

    # Act
    result = update_reaction_type(db_session_mock, mock_reaction_type.AllergyReactionTypeID, allergy_reaction_type_update, modified_by)

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_reaction_type)
    assert result.Value == allergy_reaction_type_update.Value
    assert result.ModifiedById == modified_by


def test_delete_reaction_type(db_session_mock):
    """Test case for deleting (soft-deleting) an allergy reaction type."""
    # Arrange
    modified_by = 2
    mock_reaction_type = AllergyReactionType(
        AllergyReactionTypeID=1,
        Value="Mock 1",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_reaction_type

    # Act
    result = delete_reaction_type(db_session_mock, mock_reaction_type.AllergyReactionTypeID, modified_by)

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

@pytest.fixture
def allergy_reaction_type_create():
    """Fixture to provide a mock AllergyReactionTypeCreate object."""
    return AllergyReactionTypeCreate(Value="Mock 1", IsDeleted="0")

## MOCK DATA ##
def get_mock_allergy_reaction_types():
    """Return a list of mock AllergyReactionType objects."""
    return [
        AllergyReactionType(AllergyReactionTypeID=1, Value="Rashes", IsDeleted="0"),
        AllergyReactionType(AllergyReactionTypeID=2, Value="Sneezing", IsDeleted="0"),
    ]
