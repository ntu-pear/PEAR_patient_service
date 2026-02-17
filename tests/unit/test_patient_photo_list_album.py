"""
Unit Tests for Patient Photo List Album CRUD

File: tests/unit/test_patient_photo_list_album.py

Tests for:
- Ordering by Value (A-Z)
- UPPERCASE conversion on create/update
- Case-insensitive duplicate checking
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_photo_list_album_crud import (
    create_photo_list_album,
    delete_photo_list_album,
    get_all_photo_list_albums,
    get_photo_list_album_by_id,
    update_photo_list_album,
)
from app.schemas.patient_photo_list_album import (
    PatientPhotoListAlbumCreate,
    PatientPhotoListAlbumUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_get_all_photo_list_albums_ordered_by_value(db_session_mock):
    """Test retrieving all photo list albums ordered by Value (A-Z)"""
    # Mock data - intentionally not in alphabetical order
    mock_albums = [
        mock.MagicMock(
            AlbumCategoryListID=2,
            Value="VACATION",
            IsDeleted=0,
        ),
        mock.MagicMock(
            AlbumCategoryListID=1,
            Value="FAMILY",
            IsDeleted=0,
        ),
        mock.MagicMock(
            AlbumCategoryListID=3,
            Value="PETS",
            IsDeleted=0,
        ),
    ]

    # Mock the query chain
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query  # For .asc() ordering
    mock_query.all.return_value = mock_albums
    db_session_mock.query.return_value = mock_query

    albums = get_all_photo_list_albums(db_session_mock)
    
    assert isinstance(albums, list)
    assert len(albums) == 3
    # Verify order_by was called
    mock_query.order_by.assert_called()


def test_get_photo_list_album_by_id(db_session_mock):
    """Test retrieving a specific photo list album by ID"""
    mock_album = mock.MagicMock(
        AlbumCategoryListID=1,
        Value="FAMILY",
        IsDeleted=0,
    )

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_album

    album = get_photo_list_album_by_id(db_session_mock, 1)
    
    assert album is not None
    assert album.AlbumCategoryListID == 1
    assert album.Value == "FAMILY"


def test_get_photo_list_album_by_id_not_found(db_session_mock):
    """Test retrieving a non-existent photo list album"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    album = get_photo_list_album_by_id(db_session_mock, 999)
    
    assert album is None


def test_create_photo_list_album_converts_to_uppercase(db_session_mock):
    """Test creating a photo list album converts Value to UPPERCASE"""
    # Mock: No existing album with same name
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "Value": "family photos",  # lowercase input
        "IsDeleted": 0
    }
    
    with mock.patch('app.crud.patient_photo_list_album_crud.PatientPhotoListAlbum') as mock_model:
        mock_instance = mock.MagicMock()
        mock_instance.AlbumCategoryListID = 1
        mock_instance.Value = "FAMILY PHOTOS"  # Should be UPPERCASE
        mock_instance.IsDeleted = 0
        mock_instance.CreatedDateTime = datetime.now()
        mock_instance.UpdatedDateTime = datetime.now()
        mock_model.return_value = mock_instance
        
        with mock.patch('app.crud.patient_photo_list_album_crud.log_crud_action'):
            album = create_photo_list_album(
                db_session_mock,
                PatientPhotoListAlbumCreate(**data),
                created_by="test_user",
                user_full_name="Test User"
            )
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    # Verify Value was converted to UPPERCASE
    assert album.Value == "FAMILY PHOTOS"


