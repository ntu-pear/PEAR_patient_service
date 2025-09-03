import pytest
from app.crud.patient_list_education_crud import (
    create_education_type,
    get_all_education_types,
    get_education_type_by_id,
    update_education_type,
    delete_education_type,
)
from app.schemas.patient_list_education import PatientEducationListTypeCreate, PatientEducationListTypeUpdate
from app.models.patient_list_education_model import PatientEducationList

from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_education_type(
    db_session_mock,
    education_type_create,
):
    """Test case for creating an education type."""
    # Arrange
    created_by = "1"

    # Act
    result = create_education_type(db_session_mock, education_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Primary or lower"
    assert result.IsDeleted == "0"
    assert result.CreatedById == created_by


def test_get_all_education_types(db_session_mock):
    """Test case for retrieving all education types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_education_types()

    # Act
    result = get_all_education_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Primary or lower"
    assert result[1].Value == "Secondary"


def test_get_education_type_by_id(db_session_mock):
    """Test case for retrieving an education type by ID."""
    # Arrange
    mock_education_type = PatientEducationList(
        Id=1,
        Value="Primary or lower",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_education_type
    )

    # Act
    result = get_education_type_by_id(db_session_mock, mock_education_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientEducationList)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.Id == mock_education_type.Id
    assert result.Value == mock_education_type.Value
    assert result.IsDeleted == mock_education_type.IsDeleted


def test_update_education_type(db_session_mock):
    """Test case for updating an education type."""
    # Arrange
    modified_by = "2"
    education_type_update = PatientEducationListTypeUpdate(Value="Junior College", IsDeleted="0",)
    mock_education_type = PatientEducationList(
        Id=1,
        Value="Primary or lower",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_education_type
    )

    # Act
    result = update_education_type(
        db_session_mock,
        mock_education_type.Id,
        education_type_update,
        modified_by,
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_education_type)
    assert result.Value == education_type_update.Value
    assert result.ModifiedById == modified_by


def test_delete_education_type(db_session_mock):
    """Test case for deleting (soft-deleting) an education type."""
    # Arrange
    modified_by = "2"
    mock_education_type = PatientEducationList(
        Id=1,
        Value="Primary or lower",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_education_type
    )

    # Act
    result = delete_education_type(
        db_session_mock, mock_education_type.Id, modified_by
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedById == modified_by


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def education_type_create():
    """Fixture to provide a mock PatientEducationListCreate object."""
    return PatientEducationListTypeCreate(Value="Primary or lower", IsDeleted="0")


## MOCK DATA ##
def get_mock_education_types():
    """Return a list of mock PatientEducationList objects."""
    return [
        PatientEducationList(Id=1, Value="Primary or lower", IsDeleted="0"),
        PatientEducationList(Id=2, Value="Secondary", IsDeleted="0"),
    ]
