from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.crud.patient_guardian_relationship_mapping_crud import (
    create_relationship_mapping,
    delete_relationship_mapping,
    get_relationship_mapping,
    get_relationshipId_by_relationshipName,
    update_relationship_mapping,
)
from app.schemas.patient_guardian_relationship_mapping import (
    PatientGuardianRelationshipMappingCreate,
    PatientGuardianRelationshipMappingUpdate,
)
from tests.utils.mock_db import get_db_session_mock


def test_get_relationship_mapping_found(db_session_mock):
    mock_mapping = MagicMock(id=1, relationshipName="Son", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mapping

    result = get_relationship_mapping(db_session_mock, 1)

    assert result is mock_mapping


def test_get_relationship_mapping_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = get_relationship_mapping(db_session_mock, 999)

    assert result is None


def test_get_relationship_by_name_found(db_session_mock):
    mock_mapping = MagicMock(id=1, relationshipName="Son", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mapping

    result = get_relationshipId_by_relationshipName(db_session_mock, "Son")

    assert result is mock_mapping
    assert result.relationshipName == "Son"


def test_get_relationship_by_name_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = get_relationshipId_by_relationshipName(db_session_mock, "Unknown")

    assert result is None


@patch("app.crud.patient_guardian_relationship_mapping_crud.log_crud_action")
def test_create_relationship_mapping(mock_log, db_session_mock, relationship_create):
    result = create_relationship_mapping(db_session_mock, relationship_create)

    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.relationshipName == relationship_create.relationshipName


@patch("app.crud.patient_guardian_relationship_mapping_crud.log_crud_action")
def test_update_relationship_mapping_found(mock_log, db_session_mock, relationship_update):
    mock_mapping = MagicMock(id=1, relationshipName="Son", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mapping

    result = update_relationship_mapping(db_session_mock, 1, relationship_update)

    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_mapping)
    assert result is mock_mapping


def test_update_relationship_mapping_not_found(db_session_mock, relationship_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = update_relationship_mapping(db_session_mock, 999, relationship_update)

    assert result is None


@patch("app.crud.patient_guardian_relationship_mapping_crud.log_crud_action")
def test_delete_relationship_mapping_found(mock_log, db_session_mock):
    mock_mapping = MagicMock(id=1, relationshipName="Son", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_mapping

    result = delete_relationship_mapping(db_session_mock, 1)

    assert mock_mapping.isDeleted == "1"
    db_session_mock.commit.assert_called_once()
    assert result is mock_mapping


def test_delete_relationship_mapping_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_relationship_mapping(db_session_mock, 999)

    assert result is None


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def relationship_create():
    return PatientGuardianRelationshipMappingCreate(
        isDeleted="0",
        relationshipName="Son",
    )


@pytest.fixture
def relationship_update():
    return PatientGuardianRelationshipMappingUpdate(
        isDeleted="0",
        relationshipName="Daughter",
    )
