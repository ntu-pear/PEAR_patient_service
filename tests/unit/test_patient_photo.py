from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.crud.patient_photo_crud import (
    create_patient_photo,
    delete_patient_photo,
    delete_patient_photo_by_photo_id,
    extract_public_id_from_url,
    get_patient_photo_by_patient_id,
    get_patient_photo_by_photo_id,
    get_patient_photos,
    update_patient_photo,
    update_patient_photo_by_photo_id,
)
from app.schemas.patient_photo import PatientPhotoCreate, PatientPhotoUpdate
from tests.utils.mock_db import get_db_session_mock


def test_extract_public_id_with_version():
    url = "https://res.cloudinary.com/demo/image/upload/v1234567/patients/photo.jpg"
    result = extract_public_id_from_url(url)
    assert result == "patients/photo"


def test_extract_public_id_without_version():
    url = "https://res.cloudinary.com/demo/image/upload/patients/photo.jpg"
    result = extract_public_id_from_url(url)
    assert result == "patients/photo"


def test_extract_public_id_invalid_url():
    result = extract_public_id_from_url("not-a-valid-url")
    assert result is None


def test_get_patient_photos(db_session_mock):
    mock_data = [
        MagicMock(PatientPhotoID=1, PatientID=1, IsDeleted=0),
        MagicMock(PatientPhotoID=2, PatientID=2, IsDeleted=0),
    ]
    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_data

    result = get_patient_photos(db_session_mock)

    assert len(result) == 2


def test_get_patient_photo_by_patient_id_found(db_session_mock):
    mock_data = [MagicMock(PatientPhotoID=1, PatientID=1, IsDeleted=0)]
    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_data

    result = get_patient_photo_by_patient_id(db_session_mock, 1)

    assert len(result) == 1
    assert result[0].PatientID == 1


def test_get_patient_photo_by_patient_id_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.all.return_value = []

    result = get_patient_photo_by_patient_id(db_session_mock, 999)

    assert result == []


def test_get_patient_photo_by_photo_id_found(db_session_mock):
    mock_photo = MagicMock(PatientPhotoID=1, PatientID=1, IsDeleted=0)
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_photo

    result = get_patient_photo_by_photo_id(db_session_mock, 1)

    assert result is mock_photo


def test_get_patient_photo_by_photo_id_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = get_patient_photo_by_photo_id(db_session_mock, 999)

    assert result is None


@patch("app.crud.patient_photo_crud.upload_photo_to_cloudinary", return_value="https://cloudinary.com/photo.jpg")
def test_create_patient_photo(mock_upload, db_session_mock, photo_create):
    mock_file = MagicMock()

    result = create_patient_photo(db_session_mock, mock_file, photo_create, "user1", "User One")

    mock_upload.assert_called_once_with(mock_file)
    assert result.PhotoPath == "https://cloudinary.com/photo.jpg"
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)


@patch("app.crud.patient_photo_crud.upload_photo_to_cloudinary", return_value="https://cloudinary.com/new.jpg")
@patch("app.crud.patient_photo_crud.delete_photo_from_cloudinary", return_value=True)
def test_update_patient_photo_found(mock_delete, mock_upload, db_session_mock, photo_update):
    mock_photo = MagicMock(PatientID=1, PhotoPath="https://cloudinary.com/old.jpg", IsDeleted=0)
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_photo
    mock_file = MagicMock()

    result = update_patient_photo(db_session_mock, 1, mock_file, photo_update, "user1", "User One")

    mock_delete.assert_called_once_with("https://cloudinary.com/old.jpg")
    mock_upload.assert_called_once_with(mock_file)
    assert mock_photo.PhotoPath == "https://cloudinary.com/new.jpg"
    db_session_mock.commit.assert_called_once()
    assert result is mock_photo


def test_update_patient_photo_not_found(db_session_mock, photo_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    mock_file = MagicMock()

    result = update_patient_photo(db_session_mock, 999, mock_file, photo_update, "user1", "User One")

    assert result is None


@patch("app.crud.patient_photo_crud.delete_photo_from_cloudinary", return_value=True)
def test_delete_patient_photo_found(mock_delete, db_session_mock):
    mock_photos = [
        MagicMock(PatientPhotoID=1, PatientID=1, PhotoPath="https://cloudinary.com/photo.jpg", IsDeleted=0),
    ]
    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_photos

    result = delete_patient_photo(db_session_mock, 1, "user1", "User One")

    assert mock_photos[0].IsDeleted == 1
    db_session_mock.commit.assert_called_once()
    assert result is mock_photos


def test_delete_patient_photo_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.all.return_value = []

    result = delete_patient_photo(db_session_mock, 999, "user1", "User One")

    assert result is None


@patch("app.crud.patient_photo_crud.delete_photo_from_cloudinary", return_value=True)
def test_delete_patient_photo_by_photo_id_found(mock_delete, db_session_mock):
    mock_photo = MagicMock(PatientPhotoID=1, PhotoPath="https://cloudinary.com/photo.jpg", IsDeleted=0)
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_photo

    result = delete_patient_photo_by_photo_id(db_session_mock, 1, "user1", "User One")

    assert mock_photo.IsDeleted == 1
    db_session_mock.commit.assert_called_once()
    assert result is mock_photo


def test_delete_patient_photo_by_photo_id_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_patient_photo_by_photo_id(db_session_mock, 999, "user1", "User One")

    assert result is None


@patch("app.crud.patient_photo_crud.upload_photo_to_cloudinary", return_value="https://cloudinary.com/updated.jpg")
@patch("app.crud.patient_photo_crud.delete_photo_from_cloudinary", return_value=True)
def test_update_patient_photo_by_photo_id_found(mock_delete, mock_upload, db_session_mock, photo_update):
    mock_photo = MagicMock(PatientPhotoID=1, PhotoPath="https://cloudinary.com/old.jpg", IsDeleted=0)
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_photo
    mock_file = MagicMock()

    result = update_patient_photo_by_photo_id(db_session_mock, 1, mock_file, photo_update, "user1", "User One")

    db_session_mock.commit.assert_called_once()
    assert result is mock_photo


def test_update_patient_photo_by_photo_id_not_found(db_session_mock, photo_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    mock_file = MagicMock()

    result = update_patient_photo_by_photo_id(db_session_mock, 999, mock_file, photo_update, "user1", "User One")

    assert result is None


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def photo_create():
    return PatientPhotoCreate(PatientID=1, AlbumCategoryListID=1)


@pytest.fixture
def photo_update():
    return PatientPhotoUpdate(PhotoDetails="Updated details")
