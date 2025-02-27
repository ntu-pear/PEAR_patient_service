import pytest
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    session_mock = MagicMock()
    # Mock query for Patient with a valid PatientID
    session_mock.query().filter().first.side_effect = lambda *args, **kwargs: (
        MagicMock(id=1) if "Patient.id == 1" in str(args) else None
    )
    session_mock.query.return_value.filter.return_value = session_mock.query()
    session_mock.query().all.return_value = []
    session_mock.query().filter().first.return_value = None
    return session_mock

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

def test_get_all_mobility_entries(db_session_mock, mock_mobility_entries):
    db_session_mock.query().all.return_value = mock_mobility_entries
    result = get_all_mobility_entries(db_session_mock)
    assert result == mock_mobility_entries

def test_get_mobility_entries_by_id(db_session_mock, mock_mobility_entry):
    entry_id = 1
    db_session_mock.query().filter().first.return_value = mock_mobility_entry
    result = get_mobility_entry_by_mobility_id(db_session_mock, entry_id)
    assert result == mock_mobility_entry

# def test_create_mobility_entry(db_session_mock, mobility_create_data):
#     result = create_mobility_entry(db_session_mock, mobility_create_data, created_by=1)
#     db_session_mock.add.assert_called_once_with(result)
#     db_session_mock.commit.assert_called_once()
#     db_session_mock.refresh.assert_called_once_with(result)

# def test_update_mobility_entry(db_session_mock, mobility_update_data):
#     entry_id = 1
#     result = update_mobility_entry(
#         db_session_mock, entry_id, mobility_update_data, modified_by=1
#     )
#     db_session_mock.commit.assert_called_once()
#     db_session_mock.refresh.assert_called_once_with(result)

def test_delete_mobility_entry(db_session_mock, mock_mobility_entry):
    entry_id = 1
    db_session_mock.query().filter().first.return_value = mock_mobility_entry
    result = delete_mobility_entry(db_session_mock, entry_id, modified_by=1)
    db_session_mock.commit.assert_called_once()
    assert result == mock_mobility_entry

@pytest.fixture
def mock_mobility_entries():
    return [
        PatientMobilityResponse(
            PatientID=1,
            MobilityID=1,
            MobilityListId=1,
            MobilityRemarks="Remarks",
            IsDeleted=0,
            CreatedDateTime=datetime.now(),
            ModifiedDateTime=datetime.now(),
            CreatedById="1",
            ModifiedById="1",
        ),
        PatientMobilityResponse(
            PatientID=2,
            MobilityID=2,
            MobilityListId=1,
            MobilityRemarks="Remarks",
            IsDeleted=0,
            CreatedDateTime=datetime.now(),
            ModifiedDateTime=datetime.now(),
            CreatedById="1",
            ModifiedById="1",
        ),
    ]

@pytest.fixture
def mock_mobility_entry():
    return PatientMobilityResponse(
        PatientID=1,
        MobilityID=1,
        MobilityListId=1,
        MobilityRemarks="Remarks",
        IsDeleted=0,
        CreatedDateTime=datetime.now(),
        ModifiedDateTime=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )

# @pytest.fixture
# def mobility_create_data():
#     return PatientMobilityCreate(
#         PatientID=1,
#         MobilityListId=1,
#         MobilityRemarks="New Remarks",

#     )

# @pytest.fixture
# def mobility_update_data():
#     return PatientMobilityUpdate(
#         MobilityRemarks="Updated Remarks",
#         IsDeleted=0,
#         IsRecovered=False,  # Added the missing field
#     )