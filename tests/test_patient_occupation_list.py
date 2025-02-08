import pytest
from app.crud.patient_occupation_crud import (
    create_occupation_type,
    get_all_occupation_types,
    get_occupation_type_by_id,
    update_occupation_type,
    delete_occupation_type,
)
from app.schemas.patient_occupation_list import PatientOccupationListCreate, PatientOccupationListUpdate
from app.models.patient_occupation_list_model import PatientOccupationList

from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_occupation_type(
    db_session_mock,
    occupation_type_create,
):
    """Test case for creating an occupation type."""
    # Arrange

    # Act
    result = create_occupation_type(db_session_mock, occupation_type_create)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Accountant"
    assert result.IsDeleted == "0"


def test_get_all_occupation_types(db_session_mock):
    """Test case for retrieving all occupation types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_occupation_types()

    # Act
    result = get_all_occupation_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Accountant"
    assert result[1].Value == "Arts"


def test_get_occupation_type_by_id(db_session_mock):
    """Test case for retrieving an occupation type by ID."""
    # Arrange
    mock_occupation_type = PatientOccupationList(
        Id=1,
        Value="Accountant",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_occupation_type
    )

    # Act
    result = get_occupation_type_by_id(db_session_mock, mock_occupation_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientOccupationList)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.Id == mock_occupation_type.Id
    assert result.Value == mock_occupation_type.Value
    assert result.IsDeleted == mock_occupation_type.IsDeleted


def test_update_occupation_type(db_session_mock):
    """Test case for updating an occupation type."""
    # Arrange
    occupation_type_update = PatientOccupationListUpdate(Value="Accounting", IsDeleted="0")
    mock_occupation_type = PatientOccupationList(
        Id=1,
        Value="Accountant",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_occupation_type
    )

    # Act
    result = update_occupation_type(
        db_session_mock,
        mock_occupation_type.Id,
        occupation_type_update
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_occupation_type)
    assert result.Value == occupation_type_update.Value


def test_delete_occupation_type(db_session_mock):
    """Test case for deleting (soft-deleting) an occupation type."""
    # Arrange
    mock_occupation_type = PatientOccupationList(
        Id=1,
        Value="Accountant",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_occupation_type
    )

    # Act
    result = delete_occupation_type(
        db_session_mock, mock_occupation_type.Id
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def occupation_type_create():
    """Fixture to provide a mock PatientOccupationListCreate object."""
    return PatientOccupationListCreate(Value="Accountant", IsDeleted="0")


## MOCK DATA ##
def get_mock_occupation_types():
    """Return a list of mock PatientOccupationList objects."""
    return [
        PatientOccupationList(Id=1, Value="Accountant", IsDeleted="0"),
        PatientOccupationList(Id=2, Value="Arts", IsDeleted="0"),
    ]