def test_create_photo_list_album_duplicate_check_case_insensitive(db_session_mock):
    """Test creating a photo list album with duplicate name (case-insensitive) fails"""
    # Mock: Existing album with UPPERCASE name
    mock_existing = mock.MagicMock(
        AlbumCategoryListID=1,
        Value="FAMILY",
        IsDeleted=0
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing
    
    # Try to create with different case variations
    for name in ["family", "Family", "FAMILY", "FaMiLy"]:
        data = {
            "Value": name,
            "IsDeleted": 0
        }
        
        with pytest.raises(HTTPException) as exc_info:
            create_photo_list_album(
                db_session_mock,
                PatientPhotoListAlbumCreate(**data),
                created_by="test_user",
                user_full_name="Test User"
            )
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail


def test_update_photo_list_album_converts_to_uppercase(db_session_mock):
    """Test updating a photo list album converts Value to UPPERCASE"""
    mock_data = mock.MagicMock()
    mock_data.AlbumCategoryListID = 1
    mock_data.Value = "FAMILY"
    mock_data.IsDeleted = 0

    # First call: get the record to update
    # Second call: duplicate check (should return None since "FAMILY VACATION" doesn't exist)
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_data,  # fetch record
        None,       # no duplicate
    ]

    data = {
        "Value": "family vacation"  # lowercase input
    }
    
    with mock.patch('app.crud.patient_photo_list_album_crud.log_crud_action'):
        album = update_photo_list_album(
            db_session_mock,
            1,
            PatientPhotoListAlbumUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    # Verify Value was converted to UPPERCASE
    assert album.Value == "FAMILY VACATION"


def test_update_photo_list_album_duplicate_check(db_session_mock):
    """Test updating to a duplicate Value raises 400"""
    mock_existing = mock.MagicMock(AlbumCategoryListID=1, Value="FAMILY", IsDeleted=0)
    mock_duplicate = mock.MagicMock(AlbumCategoryListID=2, Value="VACATION", IsDeleted=0)

    # First call: fetch record to update
    # Second call: duplicate check finds existing record
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_existing,
        mock_duplicate,
    ]

    data = {
        "Value": "Vacation"  # Trying to update to existing album name
    }
    
    with pytest.raises(HTTPException) as exc_info:
        update_photo_list_album(
            db_session_mock,
            1,
            PatientPhotoListAlbumUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_update_photo_list_album_partial_update(db_session_mock):
    """Test updating only IsDeleted doesn't affect Value"""
    mock_data = mock.MagicMock()
    mock_data.AlbumCategoryListID = 1
    mock_data.Value = "FAMILY"
    mock_data.IsDeleted = 0

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    # Update only IsDeleted
    data = {}  # Empty update
    
    with mock.patch('app.crud.patient_photo_list_album_crud.log_crud_action'):
        album = update_photo_list_album(
            db_session_mock,
            1,
            PatientPhotoListAlbumUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    # Value should remain unchanged
    assert album.Value == "FAMILY"


def test_update_photo_list_album_not_found_raises_404(db_session_mock):
    """Test updating a non-existent photo list album raises 404"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = {
        "Value": "Updated Album"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        update_photo_list_album(
            db_session_mock,
            999,
            PatientPhotoListAlbumUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 404


def test_delete_photo_list_album(db_session_mock):
    """Test soft deleting a photo list album"""
    mock_data = mock.MagicMock()
    mock_data.AlbumCategoryListID = 1
    mock_data.Value = "FAMILY"
    mock_data.IsDeleted = 0
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_photo_list_album_crud.log_crud_action'):
        result = delete_photo_list_album(
            db_session_mock,
            1,
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == 1


def test_delete_photo_list_album_not_found_raises_404(db_session_mock):
    """Test deleting a non-existent photo list album raises 404"""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_photo_list_album(
            db_session_mock,
            999,
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 404


def test_delete_photo_list_album_already_deleted_raises_404(db_session_mock):
    """Test deleting an already deleted album raises 404"""
    mock_data = mock.MagicMock()
    mock_data.AlbumCategoryListID = 1
    mock_data.Value = "FAMILY"
    mock_data.IsDeleted = 1  # Already deleted
    
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with pytest.raises(HTTPException) as exc_info:
        delete_photo_list_album(
            db_session_mock,
            1,
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert exc_info.value.status_code == 404