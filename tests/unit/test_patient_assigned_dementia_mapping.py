from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.crud.patient_assigned_dementia_mapping_crud import (
    create_assigned_dementia,
    delete_assigned_dementia,
    get_all_assigned_dementias,
    get_assigned_dementias,
    update_assigned_dementia,
)
from app.models.patient_assigned_dementia_mapping_model import (
    PatientAssignedDementiaMapping,
)
from app.schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementia,
    PatientAssignedDementiaCreate,
    PatientAssignedDementiaUpdate,
)

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

    now = datetime.now()
    print("creating")
    return PatientAssignedDementiaCreate(
        IsDeleted="0",
        PatientId=99,  # Use unique IDs to avoid conflicts
        DementiaTypeListId=1,
        DementiaStageId=1,
        CreatedDate=now,
        ModifiedDate=now,
        CreatedById="1",
        ModifiedById="1",
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
            DementiaStageId=1,
            CreatedById=1,
            ModifiedById=1,
        ),
        MagicMock(
            id=2,
            IsDeleted="0",
            PatientId=2,
            DementiaTypeListId=2,
            DementiaStageId=2,
            CreatedById=1,
            ModifiedById=1,
        ),
    ]


def test_get_all_assigned_dementias(db_session_mock):
    """Test retrieving all dementia assignments with pagination."""
    
    # Create mock results that simulate ORM objects
    mock_result_1 = MagicMock()
    mock_result_1.id = 1
    mock_result_1.PatientId = 101
    mock_result_1.DementiaTypeListId = 1
    mock_result_1.DementiaStageId = 1
    mock_result_1.IsDeleted = "0"
    mock_result_1.CreatedDate = "2025-01-01"
    mock_result_1.ModifiedDate = "2025-01-02"
    mock_result_1.CreatedById = "1"
    mock_result_1.ModifiedById = "2"
    mock_result_1.dementia_stage_value = "Mild"
    
    mock_result_2 = MagicMock()
    mock_result_2.id = 2
    mock_result_2.PatientId = 102
    mock_result_2.DementiaTypeListId = 2
    mock_result_2.DementiaStageId = 2
    mock_result_2.IsDeleted = "0"
    mock_result_2.CreatedDate = "2025-01-03"
    mock_result_2.ModifiedDate = "2025-01-04"
    mock_result_2.CreatedById = "1"
    mock_result_2.ModifiedById = "3"
    mock_result_2.dementia_stage_value = "Moderate"
    
    mock_results = [mock_result_1, mock_result_2]
    
    # Mock the main query chain
    db_session_mock.query.return_value.options.return_value.join.return_value.filter.return_value.count.return_value = 2
    db_session_mock.query.return_value.options.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_results
    
    # Mock the inner query for DementiaTypeValue
    # This needs to return different values for each call
    db_session_mock.query.return_value.filter.return_value.scalar.side_effect = ["Alzheimer's", "Vascular Dementia"]

    # Act: Call function
    result, totalRecords, totalPages = get_all_assigned_dementias(db_session_mock, pageNo=0, pageSize=2)

    # Assertions
    assert len(result) == 2  # Ensure 2 records returned
    assert totalRecords == 2  # Ensure correct count
    assert totalPages == 1  # Ensure correct pages
    assert result[0]["DementiaTypeValue"] == "Alzheimer's"
    assert result[0]["dementia_stage_value"] == "Mild"
    assert result[1]["DementiaTypeValue"] == "Vascular Dementia"
    assert result[1]["dementia_stage_value"] == "Moderate"

    # Debugging
    print("Returned Data:")
    for item in result:
        print(item)


