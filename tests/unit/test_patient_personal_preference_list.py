"""
Unit Tests – Patient Personal Preference List CRUD

File: tests/unit/test_patient_personal_preference_list.py
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_personal_preference_list_crud import (
    create_preference_list,
    delete_preference_list,
    get_preference_list_by_id,
    get_preference_lists,
    update_preference_list,
)
from app.schemas.patient_personal_preference_list import (
    PatientPersonalPreferenceListCreate,
    PatientPersonalPreferenceListUpdate,
)
from tests.utils.mock_db import get_db_session_mock

USER_ID = "test_user"
USER_FULL_NAME = "Test User"


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


def _make_list_item(id_=1, ptype="LikesDislikes", name="Reading"):
    item = mock.MagicMock()
    item.Id = id_
    item.PreferenceType = ptype
    item.PreferenceName = name
    item.IsDeleted = "0"
    item.CreatedDate = datetime(2024, 1, 1)
    item.ModifiedDate = datetime(2024, 1, 1)
    item.CreatedByID = USER_ID
    item.ModifiedByID = USER_ID
    return item


def _mock_query_chain(db_session_mock, count=0, all_=None, first=None):
    """Set up a standard query chain on the mock db."""
    q = mock.MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.count.return_value = count
    q.all.return_value = all_ or []
    q.first.return_value = first
    db_session_mock.query.return_value = q
    return q


# ---------------------------------------------------------------------------
# GET LIST
# ---------------------------------------------------------------------------

def test_get_preference_lists_returns_all(db_session_mock):
    """Retrieves all active preference list items with pagination."""
    items = [
        _make_list_item(1, "LikesDislikes", "Reading"),
        _make_list_item(2, "Habit",         "Snacking"),
        _make_list_item(3, "Hobby",         "Fishing"),
    ]
    _mock_query_chain(db_session_mock, count=3, all_=items)

    result, total, pages = get_preference_lists(db_session_mock, pageNo=0, pageSize=10)

    assert len(result) == 3
    assert total == 3
    assert pages == 1


def test_get_preference_lists_pagination_total_pages(db_session_mock):
    """Total pages is calculated correctly."""
    _mock_query_chain(db_session_mock, count=15, all_=[_make_list_item(i) for i in range(1, 6)])

    _, total, pages = get_preference_lists(db_session_mock, pageNo=0, pageSize=5)

    assert total == 15
    assert pages == 3


def test_get_preference_lists_filter_by_valid_type(db_session_mock):
    """Filtering by a valid preference type works."""
    items = [_make_list_item(1, "Hobby", "Fishing")]
    _mock_query_chain(db_session_mock, count=1, all_=items)

    result, total, _ = get_preference_lists(db_session_mock, preference_type="Hobby")

    assert total == 1
    assert result[0].PreferenceType == "Hobby"


def test_get_preference_lists_filter_by_ALL_skips_type_filter(db_session_mock):
    """Passing ALL as preferenceType returns all records."""
    items = [_make_list_item(i) for i in range(1, 4)]
    _mock_query_chain(db_session_mock, count=3, all_=items)

    _, total, _ = get_preference_lists(db_session_mock, preference_type="ALL")

    assert total == 3


def test_get_preference_lists_invalid_type_raises_400(db_session_mock):
    """Invalid preferenceType raises 400."""
    _mock_query_chain(db_session_mock, count=0, all_=[])

    with pytest.raises(HTTPException) as exc:
        get_preference_lists(db_session_mock, preference_type="InvalidType")

    assert exc.value.status_code == 400
    assert "Invalid preferenceType" in exc.value.detail


def test_get_preference_lists_empty_db(db_session_mock):
    """Empty DB returns empty list and zero counts."""
    _mock_query_chain(db_session_mock, count=0, all_=[])

    result, total, pages = get_preference_lists(db_session_mock)

    assert result == []
    assert total == 0
    assert pages == 0


# ---------------------------------------------------------------------------
# GET BY ID
# ---------------------------------------------------------------------------

def test_get_preference_list_by_id_found(db_session_mock):
    """Returns the item when it exists."""
    item = _make_list_item(1, "LikesDislikes", "Reading")
    db_session_mock.query.return_value.filter.return_value.first.return_value = item

    result = get_preference_list_by_id(db_session_mock, 1)

    assert result is not None
    assert result.Id == 1
    assert result.PreferenceName == "Reading"


def test_get_preference_list_by_id_not_found(db_session_mock):
    """Returns None when the item does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = get_preference_list_by_id(db_session_mock, 999)

    assert result is None


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def test_create_preference_list_likes_dislikes_success(db_session_mock):
    """Successfully creates a LikesDislikes item."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceListCreate(
        PreferenceType="LikesDislikes", PreferenceName="Dancing"
    )

    with mock.patch("app.crud.patient_personal_preference_list_crud.PatientPersonalPreferenceList") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 1
        instance.PreferenceType = "LikesDislikes"
        instance.PreferenceName = "Dancing"
        instance.IsDeleted = "0"
        MockModel.return_value = instance

        result = create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert result.PreferenceType == "LikesDislikes"
    assert result.PreferenceName == "Dancing"


def test_create_preference_list_habit_success(db_session_mock):
    """Successfully creates a Habit item."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceListCreate(
        PreferenceType="Habit", PreferenceName="Snacking"
    )

    with mock.patch("app.crud.patient_personal_preference_list_crud.PatientPersonalPreferenceList") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 2
        instance.PreferenceType = "Habit"
        instance.PreferenceName = "Snacking"
        instance.IsDeleted = "0"
        MockModel.return_value = instance

        result = create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()
    assert result.PreferenceType == "Habit"


