import pytest
from app.crud.patient_diet_crud import (
    create_diet_type,
    get_all_diet_types,
    get_diet_type_by_id,
    update_diet_type,
    delete_diet_type,
)
from app.schemas.patient_diet_list import PatientDietListCreate, PatientDietListUpdate
from app.models.patient_diet_list_model import PatientDietList

from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_diet_type(
    db_session_mock,
    diet_type_create,
):
    """Test case for creating a diet type."""
    # Arrange
    created_by = 1

    # Act
    result = create_diet_type(db_session_mock, diet_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Diabetic"
    assert result.IsDeleted == "0"
    assert result.CreatedById == created_by


def test_get_all_diet_types(db_session_mock):
    """Test case for retrieving all diet types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_diet_types()

    # Act
    result = get_all_diet_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Diabetic"
    assert result[1].Value == "Hypertension"


def test_get_diet_type_by_id(db_session_mock):
    """Test case for retrieving a diet type by ID."""
    # Arrange
    mock_diet_type = PatientDietList(
        Id=1,
        Value="Diabetic",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_diet_type
    )

    # Act
    result = get_diet_type_by_id(db_session_mock, mock_diet_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientDietList)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.Id == mock_diet_type.Id
    assert result.Value == mock_diet_type.Value
    assert result.IsDeleted == mock_diet_type.IsDeleted


def test_update_diet_type(db_session_mock):
    """Test case for updating a diet type."""
    # Arrange
    modified_by = 2
    diet_type_update = PatientDietListUpdate(Value="Diabetes II", IsDeleted="0")
    mock_diet_type = PatientDietList(
        Id=1,
        Value="Diabetes",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_diet_type
    )

    # Act
    result = update_diet_type(
        db_session_mock,
        mock_diet_type.Id,
        diet_type_update,
        modified_by,
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_diet_type)
    assert result.Value == diet_type_update.Value
    assert result.ModifiedById == modified_by


def test_delete_diet_type(db_session_mock):
    """Test case for deleting (soft-deleting) a diet type."""
    # Arrange
    modified_by = 2
    mock_diet_type = PatientDietList(
        Id=1,
        Value="Diabetes",
        IsDeleted="0",
        CreatedById=1,
        ModifiedById=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_diet_type
    )

    # Act
    result = delete_diet_type(
        db_session_mock, mock_diet_type.Id, modified_by
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
def diet_type_create():
    """Fixture to provide a mock PatientDietListCreate object."""
    return PatientDietListCreate(Value="Diabetic", IsDeleted="0")


## MOCK DATA ##
def get_mock_diet_types():
    """Return a list of mock PatientDietList objects."""
    return [
        PatientDietList(Id=1, Value="Diabetic", IsDeleted="0"),
        PatientDietList(Id=2, Value="Hypertension", IsDeleted="0"),
    ]
