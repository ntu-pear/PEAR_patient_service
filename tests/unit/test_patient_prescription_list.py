from datetime import datetime
from unittest import mock

import pytest

from app.crud.patient_prescription_list_crud import (
    create_prescription_list,
    delete_prescription_list,
    get_prescription_list_by_id,
    get_prescription_lists,
    update_prescription_list,
)
from app.schemas.patient_prescription_list import (
    PatientPrescriptionList,
    PatientPrescriptionListCreate,
    PatientPrescriptionListUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_get_prescription_lists(db_session_mock):
    """Test retrieving all prescription list items"""
    # Mock data
    mock_prescription_lists = [
        mock.MagicMock(
            Id=1,
            IsDeleted=False,
            CreatedDateTime=datetime(2023, 1, 1, 10, 0),
            UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
            Value="Paracetamol"
        ),
        mock.MagicMock(
            Id=2,
            IsDeleted=False,
            CreatedDateTime=datetime(2023, 1, 2, 10, 0),
            UpdatedDateTime=datetime(2023, 1, 2, 10, 0),
            Value="Ibuprofen"
        )
    ]

    # Mock the query chain properly
    mock_query = mock.MagicMock()
    mock_query.count.return_value = 2
    mock_query.offset.return_value.limit.return_value.all.return_value = mock_prescription_lists
    mock_query.order_by.return_value = mock_query  # In case order_by is called
    db_session_mock.query.return_value = mock_query

    prescription_lists, totalRecords, totalPages = get_prescription_lists(db_session_mock, pageNo=0, pageSize=100)
    assert isinstance(prescription_lists, list)
    assert len(prescription_lists) == 2
    assert totalRecords == 2
    assert totalPages == 1
    assert prescription_lists[0].Value == "Paracetamol"
    assert prescription_lists[1].Value == "Ibuprofen"


# def test_search_prescription_lists(db_session_mock):
#     """Test searching prescription list items by value"""
#     # Mock data
#     mock_prescription_lists = [
#         mock.MagicMock(
#             Id=1,
#             IsDeleted=False,
#             CreatedDateTime=datetime(2023, 1, 1, 10, 0),
#             UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
#             Value="Paracetamol"
#         )
#     ]

#     # Mock the query chain properly
#     mock_query = mock.MagicMock()
#     mock_filtered_query = mock.MagicMock()
#     mock_filtered_query.count.return_value = 1
#     mock_filtered_query.offset.return_value.limit.return_value.all.return_value = mock_prescription_lists
#     mock_filtered_query.order_by.return_value = mock_filtered_query  # In case order_by is called
#     mock_query.filter.return_value = mock_filtered_query
#     db_session_mock.query.return_value = mock_query

#     prescription_lists, totalRecords, totalPages = search_prescription_lists(
#         db_session_mock, 
#         search_value="Para",
#         pageNo=0, 
#         pageSize=100
#     )
#     assert isinstance(prescription_lists, list)
#     assert len(prescription_lists) == 1
#     assert totalRecords == 1
#     assert totalPages == 1
#     assert prescription_lists[0].Value == "Paracetamol"


def test_get_prescription_list_by_id(db_session_mock):
    """Test retrieving a specific prescription list item by ID"""
    # Mock data
    mock_prescription_list = mock.MagicMock(
        Id=1,
        IsDeleted=False,
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="Paracetamol"
    )

    # Set up the mock query to return the mock prescription list
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_prescription_list

    prescription_list = get_prescription_list_by_id(db_session_mock, 1)
    assert prescription_list is not None
    assert prescription_list.Id == 1
    assert prescription_list.Value == "Paracetamol"


def test_get_prescription_list_by_id_not_found(db_session_mock):
    """Test retrieving a non-existent prescription list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    prescription_list = get_prescription_list_by_id(db_session_mock, 999)
    assert prescription_list is None


@mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
def test_create_prescription_list(mock_model, db_session_mock):
    """Test creating a new prescription list item"""
    data = {
        "IsDeleted": False,
        "CreatedDateTime": datetime(2023, 1, 1, 10, 0),
        "UpdatedDateTime": datetime(2023, 1, 1, 10, 0),
        "Value": "Paracetamol"
    }
    
    prescription_list = create_prescription_list(
        db_session_mock,
        PatientPrescriptionListCreate(**data),
        created_by="test_user",
        user_full_name="Test User"
    )
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert prescription_list.Value == "Paracetamol"
    assert prescription_list.IsDeleted == False


def test_update_prescription_list(db_session_mock):
    """Test updating an existing prescription list item"""
    # Mock data
    mock_data = mock.MagicMock(
        Id=1,
        IsDeleted=False,
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="Paracetamol"
    )

    # Set up the mock query to return the mock prescription list
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    data = {
        "IsDeleted": False,
        "CreatedDateTime": datetime(2023, 1, 1, 10, 0),
        "UpdatedDateTime": datetime(2023, 1, 2, 10, 0),
        "Value": "Paracetamol 500mg"
    }
    
    prescription_list = update_prescription_list(
        db_session_mock,
        1,
        PatientPrescriptionListUpdate(**data),
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    db_session_mock.commit.assert_called_once()
    assert prescription_list.Value == "Paracetamol 500mg"
    assert prescription_list.UpdatedDateTime == datetime(2023, 1, 2, 10, 0)


def test_update_prescription_list_not_found(db_session_mock):
    """Test updating a non-existent prescription list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = {
        "IsDeleted": False,
        "CreatedDateTime": datetime(2023, 1, 1, 10, 0),
        "UpdatedDateTime": datetime(2023, 1, 2, 10, 0),
        "Value": "Paracetamol 500mg"
    }
    
    prescription_list = update_prescription_list(
        db_session_mock,
        999,
        PatientPrescriptionListUpdate(**data),
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    assert prescription_list is None


def test_delete_prescription_list(db_session_mock):
    """Test soft deleting a prescription list item"""
    # Mock data
    mock_data = mock.MagicMock(
        Id=1,
        IsDeleted=False,
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="Paracetamol"
    )
    
    # Set up the mock query to return the mock prescription list
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    result = delete_prescription_list(
        db_session_mock,
        1,
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == True


def test_delete_prescription_list_not_found(db_session_mock):
    """Test deleting a non-existent prescription list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_prescription_list(
        db_session_mock,
        999,
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    assert result is None