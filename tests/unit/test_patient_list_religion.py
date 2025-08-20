import pytest
from app.crud.patient_list_religion_crud import (
    create_religion_type,
    get_all_religion_types,
    get_religion_type_by_id,
    update_religion_type,
    delete_religion_type,
)
from app.schemas.patient_list_religion import PatientReligionListTypeCreate, PatientReligionListTypeUpdate
from app.models.patient_list_religion_model import PatientReligionList

from datetime import datetime
from tests.utils.mock_db import get_db_session_mock


# Mocking the relevant models

def test_create_religion_type(
    db_session_mock,
    religion_type_create,
):
    """Test case for creating a religion type."""
    # Arrange
    created_by = "1"

    # Act
    result = create_religion_type(db_session_mock, religion_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Atheist"
    assert result.IsDeleted == "0"
    assert result.CreatedById == created_by


def test_get_all_religion_types(db_session_mock):
    """Test case for retrieving all religion types."""
    # Arrange
    db_session_mock.query.return_value.filter.return_value.all.return_value = get_mock_religion_types()

    # Act
    result = get_all_religion_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Atheist"
    assert result[1].Value == "Buddhist"


def test_get_religion_type_by_id(db_session_mock):
    """Test case for retrieving a religion type by ID."""
    # Arrange
    mock_religion_type = PatientReligionList(
        Id=1,
        Value="Atheist",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_religion_type
    )

    # Act
    result = get_religion_type_by_id(db_session_mock, mock_religion_type.Id)

    # Assert
    db_session_mock.query.assert_called_once_with(PatientReligionList)
    db_session_mock.query.return_value.filter.assert_called_once()
    assert result.Id == mock_religion_type.Id
    assert result.Value == mock_religion_type.Value
    assert result.IsDeleted == mock_religion_type.IsDeleted


def test_update_religion_type(db_session_mock):
    """Test case for updating a religion type."""
    # Arrange
    modified_by = "2"
    religion_type_update = PatientReligionListTypeUpdate(Value="Christian", IsDeleted="0")
    mock_religion_type = PatientReligionList(
        Id=1,
        Value="Atheist",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_religion_type
    )

    # Act
    result = update_religion_type(
        db_session_mock,
        mock_religion_type.Id,
        religion_type_update,
        modified_by,
    )

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_religion_type)
    assert result.Value == religion_type_update.Value
    assert result.ModifiedById == modified_by


def test_delete_religion_type(db_session_mock):
    """Test case for deleting (soft-deleting) a religion type."""
    # Arrange
    modified_by = "2"
    mock_religion_type = PatientReligionList(
        Id=1,
        Value="Atheist",
        IsDeleted="0",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = (
        mock_religion_type
    )

    # Act
    result = delete_religion_type(
        db_session_mock, mock_religion_type.Id, modified_by
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
def religion_type_create():
    """Fixture to provide a mock PatientReligionListCreate object."""
    return PatientReligionListTypeCreate(Value="Atheist", IsDeleted="0")


## MOCK DATA ##
def get_mock_religion_types():
    """Return a list of mock PatientReligionList objects."""
    return [
        PatientReligionList(Id=1, Value="Atheist", IsDeleted="0"),
        PatientReligionList(Id=2, Value="Buddhist", IsDeleted="0"),
    ]