def test_get_assigned_dementias(db_session_mock):
    """Test case for retrieving dementia assignments for a specific patient with pagination."""

    # Create mock results that simulate ORM objects
    mock_result_1 = MagicMock()
    mock_result_1.id = 1
    mock_result_1.PatientId = 101
    mock_result_1.DementiaTypeListId = 1
    mock_result_1.DementiaStageId = 1
    mock_result_1.IsDeleted = "0"
    mock_result_1.CreatedDate = "2025-01-01"
    mock_result_1.ModifiedDate = "2025-01-02"
    mock_result_1.CreatedById = "1"
    mock_result_1.ModifiedById = "2"
    mock_result_1.dementia_stage_value = "Mild"
    
    mock_result_2 = MagicMock()
    mock_result_2.id = 2
    mock_result_2.PatientId = 101
    mock_result_2.DementiaTypeListId = 2
    mock_result_2.DementiaStageId = 3
    mock_result_2.IsDeleted = "0"
    mock_result_2.CreatedDate = "2025-01-03"
    mock_result_2.ModifiedDate = "2025-01-04"
    mock_result_2.CreatedById = "1"
    mock_result_2.ModifiedById = "3"
    mock_result_2.dementia_stage_value = "Severe"
    
    mock_results = [mock_result_1, mock_result_2]

    # Mock the main query chain
    db_session_mock.query.return_value.options.return_value.join.return_value.filter.return_value.count.return_value = 2
    db_session_mock.query.return_value.options.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_results
    
    # Mock the inner query for DementiaTypeValue
    db_session_mock.query.return_value.filter.return_value.scalar.side_effect = ["Alzheimer's", "Vascular Dementia"]

    # Act: Call the function with the mocked session and patient ID
    patient_id = 101
    result, totalRecords, totalPages = get_assigned_dementias(db_session_mock, patient_id, pageNo=0, pageSize=2)

    # Assertions
    assert len(result) == 2  #  Ensure 2 records returned
    assert totalRecords == 2  # Ensure correct count
    assert totalPages == 1  # Ensure correct pages

    # Fix attribute access: Use `.PatientId` since result is now a model instance
    assert result[0].PatientId == 101
    assert result[0].DementiaTypeValue == "Alzheimer's"
    assert result[0].DementiaStageId == 1
    assert result[0].dementia_stage_value == "Mild"
    
    assert result[1].PatientId == 101
    assert result[1].DementiaTypeValue == "Vascular Dementia"
    assert result[1].DementiaStageId == 3
    assert result[1].dementia_stage_value == "Severe"

    # Debugging
    print("Returned Data:")
    for item in result:
        print(item)


# Test for updating a dementia assignment
@mock.patch("app.models.patient_assigned_dementia_mapping_model.PatientAssignedDementiaMapping")
def test_update_assigned_dementia(mock_patient_assigned_dementia_mapping, db_session_mock):
    """Test case for updating a dementia assignment."""
    # Arrange: Mock existing record
    mock_existing_record = MagicMock(
        id=1,
        PatientId=101,
        DementiaTypeListId=1,
        DementiaStageId=1,
        IsDeleted="0",
        CreatedDate="2025-01-01",
        ModifiedDate="2025-01-02",
        CreatedById="1",
        ModifiedById="2",
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing_record

    # Provide updated data
    updated_data = PatientAssignedDementiaUpdate(
        DementiaTypeListId=2,  # Updated field
        DementiaStageId=2,  # Updated stage
        ModifiedById="3"  # Required field
    )
    modified_by = "3"  # Simulate the ID of the user modifying the record

    # Act: Call the update function
    result = update_assigned_dementia(
        db=db_session_mock,
        dementia_id=1,
        dementia_data=updated_data,
        modified_by=modified_by,
        user_full_name="TEST_NAME"
    )

    # Assert: Verify that the fields were updated
    assert result.DementiaTypeListId == updated_data.DementiaTypeListId
    assert result.ModifiedById == modified_by
    assert result.ModifiedDate is not None

    # Ensure that commit was called
    db_session_mock.commit.assert_called_once()

    # Debug: Print updated record
    print("Updated Assignment:", result)


# Test for deleting a dementia assignment
@mock.patch("app.models.patient_assigned_dementia_mapping_model.PatientAssignedDementiaMapping")
def test_delete_assigned_dementia(mock_patient_assigned_dementia_mapping, db_session_mock):
    """Test case for deleting a dementia assignment."""
    mock_existing_record = MagicMock(
        id=1,
        PatientId=101,
        DementiaTypeListId=1,
        DementiaStageId=1,
        IsDeleted="0",
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing_record

    modified_by = 3
    result = delete_assigned_dementia(db_session_mock, 1, modified_by , user_full_name="TEST_NAME")

    assert result.IsDeleted == "1"
    db_session_mock.commit.assert_called_once()