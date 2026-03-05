from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.crud.patient_highlight_type_crud import (
    create_highlight_type,
    delete_highlight_type,
    get_all_highlight_types,
    get_enabled_highlight_types,
    get_highlight_type_by_id,
    toggle_highlight_type_enabled,
    update_highlight_type,
)
from app.models.patient_highlight_type_model import PatientHighlightType
from app.schemas.patient_highlight_type import HighlightTypeCreate, HighlightTypeUpdate
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


# Test: Get All Highlight Types (with ordering)
def test_get_all_highlight_types_ordered_by_typename(db_session_mock):
    """Test case for retrieving all highlight types ordered by TypeName (A-Z)."""
    # Arrange - mock types in non-alphabetical order
    mock_types = [
        MagicMock(
            Id=2, 
            TypeName="VITAL SIGNS",  # Should come second
            TypeCode="VITAL",
            IsEnabled="1",
            IsDeleted="0"
        ),
        MagicMock(
            Id=1, 
            TypeName="ALLERGY ALERT",  # Should come first
            TypeCode="ALLERGY",
            IsEnabled="1",
            IsDeleted="0"
        ),
    ]
    
    # Mock query chain with order_by
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = mock_types
    db_session_mock.query.return_value = mock_query

    # Act
    result = get_all_highlight_types(db_session_mock)

    # Assert
    assert len(result) == 2
    # Verify order_by was called (TypeName.asc())
    mock_query.order_by.assert_called()


# Test: Get Enabled Highlight Types (with ordering)
def test_get_enabled_highlight_types_ordered(db_session_mock):
    """Test retrieving enabled types ordered by TypeName (A-Z)"""
    mock_types = [
        MagicMock(
            Id=1, 
            TypeName="MEDICATION ALERT",
            TypeCode="MEDICATION",
            IsEnabled="1",
            IsDeleted="0"
        ),
    ]
    
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = mock_types
    db_session_mock.query.return_value = mock_query

    result = get_enabled_highlight_types(db_session_mock)

    assert len(result) == 1
    mock_query.order_by.assert_called()


# Test: Create Highlight Type with UPPERCASE conversion
def test_create_highlight_type_converts_typecode_to_uppercase(db_session_mock):
    """Test case for creating a highlight type with TypeCode converted to UPPERCASE."""
    # Arrange
    created_by = "1"
    highlight_type_create = HighlightTypeCreate(
        TypeName="Prescription Alert",  # TypeName stays as-is
        TypeCode="prescription",  # lowercase TypeCode input
        Description="Test description"
    )

    # Mock: No existing type (so create will succeed)
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    # Act
    with mock.patch('app.crud.patient_highlight_type_crud.log_crud_action'):
        result = create_highlight_type(db_session_mock, highlight_type_create, created_by, "USER")

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    # Verify TypeCode was converted to UPPERCASE
    assert result.TypeCode == "PRESCRIPTION"
    # TypeName should remain as provided
    assert result.TypeName == "Prescription Alert"
    assert result.CreatedById == created_by


