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
            ModifiedById = 1
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
            ModifiedById = 1
        ),
    ]

    db_session_mock.query.filter.all = mock_data

    #Act
    result = get_patient_photos(db_session_mock)

    #Assert
    assert len(result) == 2


# def test_get_patient_photos_by_id(db_session_mock, patient_id):
#     """Test case for retrieving all photos of a given active patient"""

#     #Arrange
#     patient_id = 1
#     mock_data = [
#         MagicMock(
#             PatientPhotoID = 1,
#             IsDeleted = 0,
#             PhotoPath = "Path String A",
#             PhotoDetails = "Portrait profile photo of A",
#             AlbumCategoryListID = 1,
#             PatientID = 1,
#             CreatedDateTime = datetime.now(),
#             UpdatedDateTime = datetime.now(),
#             CreatedById = 1,
#             ModifiedById = 1
#         ),
#         MagicMock(
#             PatientPhotoID = 2,
#             IsDeleted = 0,
#             PhotoPath = "Path String B",
#             PhotoDetails = "Portrait profile photo of B",
#             AlbumCategoryListID = 1,
#             PatientID = 2,
#             CreatedDateTime = datetime.now(),
#             UpdatedDateTime = datetime.now(),
#             CreatedById = 1,
#             ModifiedById = 1
#         ),
#     ]
#     db_session_mock.query.return_value.join.return_value.join.return_value.all.return_value = mock_data

#     #Act
#     result = get_patient_photo_by_id(db_session_mock, patient_id)

#     #Assert
#     assert len(result) == 1

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


# @pytest.fixture
# def mock_patient_photo():
#     return PatientPhoto(PatientPhotoID = 1, IsDeleted = 0, PhotoPath = "Path String A", PhotoDetails = "Portrait profile photo of A",  AlbumCategoryListID = 1,
#                          PatientID = 1, CreatedDateTime = datetime.now(), UpdatedDateTime = datetime.now(), CreatedById = 1, ModifiedById = 1,)