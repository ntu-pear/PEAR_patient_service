from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.crud.patient_list_language_crud import (
    create_patient_list_language,
    delete_patient_list_language,
    get_all_patient_list_language,
    get_patient_list_language,
    update_patient_list_language,
)
from app.schemas.patient_list_language import (
    PatientListLanguageCreate,
    PatientListLanguageUpdate,
)
from tests.utils.mock_db import get_db_session_mock


def test_get_language_found(db_session_mock):
    mock_lang = MagicMock(id=1, value="English", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_lang

    result = get_patient_list_language(db_session_mock, 1)

    assert result is mock_lang


def test_get_language_not_found(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_patient_list_language(db_session_mock, 999)

    assert exc_info.value.status_code == 404


def test_get_all_languages(db_session_mock):
    mock_data = [
        MagicMock(id=1, value="English", isDeleted="0"),
        MagicMock(id=2, value="Mandarin", isDeleted="0"),
    ]
    db_session_mock.query.return_value.filter.return_value.all.return_value = mock_data

    result = get_all_patient_list_language(db_session_mock)

    assert len(result) == 2


def test_create_language_happy_path(db_session_mock, language_create):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = create_patient_list_language(db_session_mock, language_create)

    db_session_mock.add.assert_called_once_with(result)
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)


def test_create_language_duplicate_raises_400(db_session_mock, language_create):
    mock_existing = MagicMock(id=1, value="English", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing

    with pytest.raises(HTTPException) as exc_info:
        create_patient_list_language(db_session_mock, language_create)

    assert exc_info.value.status_code == 400


def test_update_language_happy_path(db_session_mock, language_update):
    mock_lang = MagicMock(id=1, value="English", isDeleted="0")

    mock_find_query = MagicMock()
    mock_find_query.filter.return_value.first.return_value = mock_lang

    mock_dup_query = MagicMock()
    mock_dup_query.filter.return_value.first.return_value = None

    db_session_mock.query.side_effect = [mock_find_query, mock_dup_query]

    result = update_patient_list_language(db_session_mock, 1, language_update)

    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_lang)
    assert result is mock_lang


def test_update_language_not_found_raises_404(db_session_mock, language_update):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_patient_list_language(db_session_mock, 999, language_update)

    assert exc_info.value.status_code == 404


def test_update_language_duplicate_raises_400(db_session_mock, language_update):
    mock_lang = MagicMock(id=1, value="English", isDeleted="0")
    mock_duplicate = MagicMock(id=2, value="Mandarin", isDeleted="0")

    mock_find_query = MagicMock()
    mock_find_query.filter.return_value.first.return_value = mock_lang

    mock_dup_query = MagicMock()
    mock_dup_query.filter.return_value.first.return_value = mock_duplicate

    db_session_mock.query.side_effect = [mock_find_query, mock_dup_query]

    with pytest.raises(HTTPException) as exc_info:
        update_patient_list_language(db_session_mock, 1, language_update)

    assert exc_info.value.status_code == 400


def test_delete_language_happy_path(db_session_mock):
    mock_lang = MagicMock(id=1, value="English", isDeleted="0")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_lang

    result = delete_patient_list_language(db_session_mock, 1)

    assert mock_lang.isDeleted == "1"
    db_session_mock.commit.assert_called_once()
    assert result is mock_lang


def test_delete_language_not_found_raises_404(db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_patient_list_language(db_session_mock, 999)

    assert exc_info.value.status_code == 404


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def language_create():
    return PatientListLanguageCreate(value="English")


@pytest.fixture
def language_update():
    return PatientListLanguageUpdate(value="Mandarin")
