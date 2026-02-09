"""
FINAL WORKING test_patient_problem.py

CRITICAL FIX: Mock joinedload to prevent SQLAlchemy errors
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_problem_crud import (
    create_problem,
    delete_problem,
    get_patient_problems,
    get_problem,
    get_problems,
    update_problem,
)
from app.models.patient_problem_list_model import PatientProblemList
from app.models.patient_problem_model import PatientProblem
from app.schemas.patient_problem import PatientProblemCreate, PatientProblemUpdate
from tests.utils.mock_db import get_db_session_mock

USER_FULL_NAME = "TEST_USER"


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def mock_problem_list():
    """Fixture to mock problem list"""
    problem_list = mock.MagicMock(spec=PatientProblemList)
    problem_list.Id = 201
    problem_list.ProblemName = "Diabetes Type 2"
    problem_list.IsDeleted = '0'
    return problem_list


def test_get_problems(db_session_mock):
    """Test retrieving all patient problems with pagination"""
    mock_problems = [
        mock.MagicMock(
            Id=1,
            PatientID=1,
            ProblemListID=201,
            DateOfDiagnosis=datetime(2024, 1, 15),
            SourceOfInformation="Medical Records",
            ProblemRemarks="Well controlled",
            IsDeleted='0',
            CreatedDate=datetime(2024, 1, 15),
            ModifiedDate=datetime(2024, 1, 15)
        ),
        mock.MagicMock(
            Id=2,
            PatientID=2,
            ProblemListID=202,
            DateOfDiagnosis=datetime(2024, 2, 20),
            SourceOfInformation="Hospital Records",
            ProblemRemarks="Under treatment",
            IsDeleted='0',
            CreatedDate=datetime(2024, 2, 20),
            ModifiedDate=datetime(2024, 2, 20)
        )
    ]

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 2
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_problems
    db_session_mock.query.return_value = mock_query

    problems, totalRecords, totalPages = get_problems(db_session_mock, pageNo=0, pageSize=10)
    
    assert isinstance(problems, list)
    assert len(problems) == 2
    assert totalRecords == 2
    assert totalPages == 1


def test_get_patient_problems(db_session_mock):
    """Test retrieving problems for a specific patient"""
    patient_id = 1
    
    mock_problems = [
        mock.MagicMock(
            Id=1,
            PatientID=patient_id,
            ProblemListID=201,
            DateOfDiagnosis=datetime(2024, 1, 15),
            SourceOfInformation="Medical Records",
            ProblemRemarks="Well controlled",
            IsDeleted='0'
        )
    ]

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 1
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_problems
    db_session_mock.query.return_value = mock_query

    problems, totalRecords, totalPages = get_patient_problems(db_session_mock, patient_id, pageNo=0, pageSize=100)
    
    assert len(problems) == 1
    assert totalRecords == 1
    assert totalPages == 1


def test_get_problem(db_session_mock):
    """Test retrieving a specific problem by ID"""
    mock_problem = mock.MagicMock(
        Id=1,
        PatientID=1,
        ProblemListID=201,
        DateOfDiagnosis=datetime(2024, 1, 15),
        SourceOfInformation="Medical Records",
        ProblemRemarks="Well controlled",
        IsDeleted='0'
    )

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_problem
    db_session_mock.query.return_value = mock_query

    problem = get_problem(db_session_mock, 1)
    
    assert problem is not None
    assert problem.Id == 1


def test_get_problem_not_found(db_session_mock):
    """Test retrieving a non-existent problem"""
    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    db_session_mock.query.return_value = mock_query

    problem = get_problem(db_session_mock, 999)
    
    assert problem is None


def test_create_problem(db_session_mock, mock_problem_list):
    """Test creating a new patient problem"""
    call_count = 0
    
    def mock_query_side_effect(model):
        nonlocal call_count
        call_count += 1
        
        query = mock.MagicMock()
        query.filter.return_value = query
        query.options.return_value = query
        
        if call_count == 1:
            query.first.return_value = mock_problem_list
        elif call_count == 2:
            query.first.return_value = None
        else:
            mock_problem_with_list = mock.MagicMock()
            mock_problem_with_list.Id = 1
            mock_problem_with_list.PatientID = 1
            mock_problem_with_list.ProblemListID = 201
            query.first.return_value = mock_problem_with_list
        
        return query
    
    db_session_mock.query.side_effect = mock_query_side_effect
    db_session_mock.flush = mock.MagicMock()
    db_session_mock.commit = mock.MagicMock()
    
    data = {
        "PatientID": 1,
        "ProblemListID": 201,
        "DateOfDiagnosis": datetime(2024, 1, 15),
        "SourceOfInformation": "Medical Records",
        "ProblemRemarks": "Well controlled"
    }
    
    with mock.patch('app.crud.patient_problem_crud.joinedload') as mock_joinedload:
        # Make joinedload return a mock that doesn't trigger SQLAlchemy
        mock_joinedload.return_value = mock.MagicMock()
        
        with mock.patch('app.crud.patient_problem_crud.PatientProblem') as mock_patient_problem:
            mock_instance = mock.MagicMock()
            mock_instance.Id = 1
            mock_instance.PatientID = 1
            mock_instance.ProblemListID = 201
            mock_patient_problem.return_value = mock_instance
            
            with mock.patch('app.crud.patient_problem_crud.create_highlight_if_needed'):
                with mock.patch('app.crud.patient_problem_crud.log_crud_action'):
                    problem = create_problem(
                        db_session_mock,
                        PatientProblemCreate(**data),
                        created_by="test_user",
                        user_full_name=USER_FULL_NAME
                    )
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert problem.PatientID == 1


def test_create_problem_fails_problem_list_not_found(db_session_mock):
    """Test creating problem with invalid ProblemListID fails"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "PatientID": 1,
        "ProblemListID": 999,
        "DateOfDiagnosis": datetime(2024, 1, 15),
        "SourceOfInformation": "Medical Records"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        create_problem(
            db_session_mock,
            PatientProblemCreate(**data),
            created_by="test_user",
            user_full_name=USER_FULL_NAME
        )
    
    assert exc_info.value.status_code == 404
    assert "Problem list" in exc_info.value.detail


