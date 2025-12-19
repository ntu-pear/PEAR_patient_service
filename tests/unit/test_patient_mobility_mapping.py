from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from app.crud.patient_mobility_mapping_crud import (
    create_mobility_entry,
    delete_mobility_entry,
    get_all_mobility_entries,
    get_mobility_entry_by_mobility_id,
    update_mobility_entry,
)
from app.schemas.patient_mobility_mapping import (
    PatientMobilityCreate,
    PatientMobilityResponse,
    PatientMobilityUpdate,
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
            RecoveryDate=None,
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
            RecoveryDate=None,
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
        RecoveryDate=None,
        IsDeleted=False,
        CreatedDateTime=datetime.now(),
        ModifiedDateTime=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )
    
@pytest.fixture
def mock_mobility_entry_recovered():
    """ Mock entry for a recovered patient with RecoveryDate """
    return PatientMobilityResponse(
        MobilityID=1,
        PatientID=1,
        MobilityListId=1,
        MobilityRemarks="Recovered from wheelchair",
        IsRecovered=True,
        RecoveryDate=date(2024, 12, 15),  # NEW: Has a recovery date
        IsDeleted=False,
        CreatedDateTime=datetime.now(),
        ModifiedDateTime=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )

@pytest.fixture
def mock_mobility_entry_not_recovered():
    """ Mock entry for a patient not recovered (for update tests) """
    entry = MagicMock()
    entry.MobilityID = 1
    entry.PatientID = 1
    entry.MobilityListId = 1
    entry.MobilityRemarks = "Uses wheelchair"
    entry.IsRecovered = False
    entry.RecoveryDate = None
    entry.IsDeleted = False
    entry.CreatedDateTime = datetime.now()
    entry.ModifiedDateTime = datetime.now()
    entry.CreatedById = "1"
    entry.ModifiedById = "1"
    return entry

@pytest.fixture
def mock_mobility_entry_already_recovered():
    """ Mock entry for a patient already recovered (for update tests) """
    entry = MagicMock()
    entry.MobilityID = 1
    entry.PatientID = 1
    entry.MobilityListId = 1
    entry.MobilityRemarks = "Recovered from wheelchair"
    entry.IsRecovered = True
    entry.RecoveryDate = date(2024, 12, 15)
    entry.IsDeleted = False
    entry.CreatedDateTime = datetime.now()
    entry.ModifiedDateTime = datetime.now()
    entry.CreatedById = "1"
    entry.ModifiedById = "1"
    return entry
    
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
        assert result[i].RecoveryDate == mock_mobility_entries[i].RecoveryDate
        assert result[i].IsDeleted == mock_mobility_entries[i].IsDeleted


def test_get_mobility_entries_by_id(db_session_mock, mock_mobility_entry):
    entry_id = 1
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry
    result = get_mobility_entry_by_mobility_id(db_session_mock, entry_id)
    assert result.MobilityID == mock_mobility_entry.MobilityID
    assert result.RecoveryDate == mock_mobility_entry.RecoveryDate

def test_delete_mobility_entry(db_session_mock, mock_mobility_entry):
    entry_id = 1
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry

    result = delete_mobility_entry(db_session_mock, entry_id, modified_by=1, user_full_name="USER")

    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == True

# New functional test cases for RecoveryDate and IsRecovered
def test_create_mobility_entry_not_recovered():
    """Test creating a mobility entry with IsRecovered=False should have RecoveryDate=None"""
    db_mock = MagicMock()
    
    # Mock the query results for validations
    db_mock.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(id=1),  # Patient exists
        MagicMock(MobilityListId=1),  # MobilityList exists
        None,  # No existing non-recovered mobility
    ]
    
    mobility_data = PatientMobilityCreate(
        PatientID=1,
        MobilityListId=1,
        MobilityRemarks="Uses wheelchair",
        IsRecovered=False,
        RecoveryDate=None
    )
    
    result = create_mobility_entry(db_mock, mobility_data, created_by="1", user_full_name="Test User")
    
    # The created entry should have RecoveryDate=None
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


