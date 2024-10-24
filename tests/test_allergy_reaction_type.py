# test_allergy_reaction_type.py

import pytest
from unittest import mock
from app.crud.allergy_reaction_type_crud import create_reaction_type, get_all_reaction_types
from app.schemas.allergy_reaction_type import AllergyReactionTypeCreate
from app.models.allergy_reaction_type_model import AllergyReactionType

# Import your mock_db from tests/utils
from tests.utils.mock_db import get_db_session_mock

# Mocking the relevant models
@mock.patch("app.models.patient_model.Patient")
@mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
@mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
@mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")  # Mock PatientDoctorNote
@mock.patch("app.models.patient_photo_model.PatientPhoto")  # Mock PatientPhoto
@mock.patch("app.models.patient_assigned_dementia_model.PatientAssignedDementia")  # Mock PatientAssignedDementia
@mock.patch("app.models.patient_mobility_model.PatientMobility")  # Mock PatientMobility
@mock.patch("app.models.patient_prescription_model.PatientPrescription")  # Add this line to mock PatientPrescription
@mock.patch("app.models.patient_social_history_model.PatientSocialHistory")  
@mock.patch("app.models.patient_vital_model.PatientVital")  
@mock.patch("app.models.patient_highlight_model.PatientHighlight")  
@mock.patch("app.models.allergy_type_model.AllergyType")  
@mock.patch("app.models.patient_guardian_relationship_mapping_model.PatientGuardianRelationshipMapping")  
def test_create_reaction_type(
    mock_patient, 
    mock_patient_guardian, 
    mock_patient_allergy_mapping, 
    mock_patient_doctor_note, 
    mock_patient_photo,  # Add new mocks here
    mock_patient_assigned_dementia,  # Add new mocks here
    mock_patient_mobility,  # Add new mocks here
    mock_patient_prescription,  # Add this mock
    mock_patient_social_history,
    mock_patient_vital,
    mock_patient_highlight,
    mock_allery_type,
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
    assert result.Active == "1"
    assert result.createdById == created_by

def test_get_all_reaction_types(db_session_mock):
    """Test case for getting all allergy reaction types."""
    
    # Arrange
    db_session_mock.query.return_value.all.return_value = get_mock_allergy_reaction_types()

    # Act
    result = get_all_reaction_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Rashes"
    assert result[1].Value == "Sneezing"

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

@pytest.fixture
def allergy_reaction_type_create():
    """Fixture to provide a mock AllergyReactionTypeCreate object."""
    return AllergyReactionTypeCreate(Value="Mock 1", Active="1")

## MOCK DATA ##
def get_mock_allergy_reaction_types():
    """Return a list of mock AllergyReactionType objects."""
    return [
        AllergyReactionType(AllergyReactionTypeID=1, Value="Rashes", Active="1"),
        AllergyReactionType(AllergyReactionTypeID=2, Value="Sneezing", Active="1"),
    ]
