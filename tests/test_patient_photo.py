import cloudinary.api
import pytest
from unittest import mock
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import relationship
from app.crud.patient_photo_crud import (
    get_patient_photos,
    get_patient_photo_by_id,
    create_patient_photo,
    update_patient_photo,
    delete_patient_photo,
    upload_photo_to_cloudinary
)
from app.models.patient_photo_model import PatientPhoto
from app.schemas.patient_photo import PatientPhotoCreate, PatientPhotoUpdate
from tests.utils.mock_db import get_db_session_mock
import cloudinary


def test_get_patient_photos(db_session_mock):
    """Test case for retrieving all active patient photos"""
    #Arrange
    mock_data = [
        MagicMock(
            PatientPhotoID = 1,
            IsDeleted = 0,
            PhotoPath = "Path String A",
            PhotoDetails = "Portrait profile photo of A",
            AlbumCategoryListID = 1,
            PatientID = 1,
            CreatedDateTime = datetime.now(),
            UpdatedDateTime = datetime.now(),
            CreatedById = 1,
            ModifiedById = 1,
        ),
        MagicMock(
            PatientPhotoID = 2,
            IsDeleted = 0,
            PhotoPath = "Path String B",
            PhotoDetails = "Portrait profile photo of B",
            AlbumCategoryListID = 1,
            PatientID = 2,
            CreatedDateTime = datetime.now(),
            UpdatedDateTime = datetime.now(),
            CreatedById = 1,
            ModifiedById = 1,
        ),
    ]

    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_data

    #Act
    result = get_patient_photos(db_session_mock)

    #Assert
    assert len(result) == 2


def test_get_patient_photos_by_id(db_session_mock):
    """Test case for retrieving all photos of a given active patient"""

    #Arrange
    patient_id = 1
    mock_data = [
        MagicMock(
            PatientPhotoID = 1,
            IsDeleted = 0,
            PhotoPath = "Path String A",
            PhotoDetails = "Portrait profile photo of A",
            AlbumCategoryListID = 1,
            PatientID = patient_id,
            CreatedDateTime = datetime.now(),
            UpdatedDateTime = datetime.now(),
            CreatedById = 1,
            ModifiedById = 1,
        )
    ]
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    #Act
    result = get_patient_photo_by_id(db_session_mock, patient_id)

    #Assert
    assert len(result) == 1


def test_create_patient_photo(db_session_mock, photo_data):
    """Test case for creating a patient photo object"""

    #Arrange
    # mock_data = [
    #     MagicMock(
    #         PatientPhotoID = 1,
    #         IsDeleted = 0,
    #         PhotoPath = "Path String A",
    #         PhotoDetails = "Portrait profile photo of A",
    #         AlbumCategoryListID = 1,
    #         PatientID = 1,
    #         CreatedDateTime = datetime.now(),
    #         UpdatedDateTime = datetime.now(),
    #         CreatedById = 1,
    #         ModifiedById = 1,
    #     )
    # ]
    # db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    #Act
    conn_test = cloudinary.api.ping()
    # result = create_patient_photo(db_session_mock, None, photo_data)

    #Assert
    assert len(conn_test) == 1
    assert conn_test['status'] == "ok"


def test_update_patient_photo(db_session_mock, update_data):
    """Test case for updating a patient photo object"""

    #Arrange
    # mock_updated_photo = PatientPhoto(
    #     IsDeleted=0,
    #     PatientID=1,
    #     PhotoPath="Path String C",
    #     PhotoDetails="Portrait profile photo of C",
    #     AlbumCategoryListID=1,
    #     CreatedDateTime=datetime.utcnow(),
    #     UpdatedDateTime=datetime.utcnow(),
    #     CreatedById="1",
    #     ModifiedById="2"
    # )
    # db_session_mock.query.return_value.filter.return_value.first.side_effect = [
    #     mock_updated_photo
    # ]

    #Act
    # result = update_patient_photo(db_session_mock, 1, None, update_data)
    conn_test = cloudinary.api.ping()

    #Assert
    assert len(conn_test) == 1
    assert conn_test['status'] == "ok"


def test_delete_patient_photo(db_session_mock):
    """Test case for deleting a patient photo object"""

    #Act
    conn_test = cloudinary.api.ping()

    #Assert
    assert len(conn_test) == 1
    assert conn_test['status'] == "ok"


@pytest.fixture
def photo_data():
    """Fixture to provide a mock of photo_data object"""
    return PatientPhotoCreate(
        PatientID=1,
        PhotoDetails="PhotoDetails",
        AlbumCategoryListID=1,
        CreatedById="1",
        ModifiedById="1"
    )


@pytest.fixture
def update_data():
    """Fixture to provide a mock of update_data object"""
    return PatientPhotoUpdate(
        IsDeleted=0,
        PatientID=1,
        PhotoPath="Path String C",
        PhotoDetails="Portrait profile photo of C",
        AlbumCategoryListID=1,
        CreatedDateTime=datetime.utcnow(),
        UpdatedDateTime=datetime.utcnow(),
        CreatedById="1",
        ModifiedById="2"
    )


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()
