from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.crud.patient_list_crud import (
    create_list_item,
    delete_list_item,
    get_all_list_types,
    get_list,
    update_list_item,
)
from app.schemas.patient_list import PatientListCreate, PatientListUpdate
from tests.utils.mock_db import get_db_session_mock


def test_get_all_list_types(db_session_mock):
    mock_data = [
        MagicMock(id=1, type="diet", value="Vegetarian"),
        MagicMock(id=2, type="diet", value="Vegan"),
    ]
    db_session_mock.query.return_value.all.return_value = mock_data

    result = get_all_list_types(db_session_mock)

    assert len(result) == 2
    assert result[0].type == "diet"


def test_get_list_by_type(db_session_mock):
    mock_data = [MagicMock(id=1, type="diet", value="Vegetarian")]
    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_data

    result = get_list(db_session_mock, "diet")

    assert len(result) == 1
    assert result[0].value == "Vegetarian"


def test_get_list_by_type_and_id(db_session_mock):
    mock_data = [MagicMock(id=1, type="diet", value="Vegetarian")]
    db_session_mock.query.return_value.filter.return_value.filter.return_value.all.return_value = mock_data

    result = get_list(db_session_mock, "diet", item_id=1)

    assert len(result) == 1
    assert result[0].id == 1


@patch("app.crud.patient_list_crud.log_crud_action")
def test_create_list_item(mock_log, db_session_mock, list_create):
    result = create_list_item(db_session_mock, list_create)

    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.type == list_create.type
    assert result.value == list_create.value


@patch("app.crud.patient_list_crud.log_crud_action")
def test_update_list_item_found(mock_log, db_session_mock, list_update):
    mock_item = MagicMock(id=1, type="diet", value="Vegetarian")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_item

    result = update_list_item(db_session_mock, 1, list_update)

    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_item)
    assert result is mock_item


def test_update_list_item_not_found(db_session_mock, list_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = update_list_item(db_session_mock, 999, list_update)

    assert result is None


@patch("app.crud.patient_list_crud.log_crud_action")
def test_delete_list_item_found(mock_log, db_session_mock):
    mock_item = MagicMock(id=1, type="diet", value="Vegetarian")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_item

    result = delete_list_item(db_session_mock, 1)

    db_session_mock.delete.assert_called_once_with(mock_item)
    db_session_mock.commit.assert_called_once()
    assert result is mock_item


def test_delete_list_item_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_list_item(db_session_mock, 999)

    assert result is None


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def list_create():
    return PatientListCreate(
        type="diet",
        value="Vegetarian",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )


@pytest.fixture
def list_update():
    return PatientListUpdate(
        type="diet",
        value="Vegan",
        modifiedDate=datetime.now(),
        ModifiedById="1",
    )
