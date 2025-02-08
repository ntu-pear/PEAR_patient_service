import pytest
from app.crud.patient_pet_crud import (
    create_pet_type,
    get_all_pet_types,
    get_pet_type_by_id,
    update_pet_type,
    delete_pet_type,
)
from app.schemas.patient_pet_list import PatientPetListCreate, PatientPetListUpdate
from app.models.patient_pet_list_model import PatientPetList

from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_pet_type(
    db_session_mock,
    pet_type_create,
):
    """Test case for creating a pet type."""
    # Arrange

    # Act
    result = create_pet_type(db_session_mock, pet_type_create)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Bird"
    assert result.IsDeleted == "0"


def test_get_all_pet_types(db_session_mock):
    """Test case for retrieving all pet types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_pet_types()

    # Act
    result = get_all_pet_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Bird"
    assert result[1].Value == "Dog"


def test_get_pet_type_by_id(db_session_mock):
    """Test case for retrieving a pet type by ID."""
    # Arrange
    mock_pet_type = PatientPetList(
        Id=1,
        Value="Bird",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_pet_type
    )

    # Act
    result = get_pet_type_by_id(db_session_mock, mock_pet_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientPetList)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.Id == mock_pet_type.Id
    assert result.Value == mock_pet_type.Value
    assert result.IsDeleted == mock_pet_type.IsDeleted


def test_update_pet_type(db_session_mock):
    """Test case for updating a pet type."""
    # Arrange
    pet_type_update = PatientPetListUpdate(Value="Parrot", IsDeleted="0")
    mock_pet_type = PatientPetList(
        Id=1,
        Value="Bird",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_pet_type
    )

    # Act
    result = update_pet_type(
        db_session_mock,
        mock_pet_type.Id,
        pet_type_update
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_pet_type)
    assert result.Value == pet_type_update.Value


def test_delete_pet_type(db_session_mock):
    """Test case for deleting (soft-deleting) a pet type."""
    # Arrange
    mock_pet_type = PatientPetList(
        Id=1,
        Value="Bird",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_pet_type
    )

    # Act
    result = delete_pet_type(
        db_session_mock, mock_pet_type.Id
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def pet_type_create():
    """Fixture to provide a mock PatientPetListCreate object."""
    return PatientPetListCreate(Value="Bird", IsDeleted="0")


## MOCK DATA ##
def get_mock_pet_types():
    """Return a list of mock PatientPetList objects."""
    return [
        PatientPetList(Id=1, Value="Bird", IsDeleted="0"),
        PatientPetList(Id=2, Value="Dog", IsDeleted="0"),
    ]
