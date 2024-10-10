import pytest
from unittest import mock
from app.crud.allergy_reaction_type_crud import create_reaction_type, get_all_reaction_types
from app.schemas.allergy_reaction_type import AllergyReactionTypeCreate
from app.models.allergy_reaction_type_model import AllergyReactionType

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    db_mock = mock.MagicMock()
    return db_mock

@pytest.fixture
def allergy_reaction_type_create():
    """Fixture to provide a mock AllergyReactionTypeCreate object."""
    return AllergyReactionTypeCreate(Value="Mock 1", Active="1")

def test_create_reaction_type(db_session_mock, allergy_reaction_type_create):
    # Arrange
    created_by = 1

    # Act
    result = create_reaction_type(db_session_mock, allergy_reaction_type_create, created_by)

    # Assert
    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.Value == "Mock 1"
    assert result.Active == "1"
    assert result.createdById == created_by

def test_get_all_reaction_types(db_session_mock):
    # Arrange
    db_session_mock.query.return_value.all.return_value = get_mock_allergy_reaction_types()

    # Act
    result = get_all_reaction_types(db_session_mock)

    # Assert
    assert len(result) == 2
    assert result[0].Value == "Rashes"
    assert result[1].Value == "Sneezing"

## MOCK DATA ##
def get_mock_allergy_reaction_types():
    """Return a list of mock AllergyReactionType objects."""
    return [
        AllergyReactionType(AllergyReactionTypeID=1, Value="Rashes", Active="1"),
        AllergyReactionType(AllergyReactionTypeID=2, Value="Sneezing", Active="1"),
    ]

