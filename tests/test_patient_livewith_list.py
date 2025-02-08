import pytest
from app.crud.patient_livewith_crud import (
    create_livewith_type,
    get_all_livewith_types,
    get_livewith_type_by_id,
    update_livewith_type,
    delete_livewith_type,
)
from app.schemas.patient_livewith_list import PatientLiveWithListCreate, PatientLiveWithListUpdate
from app.models.patient_livewith_list_model import PatientLiveWithList

from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_livewith_type(
    db_session_mock,
    livewith_type_create,
):
    """Test case for creating a livewith type."""
    # Arrange

    # Act
    result = create_livewith_type(db_session_mock, livewith_type_create)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Alone"
    assert result.IsDeleted == "0"


def test_get_all_livewith_types(db_session_mock):
    """Test case for retrieving all livewith types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_livewith_types()

    # Act
    result = get_all_livewith_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Alone"
    assert result[1].Value == "Family"


def test_get_livewith_type_by_id(db_session_mock):
    """Test case for retrieving a livewith type by ID."""
    # Arrange
    mock_livewith_type = PatientLiveWithList(
        Id=1,
        Value="Alone",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_livewith_type
    )

    # Act
    result = get_livewith_type_by_id(db_session_mock, mock_livewith_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientLiveWithList)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.Id == mock_livewith_type.Id
    assert result.Value == mock_livewith_type.Value
    assert result.IsDeleted == mock_livewith_type.IsDeleted


def test_update_livewith_type(db_session_mock):
    """Test case for updating a livewith type."""
    # Arrange
    livewith_type_update = PatientLiveWithListUpdate(Value="Siblings", IsDeleted="0")
    mock_livewith_type = PatientLiveWithList(
        Id=1,
        Value="Alone",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_livewith_type
    )

    # Act
    result = update_livewith_type(
        db_session_mock,
        mock_livewith_type.Id,
        livewith_type_update
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_livewith_type)
    assert result.Value == livewith_type_update.Value


def test_delete_livewith_type(db_session_mock):
    """Test case for deleting (soft-deleting) a livewith type."""
    # Arrange
    mock_livewith_type = PatientLiveWithList(
        Id=1,
        Value="Alone",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_livewith_type
    )

    # Act
    result = delete_livewith_type(
        db_session_mock, mock_livewith_type.Id
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


@pytest.fixture
def livewith_type_create():
    """Fixture to provide a mock PatientLiveWithListCreate object."""
    return PatientLiveWithListCreate(Value="Alone", IsDeleted="0")


## MOCK DATA ##
def get_mock_livewith_types():
    """Return a list of mock PatientLiveWithList objects."""
    return [
        PatientLiveWithList(Id=1, Value="Alone", IsDeleted="0"),
        PatientLiveWithList(Id=2, Value="Family", IsDeleted="0"),
    ]
