from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

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
    """Test retrieving all prescription list items ordered by Value (A-Z)"""
    # Mock data - should be returned in alphabetical order
    mock_prescription_lists = [
        mock.MagicMock(
            Id=2,
            IsDeleted='0',
            CreatedDateTime=datetime(2023, 1, 2, 10, 0),
            UpdatedDateTime=datetime(2023, 1, 2, 10, 0),
            Value="ASPIRIN"
        ),
        mock.MagicMock(
            Id=1,
            IsDeleted='0',
            CreatedDateTime=datetime(2023, 1, 1, 10, 0),
            UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
            Value="PARACETAMOL"
        )
    ]

    # Mock the query chain properly
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 2
    mock_query.order_by.return_value = mock_query  # For .asc() ordering
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_prescription_lists
    db_session_mock.query.return_value = mock_query

    prescription_lists, totalRecords, totalPages = get_prescription_lists(db_session_mock, pageNo=0, pageSize=100)
    assert isinstance(prescription_lists, list)
    assert len(prescription_lists) == 2
    assert totalRecords == 2
    assert totalPages == 1
    # Verify ordering is called (Value.asc())
    mock_query.order_by.assert_called()


def test_get_prescription_list_by_id(db_session_mock):
    """Test retrieving a specific prescription list item by ID"""
    # Mock data
    mock_prescription_list = mock.MagicMock(
        Id=1,
        IsDeleted='0',
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="PARACETAMOL"
    )

    # Set up the mock query to return the mock prescription list
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_prescription_list

    prescription_list = get_prescription_list_by_id(db_session_mock, 1)
    assert prescription_list is not None
    assert prescription_list.Id == 1
    assert prescription_list.Value == "PARACETAMOL"


def test_get_prescription_list_by_id_not_found(db_session_mock):
    """Test retrieving a non-existent prescription list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    prescription_list = get_prescription_list_by_id(db_session_mock, 999)
    assert prescription_list is None


@mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
def test_create_prescription_list_converts_to_uppercase(mock_model, db_session_mock):
    """Test creating a prescription list converts Value to UPPERCASE"""
    
    # No existing prescription list record found (for duplicate check)
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "IsDeleted": '0',
        "CreatedDateTime": datetime(2023, 1, 1, 10, 0),
        "UpdatedDateTime": datetime(2023, 1, 1, 10, 0),
        "Value": "paracetamol"  # lowercase input
    }
    
    with mock.patch('app.crud.patient_prescription_list_crud.log_crud_action'):
        prescription_list = create_prescription_list(
            db_session_mock,
            PatientPrescriptionListCreate(**data),
            created_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    # Verify Value was converted to UPPERCASE
    assert prescription_list.Value == "PARACETAMOL"


@mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
def test_create_prescription_list_duplicate_check(mock_model, db_session_mock):
    """Test creating a duplicate prescription list raises HTTPException"""
    
    # Mock existing record with same UPPERCASE value
    existing_record = mock.MagicMock(
        Id=1,
        Value="PARACETAMOL",
        IsDeleted='0'
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing_record
    
    data = {
        "IsDeleted": '0',
        "Value": "paracetamol"  # Same name, different case
    }
    
    with pytest.raises(HTTPException) as exc_info:
        create_prescription_list(
            db_session_mock,
            PatientPrescriptionListCreate(**data),
            created_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail
    db_session_mock.add.assert_not_called()


@mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
def test_create_prescription_list_duplicate_case_insensitive(mock_model, db_session_mock):
    """Test duplicate check is case-insensitive"""
    
    # Mock existing record
    existing_record = mock.MagicMock(
        Id=1,
        Value="PARACETAMOL",
        IsDeleted='0'
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing_record
    
    # Try to create with different case variations
    for value in ["Paracetamol", "PARACETAMOL", "paracetamol", "PaRaCeTaMoL"]:
        data = {
            "IsDeleted": '0',
            "Value": value
        }
        
        with pytest.raises(HTTPException) as exc_info:
            create_prescription_list(
                db_session_mock,
                PatientPrescriptionListCreate(**data),
                created_by="test_user",
                user_full_name="Test User"
            )
        
        assert exc_info.value.status_code == 400


def test_update_prescription_list_converts_to_uppercase(db_session_mock):
    """Test updating prescription list converts Value to UPPERCASE"""
    # Mock data
    mock_data = mock.MagicMock(
        Id=1,
        IsDeleted='0',
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="PARACETAMOL"
    )

    # Set up the mock query to return the mock prescription list
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    data = {
        "Value": "paracetamol 500mg"  # lowercase input
    }
    
    with mock.patch('app.crud.patient_prescription_list_crud.log_crud_action'):
        prescription_list = update_prescription_list(
            db_session_mock,
            1,
            PatientPrescriptionListUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    # Verify Value was converted to UPPERCASE
    assert prescription_list.Value == "PARACETAMOL 500MG"


def test_update_prescription_list_partial_update(db_session_mock):
    """Test updating only specific fields doesn't affect Value"""
    mock_data = mock.MagicMock(
        Id=1,
        IsDeleted='0',
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="PARACETAMOL"
    )

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    # Update only IsDeleted, not Value
    data = {
        "IsDeleted": '1'
    }
    
    with mock.patch('app.crud.patient_prescription_list_crud.log_crud_action'):
        prescription_list = update_prescription_list(
            db_session_mock,
            1,
            PatientPrescriptionListUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    # Value should remain unchanged
    assert prescription_list.Value == "PARACETAMOL"


def test_update_prescription_list_not_found(db_session_mock):
    """Test updating a non-existent prescription list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = {
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
        IsDeleted='0',
        CreatedDateTime=datetime(2023, 1, 1, 10, 0),
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        Value="PARACETAMOL"
    )
    
    # Set up the mock query to return the mock prescription list
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_prescription_list_crud.log_crud_action'):
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