def test_create_preference_list_hobby_success(db_session_mock):
    """Successfully creates a Hobby item."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceListCreate(
        PreferenceType="Hobby", PreferenceName="Fishing"
    )

    with mock.patch("app.crud.patient_personal_preference_list_crud.PatientPersonalPreferenceList") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 3
        instance.PreferenceType = "Hobby"
        instance.PreferenceName = "Fishing"
        instance.IsDeleted = "0"
        MockModel.return_value = instance

        result = create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()
    assert result.PreferenceType == "Hobby"


def test_create_preference_list_invalid_type_raises_400(db_session_mock):
    """CRUD guard rejects invalid PreferenceType before touching DB."""
    payload = mock.MagicMock()
    payload.PreferenceType = "BadType"
    payload.PreferenceName = "Something"
    payload.model_dump.return_value = {"PreferenceType": "BadType", "PreferenceName": "Something"}

    with pytest.raises(HTTPException) as exc:
        create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "PreferenceType must be one of" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_list_duplicate_raises_400(db_session_mock):
    """Duplicate (same type + name) raises 400 and does not write to DB."""
    existing = _make_list_item(1, "LikesDislikes", "Reading")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing

    payload = PatientPersonalPreferenceListCreate(
        PreferenceType="LikesDislikes", PreferenceName="Reading"
    )

    with pytest.raises(HTTPException) as exc:
        create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "already exists" in exc.value.detail
    db_session_mock.add.assert_not_called()


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def test_update_preference_list_name_success(db_session_mock):
    """Successfully updates PreferenceName."""
    existing = _make_list_item(1, "LikesDislikes", "Old Name")

    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        existing,  # fetch record
        None,      # duplicate check
    ]

    payload = PatientPersonalPreferenceListUpdate(PreferenceName="New Name")

    with mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        result = update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.PreferenceName == "New Name"
    assert result.ModifiedByID == USER_ID


def test_update_preference_list_type_success(db_session_mock):
    """Successfully updates PreferenceType."""
    existing = _make_list_item(1, "LikesDislikes", "Reading")

    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        existing,
        None,
    ]

    payload = PatientPersonalPreferenceListUpdate(PreferenceType="Hobby")

    with mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        result = update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.PreferenceType == "Hobby"


def test_update_preference_list_not_found_returns_none(db_session_mock):
    """Returns None when the record does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceListUpdate(PreferenceName="Anything")

    result = update_preference_list(db_session_mock, 999, payload, USER_ID, USER_FULL_NAME)

    assert result is None
    db_session_mock.commit.assert_not_called()


def test_update_preference_list_invalid_type_raises_400(db_session_mock):
    """Updating to an invalid PreferenceType raises 400."""
    existing = _make_list_item(1, "LikesDislikes", "Reading")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing

    payload = PatientPersonalPreferenceListUpdate()
    payload.model_dump = mock.MagicMock(return_value={"PreferenceType": "BadType"})

    with pytest.raises(HTTPException) as exc:
        update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "PreferenceType must be one of" in exc.value.detail


def test_update_preference_list_invalid_type_raises_400(db_session_mock):
    """Updating to an invalid PreferenceType raises 400."""
    existing = _make_list_item(1, "LikesDislikes", "Reading")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing

    # Use MagicMock instead of real Pydantic model so model_dump can be mocked
    payload = mock.MagicMock(spec=None)
    payload.model_dump = mock.MagicMock(return_value={"PreferenceType": "BadType"})

    with pytest.raises(HTTPException) as exc:
        update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "PreferenceType must be one of" in exc.value.detail


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def test_delete_preference_list_success(db_session_mock):
    """Successfully soft deletes a preference list item."""
    existing = _make_list_item(1, "LikesDislikes", "Reading")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing

    with mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        result = delete_preference_list(db_session_mock, 1, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedByID == USER_ID


def test_delete_preference_list_not_found_returns_none(db_session_mock):
    """Returns None when the record does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_preference_list(db_session_mock, 999, USER_ID, USER_FULL_NAME)

    assert result is None
    db_session_mock.commit.assert_not_called()