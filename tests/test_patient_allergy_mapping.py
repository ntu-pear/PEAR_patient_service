import pytest
from unittest.mock import MagicMock
from app.crud.patient_allergy_mapping_crud import (
    get_all_allergies,
    get_patient_allergies,
    create_patient_allergy,
    update_patient_allergy,
    delete_patient_allergy,
)
from app.schemas.patient_allergy_mapping import (
    PatientAllergyCreate,
    PatientAllergyUpdateReq,
)
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
from app.models.allergy_type_model import AllergyType
from app.models.allergy_reaction_type_model import AllergyReactionType
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_doctor_note_model import PatientDoctorNote
from app.models.patient_photo_model import PatientPhoto
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
from tests.utils.mock_db import get_db_session_mock


def test_get_all_allergies(db_session_mock):
    """Test case for retrieving all patient allergies."""
    # Arrange
    mock_data = [
        MagicMock(
            Patient_AllergyID=1,
            PatientID=1,
            AllergyRemarks="Severe reactions to corn",
            AllergyTypeValue="Corn",
            AllergyTypeIsDeleted="0",
            AllergyReactionTypeValue="Rashes",
            AllergyReactionTypeIsDeleted="0",
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=1,
            ModifiedById=1,
        ),
        MagicMock(
            Patient_AllergyID=2,
            PatientID=2,
            AllergyRemarks="Mild reactions to wheat",
            AllergyTypeValue="Wheat",
            AllergyTypeIsDeleted="0",
            AllergyReactionTypeValue="Sneezing",
            AllergyReactionTypeIsDeleted="0",
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=1,
            ModifiedById=1,
        ),
    ]
    db_session_mock.query.return_value.join.return_value.join.return_value.all.return_value = mock_data

    # Act
    result = get_all_allergies(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0]["AllergyTypeValue"] == "Corn"
    assert result[1]["AllergyReactionTypeValue"] == "Sneezing"



def test_get_patient_allergies(db_session_mock):
    """Test case for retrieving allergies for a specific patient."""
    # Arrange
    patient_id = 1
    mock_data = [
        MagicMock(
            Patient_AllergyID=1,
            PatientID=patient_id,
            AllergyRemarks="Severe reactions to corn",
            AllergyTypeValue="Corn",
            AllergyTypeIsDeleted="0",
            AllergyReactionTypeValue="Rashes",
            AllergyReactionTypeIsDeleted="0",
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=1,
            ModifiedById=1,
        )
    ]
    db_session_mock.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = mock_data

    # Act
    result = get_patient_allergies(db_session_mock, patient_id)

    # Assert
    assert len(result) == 1
    assert result[0]["PatientID"] == patient_id
    assert result[0]["AllergyTypeValue"] == "Corn"


def test_create_patient_allergy(db_session_mock, patient_allergy_create):
    """Test case for creating a new patient allergy."""
    # Arrange
    created_by = 1
    mock_allergy_type = AllergyType(AllergyTypeID=3, Value="Corn", IsDeleted="0")
    mock_reaction_type = AllergyReactionType(
        AllergyReactionTypeID=1, Value="Rashes", IsDeleted="0"
    )
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_allergy_type,
        mock_reaction_type,
        None,
    ]

    # Act
    result = create_patient_allergy(db_session_mock, patient_allergy_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.PatientID == patient_allergy_create.PatientID
    assert result.AllergyTypeID == patient_allergy_create.AllergyTypeID
    assert result.AllergyReactionTypeID == patient_allergy_create.AllergyReactionTypeID


def test_update_patient_allergy(db_session_mock, patient_allergy_update):
    """Test case for updating a patient allergy."""
    # Arrange
    modified_by = 2
    mock_patient_allergy = PatientAllergyMapping(
        Patient_AllergyID=1,
        PatientID=1,
        AllergyTypeID=3,
        AllergyReactionTypeID=1,
        AllergyRemarks="Severe reactions to corn",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=1,
        ModifiedById=1,
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_patient_allergy
    )

    # Act
    result = update_patient_allergy(
        db_session_mock, 1, patient_allergy_update, modified_by
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_patient_allergy)
    assert result.AllergyRemarks == patient_allergy_update.AllergyRemarks
    assert result.ModifiedById == modified_by


def test_delete_patient_allergy(db_session_mock):
    """Test case for deleting (soft-deleting) a patient allergy."""
    # Arrange
    modified_by = 2
    mock_patient_allergy = PatientAllergyMapping(
        Patient_AllergyID=1,
        PatientID=1,
        AllergyTypeID=3,
        AllergyReactionTypeID=1,
        AllergyRemarks="Severe reactions to corn",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=1,
        ModifiedById=1,
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_patient_allergy
    )

    # Act
    result = delete_patient_allergy(
        db_session_mock, mock_patient_allergy.Patient_AllergyID, modified_by
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_patient_allergy)
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def patient_allergy_create():
    """Fixture to provide a mock PatientAllergyCreate object."""
    return PatientAllergyCreate(
        PatientID=1,
        AllergyTypeID=3,
        AllergyReactionTypeID=1,
        AllergyRemarks="Severe reactions to corn",
    )


@pytest.fixture
def patient_allergy_update():
    """Fixture to provide a mock PatientAllergyUpdateReq object."""
    return PatientAllergyUpdateReq(
        Patient_AllergyID=1,
        AllergyTypeID=3,
        AllergyReactionTypeID=1,
        AllergyRemarks="Updated allergy remarks",
    )