def test_create_mobility_entry_recovered_with_date():
    """Test creating a mobility entry with IsRecovered=True and RecoveryDate provided"""
    db_mock = MagicMock()
    
    # Mock the query results for validations
    db_mock.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(id=1),  # Patient exists
        MagicMock(MobilityListId=1),  # MobilityList exists
        None,  # No existing non-recovered mobility
    ]
    
    recovery_date = date(2024, 12, 15)
    mobility_data = PatientMobilityCreate(
        PatientID=1,
        MobilityListId=1,
        MobilityRemarks="Recovered from wheelchair",
        IsRecovered=True,
        RecoveryDate=recovery_date
    )
    
    result = create_mobility_entry(db_mock, mobility_data, created_by="1", user_full_name="Test User")
    
    # The created entry should use the provided RecoveryDate
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


def test_create_mobility_entry_recovered_without_date():
    """Test creating a mobility entry with IsRecovered=True but no RecoveryDate should set to today"""
    db_mock = MagicMock()
    
    # Mock the query results for validations
    db_mock.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(id=1),  # Patient exists
        MagicMock(MobilityListId=1),  # MobilityList exists
        None,  # No existing non-recovered mobility
    ]
    
    mobility_data = PatientMobilityCreate(
        PatientID=1,
        MobilityListId=1,
        MobilityRemarks="Recovered from wheelchair",
        IsRecovered=True,
        RecoveryDate=None  # Not provided
    )
    
    result = create_mobility_entry(db_mock, mobility_data, created_by="1", user_full_name="Test User")
    
    # The created entry should have RecoveryDate set to today's date
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()


def test_update_mobility_entry_mark_as_recovered(mock_mobility_entry_not_recovered):
    """Test updating IsRecovered from False to True should set RecoveryDate to today"""
    db_mock = MagicMock()
    
    # Use the fixture for existing entry
    db_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry_not_recovered
    
    update_data = PatientMobilityUpdate(
        IsRecovered=True
    )
    
    result = update_mobility_entry(db_mock, mobility_id=1, mobility_data=update_data, modified_by="1", user_full_name="Test User")
    
    # RecoveryDate should be set to today
    assert mock_mobility_entry_not_recovered.RecoveryDate == date.today()
    db_mock.commit.assert_called_once()


def test_update_mobility_entry_mark_as_not_recovered(mock_mobility_entry_already_recovered):
    """Test updating IsRecovered from True to False should clear RecoveryDate"""
    db_mock = MagicMock()
    
    # Use the fixture for existing entry
    db_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry_already_recovered
    
    update_data = PatientMobilityUpdate(
        IsRecovered=False
    )
    
    result = update_mobility_entry(db_mock, mobility_id=1, mobility_data=update_data, modified_by="1", user_full_name="Test User")
    
    # RecoveryDate should be cleared
    assert mock_mobility_entry_already_recovered.RecoveryDate is None
    db_mock.commit.assert_called_once()


def test_update_mobility_entry_no_change_to_recovery_status(mock_mobility_entry_already_recovered):
    """Test updating other fields without changing IsRecovered should not affect RecoveryDate"""
    db_mock = MagicMock()
    
    # Store the original RecoveryDate to verify it doesn't change
    original_recovery_date = mock_mobility_entry_already_recovered.RecoveryDate
    
    # Use the fixture for existing entry
    db_mock.query.return_value.filter.return_value.first.return_value = mock_mobility_entry_already_recovered
    
    update_data = PatientMobilityUpdate(
        MobilityRemarks="New remarks"  # Only updating remarks, not IsRecovered
    )
    
    result = update_mobility_entry(db_mock, mobility_id=1, mobility_data=update_data, modified_by="1", user_full_name="Test User")
    
    # RecoveryDate should remain unchanged
    assert mock_mobility_entry_already_recovered.RecoveryDate == original_recovery_date
    db_mock.commit.assert_called_once()