# Test: Create Highlight Type - Duplicate TypeCode check
def test_create_highlight_type_duplicate_typecode_raises_400(db_session_mock):
    """Test creating a highlight type with duplicate TypeCode (case-insensitive) raises HTTPException"""
    # Arrange
    created_by = "1"
    
    # Mock: Existing type with UPPERCASE TypeCode
    existing_type = MagicMock(
        Id=1,
        TypeCode="PRESCRIPTION",
        IsDeleted="0"
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing_type

    # Try to create with different case variations - all should fail
    for type_code in ["prescription", "Prescription", "PRESCRIPTION", "PrEsCrIpTiOn"]:
        highlight_type_create = HighlightTypeCreate(
            TypeName="Prescription Alert",
            TypeCode=type_code
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_highlight_type(db_session_mock, highlight_type_create, created_by, "USER")

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail
        
    db_session_mock.add.assert_not_called()


# Test: Get Highlight Type by ID
def test_get_highlight_type_by_id(db_session_mock):
    """Test case for retrieving a highlight type by ID."""
    # Arrange
    mock_highlight_type = MagicMock(
        Id=1,
        TypeName="PRESCRIPTION ALERT",
        TypeCode="PRESCRIPTION",
        IsEnabled="1",
        IsDeleted="0",
        CreatedById="1",
        ModifiedById="1",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    # Act
    result = get_highlight_type_by_id(db_session_mock, mock_highlight_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientHighlightType)
    assert result.Id == mock_highlight_type.Id
    assert result.TypeName == mock_highlight_type.TypeName
    assert result.IsDeleted == mock_highlight_type.IsDeleted


# Test: Update Highlight Type with UPPERCASE conversion
def test_update_highlight_type_converts_typecode_to_uppercase(db_session_mock):
    modified_by = "2"
    highlight_type_update = HighlightTypeUpdate(
        TypeCode="updated_prescription"  # lowercase TypeCode input
    )

    mock_highlight_type = PatientHighlightType(
        Id=1,
        TypeName="Prescription Alert",
        TypeCode="PRESCRIPTION",  # Current value is different from UPDATED_PRESCRIPTION
        Description="Test description",
        IsEnabled="1",
        IsDeleted="0",
        CreatedById="1",
        ModifiedById="1",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
    )

    # First call returns the existing record, second call (duplicate check) returns None
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_highlight_type,  # fetch existing record
        None,                 # duplicate check finds nothing
    ]

    with mock.patch('app.crud.patient_highlight_type_crud.log_crud_action'):
        result = update_highlight_type(
            db_session_mock,
            mock_highlight_type.Id,
            highlight_type_update,
            modified_by,
            "USER"
        )

    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_highlight_type)
    assert result.TypeCode == "UPDATED_PRESCRIPTION"
    assert result.ModifiedById == modified_by


# Test: Update Highlight Type - partial update doesn't affect TypeCode
def test_update_highlight_type_partial_update(db_session_mock):
    """Test updating only Description doesn't change TypeCode"""
    modified_by = "2"
    highlight_type_update = HighlightTypeUpdate(
        Description="New description"
    )

    mock_highlight_type = PatientHighlightType(
        Id=1,
        TypeName="Prescription Alert",
        TypeCode="PRESCRIPTION",
        Description="Old description",
        IsEnabled="1",
        IsDeleted="0",
        CreatedById="1",
        ModifiedById="1",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
    )
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    with mock.patch('app.crud.patient_highlight_type_crud.log_crud_action'):
        result = update_highlight_type(
            db_session_mock,
            mock_highlight_type.Id,
            highlight_type_update,
            modified_by,
            "USER"
        )

    # TypeCode should remain unchanged
    assert result.TypeCode == "PRESCRIPTION"
    assert result.Description == "New description"


# Test: Toggle Highlight Type Enabled
def test_toggle_highlight_type_enabled(db_session_mock):
    """Test toggling IsEnabled field"""
    modified_by = "2"
    
    mock_highlight_type = PatientHighlightType(
        Id=1,
        TypeName="Prescription Alert",
        TypeCode="PRESCRIPTION",
        IsEnabled="1",
        IsDeleted="0",  # String "0", not False
        CreatedById="1",
        ModifiedById="1",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
    )
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    with mock.patch('app.crud.patient_highlight_type_crud.log_crud_action'):
        result = toggle_highlight_type_enabled(
            db_session_mock,
            mock_highlight_type.Id,
            modified_by,
            "USER"
        )

    db_session_mock.commit.assert_called_once()
    # IsEnabled should be toggled (1 -> False/0)
    assert result.IsEnabled != "1"


# Test: Delete Highlight Type
def test_delete_highlight_type(db_session_mock):
    """Test case for deleting (soft-deleting) a highlight type."""
    # Arrange
    modified_by = "2"
    
    mock_highlight_type = PatientHighlightType(
        Id=1,
        TypeName="Prescription Alert",
        TypeCode="PRESCRIPTION",
        Description="Test description",
        IsEnabled="1",
        IsDeleted="0",  # String "0", not False
        CreatedById="1",
        ModifiedById="1",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
    )
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_highlight_type
    )

    # Act
    with mock.patch('app.crud.patient_highlight_type_crud.log_crud_action'):
        result = delete_highlight_type(
            db_session_mock, mock_highlight_type.Id, modified_by, "USER"
        )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by


# Test: Delete non-existent Highlight Type
def test_delete_highlight_type_not_found_raises_404(db_session_mock):
    """Test deleting non-existent highlight type raises 404"""
    modified_by = "2"
    
    # Mock: No highlight type found
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_highlight_type(db_session_mock, 999, modified_by, "USER")

    assert exc_info.value.status_code == 404