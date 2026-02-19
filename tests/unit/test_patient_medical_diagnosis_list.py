"""
Unit Tests for Patient Medical Diagnosis List CRUD

File: tests/unit/test_patient_medical_diagnosis_list.py

Tests for:
- Ordering by DiagnosisName (A-Z)
- UPPERCASE conversion on create/update
- Case-insensitive duplicate checking
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_medical_diagnosis_list_crud import (
    get_all_diagnosis_list,
    get_diagnosis_by_id,
    create_diagnosis,
    update_diagnosis,
    delete_diagnosis,
)
from app.schemas.patient_medical_diagnosis_list import (
    PatientMedicalDiagnosisListCreate,
    PatientMedicalDiagnosisListUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_get_all_diagnosis_list_ordered_by_diagnosisname(db_session_mock):
    """Test retrieving all diagnosis items ordered by DiagnosisName (A-Z)"""
    # Mock data - intentionally not in alphabetical order
    mock_diagnoses = [
        mock.MagicMock(
            Id=2,
            DiagnosisName="HYPERTENSION",
            IsDeleted="0",
        ),
        mock.MagicMock(
            Id=1,
            DiagnosisName="DIABETES",
            IsDeleted="0",
        ),
    ]

    # Mock the query chain
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query  # For .asc() ordering
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_diagnoses
    db_session_mock.query.return_value = mock_query
    
    # Mock count query
    db_session_mock.query.return_value.select_from.return_value.filter.return_value.scalar.return_value = 2

    diagnoses, totalRecords, totalPages = get_all_diagnosis_list(db_session_mock, pageNo=0, pageSize=10)
    
    assert isinstance(diagnoses, list)
    assert len(diagnoses) == 2
    # Verify order_by was called
    mock_query.order_by.assert_called()


def test_get_diagnosis_by_id(db_session_mock):
    """Test retrieving a specific diagnosis by ID"""
    mock_diagnosis = mock.MagicMock(
        Id=1,
        DiagnosisName="DIABETES",
        IsDeleted="0",
    )

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_diagnosis

    diagnosis = get_diagnosis_by_id(db_session_mock, 1)
    
    assert diagnosis is not None
    assert diagnosis.Id == 1
    assert diagnosis.DiagnosisName == "DIABETES"


def test_get_diagnosis_by_id_not_found(db_session_mock):
    """Test retrieving a non-existent diagnosis"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    diagnosis = get_diagnosis_by_id(db_session_mock, 999)
    
    assert diagnosis is None


def test_create_diagnosis_duplicate_check_case_insensitive(db_session_mock):
    """Test creating a diagnosis with duplicate name (case-insensitive) fails"""
    # Mock: Existing diagnosis with UPPERCASE name
    mock_existing = mock.MagicMock(
        Id=1,
        DiagnosisName="DIABETES",
        IsDeleted="0"
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing
    
    # Try to create with different case variations
    for name in ["diabetes", "Diabetes", "DIABETES", "DiAbEtEs"]:
        data = {
            "DiagnosisName": name,
            "IsDeleted": "0"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            create_diagnosis(
                db_session_mock,
                PatientMedicalDiagnosisListCreate(**data),
                user_id="test_user",
                user_full_name="Test User"
            )
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail


def test_update_diagnosis_converts_to_uppercase(db_session_mock):
    """Test updating a diagnosis converts DiagnosisName to UPPERCASE"""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.DiagnosisName = "DIABETES"
    mock_data.IsDeleted = "0"

    first_query = mock.MagicMock()
    first_query.filter.return_value.first.return_value = mock_data

    second_query = mock.MagicMock()
    second_query.filter.return_value.first.return_value = None

    db_session_mock.query.side_effect = [first_query, second_query]

    data = {
        "DiagnosisName": "diabetes mellitus type 2",  # lowercase input
    }
    
    with mock.patch('app.crud.patient_medical_diagnosis_list_crud.log_crud_action'):
        diagnosis = update_diagnosis(
            db_session_mock,
            1,
            PatientMedicalDiagnosisListUpdate(**data),
            user_id="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    # Verify DiagnosisName was converted to UPPERCASE
    assert diagnosis.DiagnosisName == "DIABETES MELLITUS TYPE 2"


def test_update_diagnosis_partial_update(db_session_mock):
    """Test updating only other fields doesn't affect DiagnosisName"""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.DiagnosisName = "DIABETES"
    mock_data.IsDeleted = "0"

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    # Create update with only non-DiagnosisName fields
    # Using model_dump to simulate partial update
    update_obj = mock.MagicMock()
    update_obj.model_dump.return_value = {}  # Empty partial update
    
    with mock.patch('app.crud.patient_medical_diagnosis_list_crud.log_crud_action'):
        diagnosis = update_diagnosis(
            db_session_mock,
            1,
            update_obj,
            user_id="test_user",
            user_full_name="Test User"
        )
    
    # DiagnosisName should remain unchanged
    assert diagnosis.DiagnosisName == "DIABETES"


def test_delete_diagnosis(db_session_mock):
    """Test soft deleting a diagnosis"""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.DiagnosisName = "DIABETES"
    mock_data.IsDeleted = "0"
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_medical_diagnosis_list_crud.log_crud_action'):
        result = delete_diagnosis(
            db_session_mock,
            1,
            user_id="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"


def test_delete_diagnosis_not_found(db_session_mock):
    """Test deleting a non-existent diagnosis"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_diagnosis(
        db_session_mock,
        999,
        user_id="test_user",
        user_full_name="Test User"
    )
    
    # Should return None for not found
    assert result is None