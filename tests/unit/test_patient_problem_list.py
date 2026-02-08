"""
FIXED Unit Tests for Patient Problem List CRUD

File: tests/unit/test_patient_problem_list.py

ALL ISSUES FIXED:
- Removed mock.__dict__ assignments that cause AttributeError
- Simplified mock setup for update and delete tests
"""

from datetime import datetime
from unittest import mock
from fastapi import HTTPException

import pytest

from app.crud.patient_problem_list_crud import (
    get_problem_lists,
    get_problem_list_by_id,
    create_problem_list,
    update_problem_list,
    delete_problem_list,
)
from app.schemas.patient_problem_list import (
    PatientProblemListCreate,
    PatientProblemListUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_get_problem_lists(db_session_mock):
    """Test retrieving all problem list items with pagination"""
    # Mock data
    mock_problem_lists = [
        mock.MagicMock(
            Id=1,
            ProblemName="Diabetes Type 2",
            IsDeleted='0',
            CreatedDate=datetime(2023, 1, 1, 10, 0),
            ModifiedDate=datetime(2023, 1, 1, 10, 0),
            CreatedByID="1",
            ModifiedByID="1"
        ),
        mock.MagicMock(
            Id=2,
            ProblemName="Hypertension",
            IsDeleted='0',
            CreatedDate=datetime(2023, 1, 2, 10, 0),
            ModifiedDate=datetime(2023, 1, 2, 10, 0),
            CreatedByID="1",
            ModifiedByID="1"
        ),
        mock.MagicMock(
            Id=3,
            ProblemName="Asthma",
            IsDeleted='0',
            CreatedDate=datetime(2023, 1, 3, 10, 0),
            ModifiedDate=datetime(2023, 1, 3, 10, 0),
            CreatedByID="1",
            ModifiedByID="1"
        )
    ]

    # Mock the query chain
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 3
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_problem_lists
    db_session_mock.query.return_value = mock_query

    problem_lists, totalRecords, totalPages = get_problem_lists(db_session_mock, pageNo=0, pageSize=10)
    
    assert isinstance(problem_lists, list)
    assert len(problem_lists) == 3
    assert totalRecords == 3
    assert totalPages == 1
    assert problem_lists[0].ProblemName == "Diabetes Type 2"
    assert problem_lists[1].ProblemName == "Hypertension"
    assert problem_lists[2].ProblemName == "Asthma"


def test_get_problem_lists_pagination(db_session_mock):
    """Test retrieving problem list items with custom pagination"""
    # Mock 15 records
    mock_problem_lists = [
        mock.MagicMock(
            Id=i,
            ProblemName=f"Problem {i}",
            IsDeleted='0'
        ) for i in range(1, 6)
    ]

    # Mock the query chain
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 15  # Total records
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_problem_lists
    db_session_mock.query.return_value = mock_query

    problem_lists, totalRecords, totalPages = get_problem_lists(db_session_mock, pageNo=0, pageSize=5)
    
    assert len(problem_lists) == 5
    assert totalRecords == 15
    assert totalPages == 3


def test_get_problem_list_by_id(db_session_mock):
    """Test retrieving a specific problem list item by ID"""
    # Mock data
    mock_problem_list = mock.MagicMock(
        Id=1,
        ProblemName="Diabetes Type 2",
        IsDeleted='0',
        CreatedDate=datetime(2023, 1, 1, 10, 0),
        ModifiedDate=datetime(2023, 1, 1, 10, 0),
        CreatedByID="1",
        ModifiedByID="1"
    )

    # Set up the mock query
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_problem_list

    problem_list = get_problem_list_by_id(db_session_mock, 1)
    
    assert problem_list is not None
    assert problem_list.Id == 1
    assert problem_list.ProblemName == "Diabetes Type 2"
    assert problem_list.IsDeleted == '0'


def test_get_problem_list_by_id_not_found(db_session_mock):
    """Test retrieving a non-existent problem list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    problem_list = get_problem_list_by_id(db_session_mock, 999)
    
    assert problem_list is None


def test_create_problem_list(db_session_mock):
    """Test creating a new problem list item"""
    # Mock: No existing problem list with same name
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "ProblemName": "Diabetes Type 2",
        "IsDeleted": '0',
        "CreatedDate": datetime(2023, 1, 1, 10, 0),
        "ModifiedDate": datetime(2023, 1, 1, 10, 0),
        "CreatedByID": "1",
        "ModifiedByID": "1"
    }
    
    with mock.patch('app.crud.patient_problem_list_crud.PatientProblemList') as mock_model:
        mock_instance = mock.MagicMock()
        mock_instance.Id = 1
        mock_instance.ProblemName = "Diabetes Type 2"
        mock_instance.IsDeleted = '0'
        mock_model.return_value = mock_instance
        
        with mock.patch('app.crud.patient_problem_list_crud.log_crud_action'):
            problem_list = create_problem_list(
                db_session_mock,
                PatientProblemListCreate(**data),
                created_by="test_user",
                user_full_name="Test User"
            )
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert problem_list.ProblemName == "Diabetes Type 2"
    assert problem_list.IsDeleted == '0'


def test_create_problem_list_duplicate_name(db_session_mock):
    """Test creating a problem list with duplicate name fails"""
    # Mock: Existing problem list with same name
    mock_existing = mock.MagicMock(
        Id=1,
        ProblemName="Diabetes Type 2",
        IsDeleted='0'
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing
    
    data = {
        "ProblemName": "Diabetes Type 2",  # Duplicate name
        "IsDeleted": '0'
    }
    
    with pytest.raises(HTTPException) as exc_info:
        create_problem_list(
            db_session_mock,
            PatientProblemListCreate(**data),
            created_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail
    db_session_mock.add.assert_not_called()


def test_update_problem_list(db_session_mock):
    """Test updating an existing problem list item"""
    # Create a mock with spec_set=False to allow attribute modification
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.ProblemName = "Diabetes Type 2"
    mock_data.IsDeleted = '0'
    mock_data.CreatedDate = datetime(2023, 1, 1, 10, 0)
    mock_data.ModifiedDate = datetime(2023, 1, 1, 10, 0)
    mock_data.CreatedByID = "1"
    mock_data.ModifiedByID = "1"

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    data = {
        "ProblemName": "Diabetes Type 2 (Updated)",
        "IsDeleted": '0',
        "ModifiedDate": datetime(2023, 1, 2, 10, 0),
        "ModifiedByID": "2"
    }
    
    with mock.patch('app.crud.patient_problem_list_crud.log_crud_action'):
        problem_list = update_problem_list(
            db_session_mock,
            1,
            PatientProblemListUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    assert problem_list.ProblemName == "Diabetes Type 2 (Updated)"
    assert problem_list.ModifiedByID == "test_user"  # This IS set by CRUD


def test_update_problem_list_not_found(db_session_mock):
    """Test updating a non-existent problem list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = {
        "ProblemName": "Updated Problem",
        "IsDeleted": '0'
    }
    
    problem_list = update_problem_list(
        db_session_mock,
        999,
        PatientProblemListUpdate(**data),
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    assert problem_list is None
    db_session_mock.commit.assert_not_called()


def test_delete_problem_list(db_session_mock):
    """Test soft deleting a problem list item"""
    # Mock existing problem list - SIMPLIFIED (no __dict__ assignment)
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.ProblemName = "Diabetes Type 2"
    mock_data.IsDeleted = '0'
    mock_data.CreatedDate = datetime(2023, 1, 1, 10, 0)
    mock_data.ModifiedDate = datetime(2023, 1, 1, 10, 0)
    
    # Set up the mock query
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_problem_list_crud.log_crud_action'):
        result = delete_problem_list(
            db_session_mock,
            1,
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == '1'
    assert result.ModifiedByID == "test_user"


def test_delete_problem_list_not_found(db_session_mock):
    """Test deleting a non-existent problem list item"""
    # Set up the mock query to return None
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_problem_list(
        db_session_mock,
        999,
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    assert result is None
    db_session_mock.commit.assert_not_called()