def test_create_problem_fails_duplicate_exists(db_session_mock, mock_problem_list):
    """Test creating duplicate problem fails"""
    mock_existing = mock.MagicMock(spec=PatientProblem)
    mock_existing.Id = 555
    mock_existing.PatientID = 1
    mock_existing.ProblemListID = 201
    mock_existing.IsDeleted = '0'
    
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_problem_list,
        mock_existing,
    ]
    
    data = {
        "PatientID": 1,
        "ProblemListID": 201,
        "DateOfDiagnosis": datetime(2024, 1, 15),
        "SourceOfInformation": "Medical Records"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        create_problem(
            db_session_mock,
            PatientProblemCreate(**data),
            created_by="test_user",
            user_full_name=USER_FULL_NAME
        )
    
    assert exc_info.value.status_code == 400
    assert "already has this problem recorded" in exc_info.value.detail


def test_create_problem_different_patient_same_condition(db_session_mock, mock_problem_list):
    """Test different patients can have the same problem"""
    call_count = 0
    
    def mock_query_side_effect(model):
        nonlocal call_count
        call_count += 1
        
        query = mock.MagicMock()
        query.filter.return_value = query
        query.options.return_value = query
        
        if call_count == 1:
            query.first.return_value = mock_problem_list
        elif call_count == 2:
            query.first.return_value = None
        else:
            mock_problem_with_list = mock.MagicMock()
            mock_problem_with_list.Id = 2
            query.first.return_value = mock_problem_with_list
        
        return query
    
    db_session_mock.query.side_effect = mock_query_side_effect
    db_session_mock.flush = mock.MagicMock()
    db_session_mock.commit = mock.MagicMock()
    
    data = {
        "PatientID": 2,
        "ProblemListID": 201,
        "DateOfDiagnosis": datetime(2024, 2, 20),
        "SourceOfInformation": "Hospital Records"
    }
    
    with mock.patch('app.crud.patient_problem_crud.joinedload') as mock_joinedload:
        mock_joinedload.return_value = mock.MagicMock()
        
        with mock.patch('app.crud.patient_problem_crud.PatientProblem') as mock_patient_problem:
            mock_instance = mock.MagicMock()
            mock_instance.Id = 2
            mock_patient_problem.return_value = mock_instance
            
            with mock.patch('app.crud.patient_problem_crud.create_highlight_if_needed'):
                with mock.patch('app.crud.patient_problem_crud.log_crud_action'):
                    problem = create_problem(
                        db_session_mock,
                        PatientProblemCreate(**data),
                        created_by="test_user",
                        user_full_name=USER_FULL_NAME
                    )
    
    db_session_mock.add.assert_called_once()


def test_update_problem(db_session_mock):
    """Test updating an existing problem"""
    mock_problem = mock.MagicMock()
    mock_problem.Id = 555
    mock_problem.PatientID = 1
    mock_problem.ProblemListID = 201
    mock_problem.IsDeleted = '0'
    
    call_count = 0
    
    def mock_query_side_effect(model):
        nonlocal call_count
        call_count += 1
        
        query = mock.MagicMock()
        query.filter.return_value = query
        query.options.return_value = query
        
        if call_count == 1:
            query.first.return_value = mock_problem
        elif call_count == 2:
            query.first.return_value = None
        else:
            mock_updated = mock.MagicMock()
            mock_updated.ProblemRemarks = "Improved with treatment"
            query.first.return_value = mock_updated
        
        return query
    
    db_session_mock.query.side_effect = mock_query_side_effect
    db_session_mock.commit = mock.MagicMock()
    db_session_mock.flush = mock.MagicMock()
    
    data = {
        "ProblemRemarks": "Improved with treatment"
    }
    
    with mock.patch('app.crud.patient_problem_crud.joinedload') as mock_joinedload:
        mock_joinedload.return_value = mock.MagicMock()
        
        with mock.patch('app.crud.patient_problem_crud.create_highlight_if_needed'):
            with mock.patch('app.crud.patient_problem_crud.log_crud_action'):
                problem = update_problem(
                    db_session_mock,
                    555,
                    PatientProblemUpdate(**data),
                    modified_by="test_user",
                    user_full_name=USER_FULL_NAME
                )
    
    db_session_mock.commit.assert_called_once()
    assert problem.ProblemRemarks == "Improved with treatment"


def test_update_problem_not_found(db_session_mock):
    """Test updating non-existent problem returns None"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "ProblemRemarks": "Updated"
    }
    
    result = update_problem(
        db_session_mock,
        9999,
        PatientProblemUpdate(**data),
        modified_by="test_user",
        user_full_name=USER_FULL_NAME
    )
    
    assert result is None


def test_update_problem_fails_duplicate_exists(db_session_mock):
    """Test updating to create duplicate fails"""
    mock_problem = mock.MagicMock()
    mock_problem.Id = 555
    mock_problem.PatientID = 1
    mock_problem.ProblemListID = 202
    mock_problem.IsDeleted = '0'
    
    duplicate_problem = mock.MagicMock()
    duplicate_problem.Id = 444
    duplicate_problem.PatientID = 1
    duplicate_problem.ProblemListID = 201
    duplicate_problem.IsDeleted = '0'
    
    call_count = 0
    
    def mock_first():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_problem
        else:
            return duplicate_problem
    
    db_session_mock.query.return_value.filter.return_value.first = mock_first
    
    data = {
        "ProblemListID": 201
    }
    
    with pytest.raises(HTTPException) as exc_info:
        update_problem(
            db_session_mock,
            555,
            PatientProblemUpdate(**data),
            modified_by="test_user",
            user_full_name=USER_FULL_NAME
        )
    
    assert exc_info.value.status_code == 400
    assert "Another problem record" in exc_info.value.detail


def test_delete_problem(db_session_mock):
    """Test soft deleting a problem"""
    mock_problem = mock.MagicMock()
    mock_problem.Id = 555
    mock_problem.PatientID = 1
    mock_problem.IsDeleted = '0'
    
    call_count = 0
    
    def mock_query_side_effect(model):
        nonlocal call_count
        call_count += 1
        
        query = mock.MagicMock()
        query.filter.return_value = query
        query.options.return_value = query
        
        if call_count == 1:
            query.first.return_value = mock_problem
        else:
            mock_deleted = mock.MagicMock()
            mock_deleted.IsDeleted = '1'
            mock_deleted.ModifiedByID = "test_user"
            query.first.return_value = mock_deleted
        
        return query
    
    db_session_mock.query.side_effect = mock_query_side_effect
    db_session_mock.flush = mock.MagicMock()
    db_session_mock.commit = mock.MagicMock()

    with mock.patch('app.crud.patient_problem_crud.joinedload') as mock_joinedload:
        mock_joinedload.return_value = mock.MagicMock()
        
        with mock.patch('app.crud.patient_problem_crud.create_highlight_if_needed'):
            with mock.patch('app.crud.patient_problem_crud.log_crud_action'):
                result = delete_problem(
                    db_session_mock,
                    555,
                    modified_by="test_user",
                    user_full_name=USER_FULL_NAME
                )
    
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == '1'


def test_delete_problem_not_found(db_session_mock):
    """Test deleting non-existent problem returns None"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_problem(
        db_session_mock,
        9999,
        modified_by="test_user",
        user_full_name=USER_FULL_NAME
    )
    
    assert result is None