import pytest
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value = session_mock.query()
    session_mock.query().all.return_value = []
    session_mock.query().filter().first.return_value = None
    return session_mock

from app.crud.patient_mobility_list_crud import (
    get_all_mobility_list_entries,
    get_mobility_list_entry_by_id,
    create_mobility_list_entry,
    update_mobility_list_entry,
    delete_mobility_list_entry,
)
from app.schemas.patient_mobility_list import (
    PatientMobilityList,
    PatientMobilityListCreate,
    PatientMobilityListUpdate,
)

def test_get_all_mobility_list_entries(db_session_mock, mock_mobility_list_entries):
    db_session_mock.query().all.return_value = mock_mobility_list_entries
    result = get_all_mobility_list_entries(db_session_mock)
    assert result == mock_mobility_list_entries

def test_get_mobility_list_entry_by_id(db_session_mock, mock_mobility_list_entry):
    entry_id = 1
    db_session_mock.query().filter().first.return_value = mock_mobility_list_entry
    result = get_mobility_list_entry_by_id(db_session_mock, entry_id)
    assert result == mock_mobility_list_entry

def test_create_mobility_list_entry(db_session_mock, mobility_list_create_data):
    result = create_mobility_list_entry(db_session_mock, mobility_list_create_data, created_by=1)
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)


def test_delete_mobility_list_entry(db_session_mock, mock_mobility_list_entry):
    entry_id = 1
    db_session_mock.query().filter().first.return_value = mock_mobility_list_entry
    result = delete_mobility_list_entry(db_session_mock, entry_id, modified_by=1)
    db_session_mock.commit.assert_called_once()
    assert result == mock_mobility_list_entry

@pytest.fixture
def mock_mobility_list_entries():
    return [
        PatientMobilityList(
            MobilityListId=1,
            IsDeleted=0,
            CreatedDateTime=datetime.now(),
            ModifiedDateTime=datetime.now(),
            CreatedById=1,
            ModifiedById=1,
            Value="List 1",
        ),
        PatientMobilityList(
            MobilityListId=2,
            IsDeleted=0,
            CreatedDateTime=datetime.now(),
            ModifiedDateTime=datetime.now(),
            CreatedById=1,
            ModifiedById=1,
            Value="List 2",
        ),
    ]

@pytest.fixture
def mock_mobility_list_entry():
    return PatientMobilityList(
        MobilityListId=1,
        IsDeleted=0,
        CreatedDateTime=datetime.now(),
        ModifiedDateTime=datetime.now(),
        CreatedById=1,
        ModifiedById=1,
        Value="Sample List",
    )

@pytest.fixture
def mobility_list_create_data():
    return PatientMobilityListCreate(
        MobilityListId=1,
        Value="New List",
        CreatedById=1,
        ModifiedById=1,
        IsDeleted=0,
        CreatedDateTime=datetime.now(),
        ModifiedDateTime=datetime.now(),
    )
