import pytest
from unittest import mock
from app.crud.patient_highlight_type_crud import (
    create_highlight_type,
    get_all_highlight_types,
    get_highlight_type_by_id,
    update_highlight_type,
    delete_highlight_type,
)
from app.schemas.patient_highlight_type import HighlightTypeCreate, HighlightTypeUpdate
from app.models.patient_highlight_type_model import HighlightType
from app.models.allergy_reaction_type_model import AllergyReactionType
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
from app.models.patient_doctor_note_model import PatientDoctorNote
from app.models.patient_photo_model import PatientPhoto
from app.models.patient_model import Patient
from app.models.patient_assigned_dementia_model import PatientAssignedDementia
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
from tests.utils.mock_db import get_db_session_mock


# Test: Create Highlight Type
def test_create_highlight_type(db_session_mock):
    """Test case for creating a highlight type."""
    # Arrange
    created_by = 1
    highlight_type_create = HighlightTypeCreate(Value="newPrescription", IsDeleted="0")

    # Act
    result = create_highlight_type(db_session_mock, highlight_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "newPrescription"
    assert result.IsDeleted == "0"
    assert result.CreatedById == created_by


# Test: Get All Highlight Types
def test_get_all_highlight_types(db_session_mock):
    """Test case for retrieving all highlight types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_highlight_types()

    # Act
    result = get_all_highlight_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "newPrescription"
    assert result[1].Value == "newAllergy"


# Test: Get Highlight Type by ID
def test_get_highlight_type_by_id(db_session_mock):
    """Test case for retrieving a highlight type by ID."""
    # Arrange
    mock_highlight_type = HighlightType(
        HighlightTypeID=1,
        Value="newPrescription",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    # Act
    result = get_highlight_type_by_id(db_session_mock, mock_highlight_type.HighlightTypeID)

    # Assert
    db_session_mock.query.assert_called_once_with(HighlightType)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.HighlightTypeID == mock_highlight_type.HighlightTypeID
    assert result.Value == mock_highlight_type.Value
    assert result.IsDeleted == mock_highlight_type.IsDeleted


# Test: Update Highlight Type
def test_update_highlight_type(db_session_mock):
    """Test case for updating a highlight type."""
    # Arrange
    modified_by = 2
    highlight_type_update = HighlightTypeUpdate(Value="updatedPrescription", IsDeleted="0")
    mock_highlight_type = HighlightType(
        HighlightTypeID=1,
        Value="newPrescription",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    # Act
    result = update_highlight_type(
        db_session_mock,
        mock_highlight_type.HighlightTypeID,
        highlight_type_update,
        modified_by,
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_highlight_type)
    assert result.Value == highlight_type_update.Value
    assert result.ModifiedById == modified_by


# Test: Delete Highlight Type
def test_delete_highlight_type(db_session_mock):
    """Test case for deleting (soft-deleting) a highlight type."""
    # Arrange
    modified_by = 2
    mock_highlight_type = HighlightType(
        HighlightTypeID=1,
        Value="newPrescription",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    # Act
    result = delete_highlight_type(
        db_session_mock, mock_highlight_type.HighlightTypeID, modified_by
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by


# Mock Fixtures
@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def highlight_type_create():
    """Fixture to provide a mock HighlightTypeCreate object."""
    return HighlightTypeCreate(Value="newPrescription", IsDeleted="0")


# Mock Data
def get_mock_highlight_types():
    """Return a list of mock HighlightType objects."""
    return [
        HighlightType(HighlightTypeID=1, Value="newPrescription", IsDeleted="0"),
        HighlightType(HighlightTypeID=2, Value="newAllergy", IsDeleted="0"),
    ]
