import pytest
from unittest.mock import MagicMock
from app.crud.patient_highlight_crud import (
    get_all_highlights,
    get_highlights_by_patient,
    create_highlight,
    update_highlight,
    delete_highlight,
)
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
from app.models.allergy_type_model import AllergyType
from app.models.allergy_reaction_type_model import AllergyReactionType
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
from app.models.patient_highlight_type_model import PatientHighlightType
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
# ADD Problem model imports
from app.models.patient_problem_list_model import PatientProblemList
from app.models.patient_problem_model import PatientProblem

from app.schemas.patient_highlight import PatientHighlightCreate, PatientHighlightUpdate
from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


def test_get_all_highlights(db_session_mock):
    """Test case for retrieving all patient highlights."""
    # Arrange - NEW V3 Schema
    mock_data = [
        MagicMock(
            Id=1,
            PatientId=1,
            HighlightTypeId=1,
            HighlightText="Allergy: Shellfish",
            SourceTable="PATIENT_ALLERGY_MAPPING",
            SourceRecordId=101,
            IsDeleted=0,
            CreatedDate=datetime.now(),
            ModifiedDate=datetime.now(),
            CreatedById="2",
            ModifiedById="2",
        ),
        MagicMock(
            Id=2,
            PatientId=2,
            HighlightTypeId=2,
            HighlightText="High BP: 180/110 mmHg",
            SourceTable="PATIENT_VITAL",
            SourceRecordId=202,
            IsDeleted=0,
            CreatedDate=datetime.now(),
            ModifiedDate=datetime.now(),
            CreatedById="2",
            ModifiedById="2",
        ),
    ]
    db_session_mock.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = mock_data

    # Act
    result = get_all_highlights(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].HighlightText == "Allergy: Shellfish"
    assert result[1].HighlightText == "High BP: 180/110 mmHg"


def test_get_highlights_by_patient(db_session_mock):
    """Test case for retrieving highlights for a specific patient."""
    # Arrange
    patient_id = 1
    mock_data = [
        MagicMock(
            Id=1,
            PatientId=patient_id,
            HighlightTypeId=1,
            HighlightText="Allergy: Shellfish",
            SourceTable="PATIENT_ALLERGY_MAPPING",
            SourceRecordId=101,
            IsDeleted=0,
            CreatedDate=datetime.now(),
            ModifiedDate=datetime.now(),
            CreatedById="2",
            ModifiedById="2",
        )
    ]
    db_session_mock.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = mock_data

    # Act
    result = get_highlights_by_patient(db_session_mock, patient_id)

    # Assert
    assert len(result) == 1
    assert result[0].PatientId == patient_id
    assert result[0].HighlightText == "Allergy: Shellfish"


def test_create_highlight(db_session_mock, patient_highlight_create):
    """Test case for creating a new patient highlight."""
    # Arrange
    created_by = "1"

    # Act
    result = create_highlight(db_session_mock, patient_highlight_create, created_by, "USER")

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.PatientId == patient_highlight_create.PatientId
    assert result.HighlightTypeId == patient_highlight_create.HighlightTypeId
    assert result.HighlightText == patient_highlight_create.HighlightText


def test_update_highlight(db_session_mock, patient_highlight_update):
    """Test case for updating a patient highlight."""
    # Arrange
    modified_by = "2"
    # NEW V3 Schema - use mock instead of instantiating model
    mock_highlight = MagicMock(
        Id=1,
        PatientId=1,
        HighlightTypeId=1,
        HighlightText="Allergy: Shellfish",
        SourceTable="PATIENT_ALLERGY_MAPPING",
        SourceRecordId=101,
        IsDeleted=0,
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight
    )

    # Act
    result = update_highlight(
        db_session_mock, mock_highlight.Id, patient_highlight_update, modified_by, "USER"
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_highlight)
    assert result.HighlightText == patient_highlight_update.HighlightText
    assert result.ModifiedById == modified_by


def test_delete_highlight(db_session_mock):
    """Test case for deleting (soft-deleting) a patient highlight."""
    # Arrange
    modified_by = "2"
    mock_highlight = MagicMock(
        Id=1,
        PatientId=1,
        HighlightTypeId=1,
        HighlightText="Allergy: Shellfish",
        SourceTable="PATIENT_ALLERGY_MAPPING",
        SourceRecordId=101,
        IsDeleted=0,
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight
    )
    
    # Act
    result = delete_highlight(db_session_mock, mock_highlight.Id, modified_by, "USER")
    
    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def patient_highlight_create():
    """Fixture to provide a mock PatientHighlightCreate object."""
    # NEW V3 Schema
    return PatientHighlightCreate(
        PatientId=1,
        HighlightTypeId=1,
        HighlightText="Allergy: Shellfish",
        SourceTable="PATIENT_ALLERGY_MAPPING",
        SourceRecordId=101
    )


@pytest.fixture
def patient_highlight_update():
    """Fixture to provide a mock PatientHighlightUpdate object."""
    # NEW V3 Schema
    return PatientHighlightUpdate(
        HighlightText="Allergy: Shellfish (Updated)"
    )