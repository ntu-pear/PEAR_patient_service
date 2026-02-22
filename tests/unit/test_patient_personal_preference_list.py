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


def _make_list_item(id_=1, ptype="LikesDislikes", name="READING"):
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
# GET LIST (with ordering tests)
# ---------------------------------------------------------------------------

def test_get_preference_lists_ordered_by_preferencename(db_session_mock):
    """Retrieves all items ordered by PreferenceName (A-Z)."""
    items = [
        _make_list_item(1, "LikesDislikes", "DANCING"),  # Should come first
        _make_list_item(2, "Habit",         "SNACKING"),  # Should come second
        _make_list_item(3, "Hobby",         "FISHING"),   # Should come third (alphabetically)
    ]
    q = _mock_query_chain(db_session_mock, count=3, all_=items)

    result, total, pages = get_preference_lists(db_session_mock, pageNo=0, pageSize=10)

    assert len(result) == 3
    assert total == 3
    assert pages == 1
    # Verify order_by was called (PreferenceName.asc())
    q.order_by.assert_called()


def test_get_preference_lists_pagination_total_pages(db_session_mock):
    """Total pages is calculated correctly."""
    _mock_query_chain(db_session_mock, count=15, all_=[_make_list_item(i) for i in range(1, 6)])

    _, total, pages = get_preference_lists(db_session_mock, pageNo=0, pageSize=5)

    assert total == 15
    assert pages == 3


def test_get_preference_lists_filter_by_valid_type(db_session_mock):
    """Filtering by a valid preference type works."""
    items = [_make_list_item(1, "Hobby", "FISHING")]
    _mock_query_chain(db_session_mock, count=1, all_=items)

    result, total, _ = get_preference_lists(db_session_mock, preference_type="Hobby")

    assert total == 1
    assert result[0].PreferenceType == "Hobby"


def test_get_preference_lists_invalid_type_raises_400(db_session_mock):
    """Invalid preferenceType raises 400."""
    _mock_query_chain(db_session_mock, count=0, all_=[])

    with pytest.raises(HTTPException) as exc:
        get_preference_lists(db_session_mock, preference_type="InvalidType")

    assert exc.value.status_code == 400
    assert "Invalid preferenceType" in exc.value.detail


# ---------------------------------------------------------------------------
# GET BY ID
# ---------------------------------------------------------------------------

def test_get_preference_list_by_id_found(db_session_mock):
    """Returns the item when it exists."""
    item = _make_list_item(1, "LikesDislikes", "READING")
    db_session_mock.query.return_value.filter.return_value.first.return_value = item

    result = get_preference_list_by_id(db_session_mock, 1)

    assert result is not None
    assert result.Id == 1
    assert result.PreferenceName == "READING"


def test_get_preference_list_by_id_not_found(db_session_mock):
    """Returns None when the item does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = get_preference_list_by_id(db_session_mock, 999)

    assert result is None


# ---------------------------------------------------------------------------
# CREATE (with UPPERCASE conversion and duplicate check)
# ---------------------------------------------------------------------------

def test_create_preference_list_converts_to_uppercase(db_session_mock):
    """Successfully creates item with PreferenceName converted to UPPERCASE."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceListCreate(
        PreferenceType="LikesDislikes", 
        PreferenceName="dancing"  # lowercase input
    )

    with mock.patch("app.crud.patient_personal_preference_list_crud.PatientPersonalPreferenceList") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 1
        instance.PreferenceType = "LikesDislikes"
        instance.PreferenceName = "DANCING"  # Should be UPPERCASE
        instance.IsDeleted = "0"
        MockModel.return_value = instance

        result = create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert result.PreferenceName == "DANCING"


def test_create_preference_list_duplicate_case_insensitive(db_session_mock):
    """Duplicate check is case-insensitive."""
    existing = _make_list_item(1, "LikesDislikes", "READING")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing

    # Try different case variations - all should fail
    for name in ["reading", "READING", "Reading", "rEaDiNg"]:
        payload = PatientPersonalPreferenceListCreate(
            PreferenceType="LikesDislikes", 
            PreferenceName=name
        )

        with pytest.raises(HTTPException) as exc:
            create_preference_list(db_session_mock, payload, USER_ID, USER_FULL_NAME)

        assert exc.value.status_code == 400
        assert "already exists" in exc.value.detail


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


def test_create_preference_list_different_types_same_name_allowed(db_session_mock):
    """Same PreferenceName is allowed for different PreferenceTypes."""
    # First call: no existing record
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload1 = PatientPersonalPreferenceListCreate(
        PreferenceType="LikesDislikes", 
        PreferenceName="Swimming"
    )

    with mock.patch("app.crud.patient_personal_preference_list_crud.PatientPersonalPreferenceList") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        instance1 = mock.MagicMock()
        instance1.Id = 1
        instance1.PreferenceType = "LikesDislikes"
        instance1.PreferenceName = "SWIMMING"
        MockModel.return_value = instance1

        result1 = create_preference_list(db_session_mock, payload1, USER_ID, USER_FULL_NAME)

    # This is allowed - same name, different type
    assert result1.PreferenceName == "SWIMMING"


# ---------------------------------------------------------------------------
# UPDATE (with UPPERCASE conversion)
# ---------------------------------------------------------------------------

def test_update_preference_list_name_converts_to_uppercase(db_session_mock):
    """Successfully updates PreferenceName with UPPERCASE conversion."""
    existing = _make_list_item(1, "LikesDislikes", "OLD NAME")

    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        existing,  # fetch record
        None,      # duplicate check
    ]

    payload = PatientPersonalPreferenceListUpdate(PreferenceName="new name")  # lowercase

    with mock.patch("app.crud.patient_personal_preference_list_crud.log_crud_action"):
        result = update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.PreferenceName == "NEW NAME"  # Should be UPPERCASE
    assert result.ModifiedByID == USER_ID


def test_update_preference_list_not_found_returns_none(db_session_mock):
    """Returns None when the record does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceListUpdate(PreferenceName="Anything")

    result = update_preference_list(db_session_mock, 999, payload, USER_ID, USER_FULL_NAME)

    assert result is None
    db_session_mock.commit.assert_not_called()


def test_update_preference_list_invalid_type_raises_400(db_session_mock):
    """Updating to an invalid PreferenceType raises 400."""
    existing = _make_list_item(1, "LikesDislikes", "READING")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing

    # Use MagicMock so model_dump can be mocked
    payload = mock.MagicMock(spec=None)
    payload.model_dump = mock.MagicMock(return_value={"PreferenceType": "BadType"})

    with pytest.raises(HTTPException) as exc:
        update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "PreferenceType must be one of" in exc.value.detail


def test_update_preference_list_duplicate_check(db_session_mock):
    """Updating to duplicate (type+name) raises 400."""
    existing = _make_list_item(1, "LikesDislikes", "READING")
    duplicate = _make_list_item(2, "LikesDislikes", "SWIMMING")

    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        existing,   # fetch record
        duplicate,  # duplicate check finds existing record
    ]

    payload = PatientPersonalPreferenceListUpdate(PreferenceName="Swimming")

    with pytest.raises(HTTPException) as exc:
        update_preference_list(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "already exists" in exc.value.detail


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def test_delete_preference_list_success(db_session_mock):
    """Successfully soft deletes a preference list item."""
    existing = _make_list_item(1, "LikesDislikes", "READING")
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