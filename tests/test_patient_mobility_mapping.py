import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.crud.patient_mobility_mapping_crud import (
    get_all_mobility_entries,
    get_mobility_entry_by_mobility_id,
    create_mobility_entry,
    update_mobility_entry,
    delete_mobility_entry,
)
from app.schemas.patient_mobility_mapping import (
    PatientMobilityCreate,
    PatientMobilityUpdate,
    PatientMobilityResponse,
)

@pytest.fixture
def db_session_mock():
    session_mock = MagicMock()
    session_mock.query.return_value.count.return_value = 2  
    return session_mock

@pytest.fixture
def mock_mobility_entries():
    return [
        PatientMobilityResponse(
            MobilityID=1,
            PatientID=1,
            MobilityListId=1,
            MobilityRemarks="Remarks",
            IsRecovered=False,
            IsDeleted=False,
            CreatedDateTime=datetime.now(),
            ModifiedDateTime=datetime.now(),
            CreatedById="1",
            ModifiedById="1",
        ),
        PatientMobilityResponse(
            MobilityID=2,
            PatientID=2,
            MobilityListId=1,
            MobilityRemarks="Remarks",
            IsRecovered=False,
            IsDeleted=False,
            CreatedDateTime=datetime.now(),
            ModifiedDateTime=datetime.now(),
            CreatedById="1",
            ModifiedById="1",
        ),
    ]

@pytest.fixture
def mock_mobility_entry():
    return PatientMobilityResponse(
        MobilityID=1,
        PatientID=1,
        MobilityListId=1,
        MobilityRemarks="Remarks",
        IsRecovered=False,
        IsDeleted=False,
        CreatedDateTime=datetime.now(),
        ModifiedDateTime=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )
def test_get_all_mobility_entries(db_session_mock, mock_mobility_entries):
    # Fix mock behavior to return actual data instead of a MagicMock
    db_session_mock.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_mobility_entries
    db_session_mock.query.return_value.filter.return_value.count.return_value = len(mock_mobility_entries)  # Ensure count() returns an integer

    # Call function
    result, totalRecords, totalPages = get_all_mobility_entries(db_session_mock)

    # Assertions
    assert isinstance(result, list)  # Ensure result is a list
    assert totalRecords == len(mock_mobility_entries)  # Verify total records
    assert totalPages == 1  # Check calculated total pages

    for i in range(len(result)):
        assert result[i].MobilityID == mock_mobility_entries[i].MobilityID
        assert result[i].PatientID == mock_mobility_entries[i].PatientID
        assert result[i].MobilityListId == mock_mobility_entries[i].MobilityListId
        assert result[i].IsRecovered == mock_mobility_entries[i].IsRecovered
        assert result[i].IsDeleted == mock_mobility_entries[i].IsDeleted


def test_get_mobility_entries_by_id(db_session_mock, mock_mobility_entry):
    entry_id = 1
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry
    result = get_mobility_entry_by_mobility_id(db_session_mock, entry_id)
    assert result.MobilityID == mock_mobility_entry.MobilityID

def test_delete_mobility_entry(db_session_mock, mock_mobility_entry):
    entry_id = 1
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry

    result = delete_mobility_entry(db_session_mock, entry_id, modified_by=1, user_full_name="USER")

    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == True
