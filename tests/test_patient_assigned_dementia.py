import pytest
from unittest import mock
from unittest.mock import MagicMock
from app.crud.patient_assigned_dementia_mapping_crud import (
    create_assigned_dementia,
    get_all_assigned_dementias,
)
from app.schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementiaCreate,
)
from app.models.patient_assigned_dementia_mapping_model import PatientAssignedDementiaMapping


# Mock the database session
@pytest.fixture
def db_session_mock():
    mock_session = MagicMock()
    # Ensure no duplicate record by default
    mock_session.query.return_value.filter.return_value.first.return_value = None
    return mock_session


# Mock input data for creating a dementia record
@pytest.fixture
def patient_assigned_dementia_create():
    from datetime import datetime

    now = datetime.utcnow()
    print("creating")
    return PatientAssignedDementiaCreate(
        IsDeleted="0",
        PatientId=99,  # Use unique IDs to avoid conflicts
        DementiaTypeListId=1,
        CreatedDate=now,
        ModifiedDate=now,
        CreatedById=1,
        ModifiedById=1,
    )


# Mock data for testing retrieval
@pytest.fixture
def get_mock_assigned_dementias():
    return [
        MagicMock(
            id=1,
            IsDeleted="0",
            PatientId=1,
            DementiaTypeListId=1,
            CreatedById=1,
            ModifiedById=1,
        ),
        MagicMock(
            id=2,
            IsDeleted="0",
            PatientId=2,
            DementiaTypeListId=2,
            CreatedById=1,
            ModifiedById=1,
        ),
    ]


# Test creating an assigned dementia record
@mock.patch("app.models.patient_guardian_relationship_mapping_model.PatientGuardianRelationshipMapping")
@mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
@mock.patch("app.models.allergy_reaction_type_model.AllergyReactionType")
@mock.patch("app.models.patient_assigned_dementia_list_model.PatientAssignedDementiaList")
@mock.patch("app.models.allergy_type_model.AllergyType")
@mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
@mock.patch("app.models.patient_highlight_model.PatientHighlight")
@mock.patch("app.models.patient_vital_model.PatientVital")
@mock.patch("app.models.patient_prescription_model.PatientPrescription")
@mock.patch("app.models.patient_mobility_model.PatientMobility")
@mock.patch("app.models.patient_photo_model.PatientPhoto")
@mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")
@mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
@mock.patch("app.models.patient_assigned_dementia_mapping_model.PatientAssignedDementiaMapping")
def test_create_assigned_dementia(
    mock_patient_assigned_dementia_mapping,
    mock_patient_assigned_dementia_list,
    mock_allergy_reaction_type,
    mock_patient_guardian_relationship_mapping,
    mock_patient_patient_guardian,
    mock_allergy_type,
    mock_patient_social_history,
    mock_patient_highlight,
    mock_patient_vital,
    mock_patient_prescription,
    mock_patient_mobility,
    mock_patient_photo,
    mock_patient_doctor_note,
    mock_patient_allergy_mapping,
    db_session_mock,
    patient_assigned_dementia_create,
):
    """Test case for creating an assigned dementia record."""
    # Mock valid dementia type
    dementia_type_mock = MagicMock()
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        dementia_type_mock,  # First query for dementia type existence
        None,  # Second query for checking existing assignment
    ]

    # Explicitly set attributes for the mocked PatientAssignedDementiaMapping instance
    mock_instance = PatientAssignedDementiaMapping(
        PatientId=patient_assigned_dementia_create.PatientId,
        DementiaTypeListId=patient_assigned_dementia_create.DementiaTypeListId,
        IsDeleted=patient_assigned_dementia_create.IsDeleted,
        CreatedById=patient_assigned_dementia_create.CreatedById,
        ModifiedById=patient_assigned_dementia_create.ModifiedById,
    )
    db_session_mock.add.side_effect = lambda x: setattr(x, "id", 1)  # Simulate setting a database-generated ID

    # Mock the PatientAssignedDementiaMapping model creation to return the mock instance
    mock_patient_assigned_dementia_mapping.return_value = mock_instance

    # Act
    created_by = 1
    result = create_assigned_dementia(
        db_session_mock, patient_assigned_dementia_create, created_by
    )

    # Validate the object added to the database
    added_instance = db_session_mock.add.call_args[0][0]
    assert isinstance(added_instance, PatientAssignedDementiaMapping)
    assert added_instance.PatientId == patient_assigned_dementia_create.PatientId
    assert added_instance.DementiaTypeListId == patient_assigned_dementia_create.DementiaTypeListId
    assert added_instance.IsDeleted == patient_assigned_dementia_create.IsDeleted
    assert added_instance.CreatedById == patient_assigned_dementia_create.CreatedById
    assert added_instance.ModifiedById == patient_assigned_dementia_create.ModifiedById

    # Assert database interaction
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(added_instance)

    # Print for debugging purposes
    print("Created Object:", added_instance)
    print("Attributes:")
    print(f"PatientId: {added_instance.PatientId}")
    print(f"DementiaTypeListId: {added_instance.DementiaTypeListId}")
    print(f"IsDeleted: {added_instance.IsDeleted}")
    print(f"CreatedById: {added_instance.CreatedById}")
    print(f"ModifiedById: {added_instance.ModifiedById}")



@mock.patch("app.models.patient_assigned_dementia_mapping_model.PatientAssignedDementiaMapping")
@mock.patch("app.models.patient_assigned_dementia_list_model.PatientAssignedDementiaList")
def test_get_all_assigned_dementias(
    mock_patient_assigned_dementia_mapping,
    mock_patient_assigned_dementia_list,
    db_session_mock,
):
    """Test case for retrieving all dementia assignments."""
    # Mock data to simulate query results
    mock_results = [
        MagicMock(
            id=1,
            PatientId=101,
            DementiaTypeListId=1,
            IsDeleted="0",
            CreatedDate="2025-01-01",
            ModifiedDate="2025-01-02",
            CreatedById=1,
            ModifiedById=2,
            DementiaTypeValue="Alzheimer's",
        ),
        MagicMock(
            id=2,
            PatientId=102,
            DementiaTypeListId=2,
            IsDeleted="0",
            CreatedDate="2025-01-03",
            ModifiedDate="2025-01-04",
            CreatedById=1,
            ModifiedById=3,
            DementiaTypeValue="Vascular Dementia",
        ),
    ]

    # Mock the query behavior
    db_session_mock.query.return_value.join.return_value.filter.return_value.all.return_value = mock_results

    # Act: Call the function with the mocked session
    result = get_all_assigned_dementias(db_session_mock)

    # Assert: Verify the length of the returned data
    assert len(result) == 2

    # Assert: Verify the data matches the mocked results
    assert result[0]["PatientId"] == 101
    assert result[0]["DementiaTypeValue"] == "Alzheimer's"
    assert result[1]["PatientId"] == 102
    assert result[1]["DementiaTypeValue"] == "Vascular Dementia"

    # Debug: Print the result for verification
    print("Test Result:")
    for item in result:
        print(item)