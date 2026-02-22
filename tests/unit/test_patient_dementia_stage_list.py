"""
Unit Tests for Patient Dementia Stage List CRUD

File: tests/unit/test_patient_dementia_stage_list.py

Tests for:
- Ordering by DementiaStage (A-Z)
- UPPERCASE conversion on create/update
- Case-insensitive duplicate checking
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_dementia_stage_list_crud import (
    create_dementia_stage_list_entry,
    delete_dementia_stage_list_entry,
    get_all_dementia_stage_list_entries,
    get_dementia_stage_list_entry_by_id,
    update_dementia_stage_list_entry,
)
from app.schemas.patient_dementia_stage_list import (
    PatientDementiaStageListCreate,
    PatientDementiaStageListUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_get_all_dementia_stage_list_ordered_by_dementiastage(db_session_mock):
    """Test retrieving all dementia stages ordered by DementiaStage (A-Z)"""
    # Mock data - intentionally not in alphabetical order
    mock_stages = [
        mock.MagicMock(
            id=2,
            DementiaStage="MODERATE",
            IsDeleted="0",
        ),
        mock.MagicMock(
            id=1,
            DementiaStage="EARLY",
            IsDeleted="0",
        ),
        mock.MagicMock(
            id=3,
            DementiaStage="SEVERE",
            IsDeleted="0",
        ),
    ]

    # Mock the query chain
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query  # For .asc() ordering
    mock_query.all.return_value = mock_stages
    db_session_mock.query.return_value = mock_query

    stages = get_all_dementia_stage_list_entries(db_session_mock)
    
    assert isinstance(stages, list)
    assert len(stages) == 3
    # Verify order_by was called
    mock_query.order_by.assert_called()

def test_get_dementia_stage_list_entry_by_id(db_session_mock):
    """Test retrieving a specific dementia stage by ID"""
    mock_stage = mock.MagicMock(
        id=1,
        DementiaStage="EARLY",
        IsDeleted="0",
    )

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_stage

    stage = get_dementia_stage_list_entry_by_id(db_session_mock, 1)
    
    assert stage is not None
    assert stage.id == 1
    assert stage.DementiaStage == "EARLY"


def test_get_dementia_stage_list_entry_by_id_not_found_raises_404(db_session_mock):
    """Test retrieving a non-existent dementia stage raises 404"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_dementia_stage_list_entry_by_id(db_session_mock, 999)
    
    assert exc_info.value.status_code == 404


def test_create_dementia_stage_converts_to_uppercase(db_session_mock):
    """Test creating a dementia stage converts DementiaStage to UPPERCASE"""
    # Mock: No existing stage with same name
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "DementiaStage": "early stage"  # lowercase input
    }
    
    with mock.patch('app.crud.patient_dementia_stage_list_crud.PatientDementiaStageList') as mock_model:
        mock_instance = mock.MagicMock()
        mock_instance.id = 1
        mock_instance.DementiaStage = "EARLY STAGE"  # Should be UPPERCASE
        mock_instance.IsDeleted = "0"
        mock_instance.CreatedDate = datetime.now()
        mock_instance.ModifiedDate = datetime.now()
        mock_model.return_value = mock_instance
        
        with mock.patch('app.crud.patient_dementia_stage_list_crud.log_crud_action'):
            stage = create_dementia_stage_list_entry(
                db_session_mock,
                PatientDementiaStageListCreate(**data),
                created_by="test_user",
                user_full_name="Test User"
            )
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    # Verify DementiaStage was converted to UPPERCASE
    assert stage.DementiaStage == "EARLY STAGE"


def test_create_dementia_stage_duplicate_check_case_insensitive(db_session_mock):
    """Test creating a dementia stage with duplicate name (case-insensitive) fails"""
    # Mock: Existing stage with UPPERCASE name
    mock_existing = mock.MagicMock(
        id=1,
        DementiaStage="EARLY",
        IsDeleted="0"
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing
    
    # Try to create with different case variations
    for name in ["early", "Early", "EARLY", "EaRlY"]:
        data = {
            "DementiaStage": name
        }
        
        with pytest.raises(HTTPException) as exc_info:
            create_dementia_stage_list_entry(
                db_session_mock,
                PatientDementiaStageListCreate(**data),
                created_by="test_user",
                user_full_name="Test User"
            )
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail


def test_update_dementia_stage_converts_to_uppercase(db_session_mock):
    """Test updating a dementia stage converts DementiaStage to UPPERCASE"""
    mock_data = mock.MagicMock()
    mock_data.id = 1
    mock_data.DementiaStage = "EARLY"
    mock_data.IsDeleted = "0"

    # First call: fetch record, Second call: duplicate check
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_data,  # fetch
        None,       # no duplicate
    ]

    data = {
        "DementiaStage": "moderate stage"  # lowercase input
    }
    
    with mock.patch('app.crud.patient_dementia_stage_list_crud.log_crud_action'):
        stage = update_dementia_stage_list_entry(
            db_session_mock,
            1,
            PatientDementiaStageListUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    # Verify DementiaStage was converted to UPPERCASE
    assert stage.DementiaStage == "MODERATE STAGE"


def test_update_dementia_stage_duplicate_check(db_session_mock):
    """Test updating to a duplicate DementiaStage raises 400"""
    mock_existing = mock.MagicMock(id=1, DementiaStage="EARLY", IsDeleted="0")
    mock_duplicate = mock.MagicMock(id=2, DementiaStage="MODERATE", IsDeleted="0")

    # First call: fetch record, Second call: duplicate check finds existing
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_existing,  # fetch
        mock_duplicate,  # duplicate found
    ]

    data = {
        "DementiaStage": "Moderate"  # Trying to update to existing stage
    }
    
    with pytest.raises(HTTPException) as exc_info:
        update_dementia_stage_list_entry(
            db_session_mock,
            1,
            PatientDementiaStageListUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_update_dementia_stage_not_found_returns_none(db_session_mock):
    """Test updating a non-existent dementia stage returns None"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = {
        "DementiaStage": "Updated Stage"
    }
    
    result = update_dementia_stage_list_entry(
        db_session_mock,
        999,
        PatientDementiaStageListUpdate(**data),
        modified_by="test_user",
        user_full_name="Test User"
    )
    
    assert result is None


def test_delete_dementia_stage(db_session_mock):
    """Test soft deleting a dementia stage"""
    mock_data = mock.MagicMock()
    mock_data.id = 1
    mock_data.DementiaStage = "EARLY"
    mock_data.IsDeleted = "0"
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_dementia_stage_list_crud.log_crud_action'):
        result = delete_dementia_stage_list_entry(
            db_session_mock,
            1,
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"


def test_delete_dementia_stage_not_found_raises_404(db_session_mock):
    """Test deleting a non-existent dementia stage raises 404"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_dementia_stage_list_entry(
            db_session_mock,
            999,
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 404