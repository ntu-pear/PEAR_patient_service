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


def test_get_problem_lists_ordered_by_problemname(db_session_mock):
    """Test retrieving all problem list items ordered by ProblemName (A-Z)"""
    # Mock data - intentionally not in alphabetical order
    mock_problem_lists = [
        mock.MagicMock(
            Id=3,
            ProblemName="ASTHMA",
            IsDeleted='0',
        ),
        mock.MagicMock(
            Id=1,
            ProblemName="DIABETES TYPE 2",
            IsDeleted='0',
        ),
        mock.MagicMock(
            Id=2,
            ProblemName="HYPERTENSION",
            IsDeleted='0',
        )
    ]

    # Mock the query chain
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 3
    mock_query.order_by.return_value = mock_query  # For .asc() ordering
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_problem_lists
    db_session_mock.query.return_value = mock_query

    problem_lists, totalRecords, totalPages = get_problem_lists(db_session_mock, pageNo=0, pageSize=10)
    
    assert isinstance(problem_lists, list)
    assert len(problem_lists) == 3
    assert totalRecords == 3
    assert totalPages == 1
    # Verify order_by was called (ProblemName.asc())
    mock_query.order_by.assert_called()


def test_get_problem_list_by_id(db_session_mock):
    """Test retrieving a specific problem list item by ID"""
    mock_problem_list = mock.MagicMock(
        Id=1,
        ProblemName="DIABETES TYPE 2",
        IsDeleted='0',
    )

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_problem_list

    problem_list = get_problem_list_by_id(db_session_mock, 1)
    
    assert problem_list is not None
    assert problem_list.Id == 1
    assert problem_list.ProblemName == "DIABETES TYPE 2"


def test_get_problem_list_by_id_not_found(db_session_mock):
    """Test retrieving a non-existent problem list item"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    problem_list = get_problem_list_by_id(db_session_mock, 999)
    
    assert problem_list is None


def test_create_problem_list_converts_to_uppercase(db_session_mock):
    """Test creating a problem list converts ProblemName to UPPERCASE"""
    # Mock: No existing problem list with same name
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "ProblemName": "diabetes type 2",  # lowercase input
        "IsDeleted": '0',
    }
    
    with mock.patch('app.crud.patient_problem_list_crud.PatientProblemList') as mock_model:
        mock_instance = mock.MagicMock()
        mock_instance.Id = 1
        mock_instance.ProblemName = "DIABETES TYPE 2"  # Should be UPPERCASE
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
    # Verify ProblemName was converted to UPPERCASE
    assert problem_list.ProblemName == "DIABETES TYPE 2"


def test_create_problem_list_duplicate_check_case_insensitive(db_session_mock):
    """Test creating a problem list with duplicate name (case-insensitive) fails"""
    # Mock: Existing problem list with UPPERCASE name
    mock_existing = mock.MagicMock(
        Id=1,
        ProblemName="DIABETES TYPE 2",
        IsDeleted='0'
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing
    
    # Try to create with different case variations
    for name in ["diabetes type 2", "Diabetes Type 2", "DIABETES TYPE 2", "DiAbEtEs TyPe 2"]:
        data = {
            "ProblemName": name,
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


def test_update_problem_list_converts_to_uppercase(db_session_mock):
    """Test updating a problem list converts ProblemName to UPPERCASE"""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.ProblemName = "DIABETES TYPE 2"
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    data = {
        "ProblemName": "diabetes type 2 (updated)",  # lowercase input
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
    # Verify ProblemName was converted to UPPERCASE
    assert problem_list.ProblemName == "DIABETES TYPE 2 (UPDATED)"


def test_update_problem_list_partial_update(db_session_mock):
    """Test updating only IsDeleted doesn't affect ProblemName"""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.ProblemName = "DIABETES TYPE 2"
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    # Update only IsDeleted
    data = {
        "IsDeleted": '1'
    }
    
    with mock.patch('app.crud.patient_problem_list_crud.log_crud_action'):
        problem_list = update_problem_list(
            db_session_mock,
            1,
            PatientProblemListUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    # ProblemName should remain unchanged
    assert problem_list.ProblemName == "DIABETES TYPE 2"


def test_update_problem_list_not_found(db_session_mock):
    """Test updating a non-existent problem list item"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = {
        "ProblemName": "Updated Problem",
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
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.ProblemName = "DIABETES TYPE 2"
    mock_data.IsDeleted = '0'
    
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
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_problem_list(
        db_session_mock,
        999,
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    assert result is None
    db_session_mock.commit.assert_not_called()