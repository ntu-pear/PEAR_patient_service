import pytest
from unittest import mock
from unittest.mock import MagicMock
from datetime import datetime
from app.crud.patient_assigned_dementia_list_crud import (
    get_all_dementia_list_entries,
    get_dementia_list_entry_by_id,
    create_dementia_list_entry,
    update_dementia_list_entry,
    delete_dementia_list_entry,
)
from app.schemas.patient_assigned_dementia_list import (
    PatientAssignedDementiaListCreate,
    PatientAssignedDementiaListUpdate,
)
from app.models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from tests.utils.mock_db import get_db_session_mock

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

def get_mock_dementia_list_entry():
    """Create a mock PatientAssignedDementiaList entry."""
    return PatientAssignedDementiaList(
        DementiaTypeListId=1,
        Value="Alzheimer's",
        IsDeleted="0",
        CreatedDate=datetime.utcnow(),
        ModifiedDate=datetime.utcnow(),
        CreatedById="1",
        ModifiedById="1",
    )

# Test: Get all dementia list entries
# Test: Get all dementia list entries
@mock.patch("app.models.patient_assigned_dementia_list_model.PatientAssignedDementiaList")
@mock.patch("app.models.patient_guardian_relationship_mapping_model.PatientGuardianRelationshipMapping")
@mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
@mock.patch("app.models.allergy_reaction_type_model.AllergyReactionType")
@mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
@mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")  # Mock PatientDoctorNote
@mock.patch("app.models.patient_photo_model.PatientPhoto")  # Mock PatientPhoto
@mock.patch("app.models.patient_photo_list_model.PatientPhotoList")  # Mock PatientPhoto
@mock.patch("app.models.patient_mobility_list_model.PatientMobilityList")
@mock.patch("app.models.patient_mobility_mapping_model.PatientMobility")
@mock.patch("app.models.patient_prescription_model.PatientPrescription")
@mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
@mock.patch("app.models.patient_vital_model.PatientVital")
@mock.patch("app.models.patient_highlight_model.PatientHighlight")
@mock.patch("app.models.allergy_type_model.AllergyType")
def test_get_all_dementia_list_entries(
    mock_dementia_list_model,
    mock_relationship_mapping_model,
    mock_patient_guardian_model,
    mock_allergy_reaction_model,
    mock_allergy_mapping_model,
    mock_doctor_note_model,
    mock_photo_model,
    mock_photo_list_model,
    mock_mobility_model,
    mock_mobility_model_list,
    mock_prescription_model,
    mock_social_history_model,
    mock_vital_model,
    mock_highlight_model,
    mock_allergy_type_model,
    db_session_mock,
):
    """Test case for retrieving all dementia list entries."""
    # Arrange: Create a mock instance
    mock_instance = MagicMock()
    mock_instance.DementiaTypeListId = 1
    mock_instance.Value = "Alzheimer's"
    mock_instance.IsDeleted = "0"
    mock_instance.CreatedById = "1"
    mock_instance.ModifiedById = "1"
    mock_instance.CreatedDate = datetime.utcnow()
    mock_instance.ModifiedDate = datetime.utcnow()

    # Mock query result to return the mock instance in a list
    db_session_mock.query.return_value.all.return_value = [mock_instance]

    # Debug: Ensure mock query is set up
    print("Mock Query Result:", db_session_mock.query.return_value.all())

    # Act: Call the function with the mocked session
    entries = get_all_dementia_list_entries(db_session_mock)

    # Debug: Print the returned entries
    print("Entries Retrieved:", entries)

    # Assert: Verify the returned entries match the mock data
    assert len(entries) == 1
    retrieved_entry = entries[0]
    assert retrieved_entry.DementiaTypeListId == mock_instance.DementiaTypeListId
    assert retrieved_entry.Value == mock_instance.Value
    assert retrieved_entry.IsDeleted == mock_instance.IsDeleted
    assert retrieved_entry.CreatedById == mock_instance.CreatedById
    assert retrieved_entry.ModifiedById == mock_instance.ModifiedById

# Test: Get dementia list entry by ID
@mock.patch("app.crud.patient_assigned_dementia_list_crud.PatientAssignedDementiaList")
def test_get_dementia_list_entry_by_id(mock_patient_assigned_dementia_list, db_session_mock):
    """Test case for retrieving a single dementia list entry by ID."""
    mock_entry = get_mock_dementia_list_entry()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_entry

    # Act
    entry = get_dementia_list_entry_by_id(db_session_mock, mock_entry.DementiaTypeListId)

    # Assert
    assert entry.DementiaTypeListId == mock_entry.DementiaTypeListId
    db_session_mock.query.return_value.filter.return_value.first.assert_called_once()

# Test: Create dementia list entry
def test_create_dementia_list_entry(db_session_mock):
    """Test case for creating a dementia list entry."""
    mock_input = PatientAssignedDementiaListCreate(Value="Alzheimer's")

    # Act
    created_entry = create_dementia_list_entry(db_session_mock, mock_input, created_by=1, user_full_name="TEST_NAME")

    # Assert
    db_session_mock.add.assert_called_once_with(created_entry)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(created_entry)

# Test: Update dementia list entry
@mock.patch("app.crud.patient_assigned_dementia_list_crud.PatientAssignedDementiaList")
def test_update_dementia_list_entry(mock_patient_assigned_dementia_list, db_session_mock):
    """Test case for updating a dementia list entry."""
    # Arrange: Mock the existing entry
    mock_entry = get_mock_dementia_list_entry()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_entry

    # Include all required fields for the update schema
    mock_input = PatientAssignedDementiaListUpdate(
        Value="Updated Value",
        IsDeleted="0"  # Include the required `IsDeleted` field
    )

    # Act: Perform the update
    updated_entry = update_dementia_list_entry(
        db_session_mock,
        mock_entry.DementiaTypeListId,
        mock_input,
        modified_by="1",
        user_full_name="TEST_NAME"
    )

    # Assert: Validate the updated fields
    assert updated_entry.Value == mock_input.Value
    assert updated_entry.IsDeleted == mock_input.IsDeleted
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(updated_entry)


# Test: Delete dementia list entry
@mock.patch("app.models.patient_assigned_dementia_list_model.PatientAssignedDementiaList")
def test_delete_dementia_list_entry(mock_patient_assigned_dementia_list, db_session_mock):
    """Test case for deleting a dementia list entry."""
    # Arrange: Mock existing dementia list entry
    mock_entry = get_mock_dementia_list_entry()
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_entry

    # Act: Call the delete function
    deleted_entry = delete_dementia_list_entry(
        db_session_mock,
        mock_entry.DementiaTypeListId,
        modified_by="1",
        user_full_name="TEST_NAME"
    )

    # Assert: Verify the entry is marked as deleted
    assert deleted_entry.IsDeleted == "1"

    # Assert: Verify database interactions
    db_session_mock.query.return_value.filter.return_value.first.assert_called_once()
    db_session_mock.commit.assert_called_once()

    # Debug Output: Print deleted entry details
    print("Deleted Entry:", deleted_entry)

