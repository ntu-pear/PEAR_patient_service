import pytest
from unittest import mock
from app.crud.allergy_type_crud import (
    create_allergy_type,
    get_all_allergy_types,
    get_allergy_type_by_id,
    update_allergy_type,
    delete_allergy_type,
)
from app.schemas.allergy_type import AllergyTypeCreate, AllergyTypeUpdate
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
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
from app.models.allergy_reaction_type_model import AllergyReactionType
from app.models.allergy_type_model import AllergyType
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_allergy_type(
    db_session_mock,
    allergy_type_create,
):
    """Test case for creating an allergy type."""
    # Arrange
    created_by = 1

    # Act
    result = create_allergy_type(db_session_mock, allergy_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Corn"
    assert result.IsDeleted == "0"
    assert result.CreatedById == created_by


def test_get_all_allergy_types(db_session_mock):
    """Test case for retrieving all allergy types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_allergy_types()

    # Act
    result = get_all_allergy_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Corn"
    assert result[1].Value == "Wheat"


def test_get_allergy_type_by_id(db_session_mock):
    """Test case for retrieving an allergy type by ID."""
    # Arrange
    mock_allergy_type = AllergyType(
        AllergyTypeID=1,
        Value="Corn",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_allergy_type
    )

    # Act
    result = get_allergy_type_by_id(db_session_mock, mock_allergy_type.AllergyTypeID)

    # Assert
    db_session_mock.query.assert_called_once_with(AllergyType)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.AllergyTypeID == mock_allergy_type.AllergyTypeID
    assert result.Value == mock_allergy_type.Value
    assert result.IsDeleted == mock_allergy_type.IsDeleted


def test_update_allergy_type(db_session_mock):
    """Test case for updating an allergy type."""
    # Arrange
    modified_by = 2
    allergy_type_update = AllergyTypeUpdate(Value="Updated Corn", IsDeleted="0")
    mock_allergy_type = AllergyType(
        AllergyTypeID=1,
        Value="Corn",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_allergy_type
    )

    # Act
    result = update_allergy_type(
        db_session_mock,
        mock_allergy_type.AllergyTypeID,
        allergy_type_update,
        modified_by,
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_allergy_type)
    assert result.Value == allergy_type_update.Value
    assert result.ModifiedById == modified_by


def test_delete_allergy_type(db_session_mock):
    """Test case for deleting (soft-deleting) an allergy type."""
    # Arrange
    modified_by = 2
    mock_allergy_type = AllergyType(
        AllergyTypeID=1,
        Value="Corn",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_allergy_type
    )

    # Act
    result = delete_allergy_type(
        db_session_mock, mock_allergy_type.AllergyTypeID, modified_by
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def allergy_type_create():
    """Fixture to provide a mock AllergyTypeCreate object."""
    return AllergyTypeCreate(Value="Corn", IsDeleted="0")


## MOCK DATA ##
def get_mock_allergy_types():
    """Return a list of mock AllergyType objects."""
    return [
        AllergyType(AllergyTypeID=1, Value="Corn", IsDeleted="0"),
        AllergyType(AllergyTypeID=2, Value="Wheat", IsDeleted="0"),
    ]
