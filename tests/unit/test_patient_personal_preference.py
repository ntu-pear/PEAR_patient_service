"""
Unit Tests – Patient Personal Preference CRUD

File: tests/unit/test_patient_personal_preference.py
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_personal_preference_crud import (
    create_preference,
    delete_preference,
    get_patient_preferences,
    get_preference,
    get_preferences,
    update_preference,
)
from app.schemas.patient_personal_preference import (
    PatientPersonalPreferenceCreate,
    PatientPersonalPreferenceUpdate,
)
from tests.utils.mock_db import get_db_session_mock

USER_ID = "test_user"
USER_FULL_NAME = "Test User"


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


@pytest.fixture
def mock_patient():
    patient = mock.MagicMock()
    patient.id = 1
    patient.isDeleted = "0"
    return patient


@pytest.fixture
def mock_pref_list_likes():
    item = mock.MagicMock()
    item.Id = 10
    item.PreferenceType = "LikesDislikes"
    item.PreferenceName = "Reading"
    item.IsDeleted = "0"
    return item


@pytest.fixture
def mock_pref_list_habit():
    item = mock.MagicMock()
    item.Id = 20
    item.PreferenceType = "Habit"
    item.PreferenceName = "Snacking"
    item.IsDeleted = "0"
    return item


@pytest.fixture
def mock_pref_list_hobby():
    item = mock.MagicMock()
    item.Id = 30
    item.PreferenceType = "Hobby"
    item.PreferenceName = "Fishing"
    item.IsDeleted = "0"
    return item


def _make_preference(id_=1, patient_id=1, list_id=10, is_like="Y"):
    pref = mock.MagicMock()
    pref.Id = id_
    pref.PatientID = patient_id
    pref.PersonalPreferenceListID = list_id
    pref.IsLike = is_like
    pref.PreferenceRemarks = None
    pref.IsDeleted = "0"
    pref.CreatedDate = datetime(2024, 1, 1)
    pref.ModifiedDate = datetime(2024, 1, 1)
    pref.CreatedByID = USER_ID
    pref.ModifiedByID = USER_ID
    return pref


def _setup_query_sequence(db_session_mock, responses):
    """
    Set up db.query to return different mock query chains per call.
    Each entry in responses is the value returned by .first() for that call.
    """
    call_count = 0

    def side_effect(model):
        nonlocal call_count
        call_count += 1
        q = mock.MagicMock()
        q.filter.return_value = q
        q.options.return_value = q
        q.join.return_value = q
        q.order_value = q
        q.order_by.return_value = q
        q.offset.return_value = q
        q.limit.return_value = q
        q.count.return_value = 1
        q.all.return_value = []

        idx = call_count - 1
        if idx < len(responses):
            q.first.return_value = responses[idx]
        else:
            q.first.return_value = None

        return q

    db_session_mock.query.side_effect = side_effect


# ---------------------------------------------------------------------------
# GET ALL PREFERENCES
# ---------------------------------------------------------------------------

def test_get_preferences_returns_paginated_results(db_session_mock):
    """Returns all active preferences across all patients."""
    prefs = [_make_preference(i, patient_id=i) for i in range(1, 4)]

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.count.return_value = 3
    mock_query.all.return_value = prefs
    db_session_mock.query.return_value = mock_query

    result, total, pages = get_preferences(db_session_mock, pageNo=0, pageSize=10)

    assert len(result) == 3
    assert total == 3
    assert pages == 1


def test_get_preferences_empty(db_session_mock):
    """Empty DB returns empty list."""
    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.count.return_value = 0
    mock_query.all.return_value = []
    db_session_mock.query.return_value = mock_query

    result, total, pages = get_preferences(db_session_mock)

    assert result == []
    assert total == 0
    assert pages == 0


# ---------------------------------------------------------------------------
# GET PATIENT PREFERENCES
# ---------------------------------------------------------------------------

def test_get_patient_preferences_returns_for_patient(db_session_mock):
    """Returns preferences for a specific patient."""
    prefs = [_make_preference(1, patient_id=1)]

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.count.return_value = 1
    mock_query.all.return_value = prefs
    db_session_mock.query.return_value = mock_query

    result, total, pages = get_patient_preferences(db_session_mock, patient_id=1)

    assert len(result) == 1
    assert total == 1
    assert result[0].PatientID == 1


def test_get_patient_preferences_with_type_filter(db_session_mock):
    """Filtering by preference type applies join and filter."""
    prefs = [_make_preference(1, patient_id=1, list_id=20)]

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.count.return_value = 1
    mock_query.all.return_value = prefs
    db_session_mock.query.return_value = mock_query

    result, total, _ = get_patient_preferences(
        db_session_mock, patient_id=1, preference_type="Habit"
    )

    assert total == 1


# ---------------------------------------------------------------------------
# GET SINGLE PREFERENCE
# ---------------------------------------------------------------------------

def test_get_preference_found(db_session_mock):
    """Returns the preference when it exists."""
    pref = _make_preference(1)

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = pref
    db_session_mock.query.return_value = mock_query

    result = get_preference(db_session_mock, 1)

    assert result is not None
    assert result.Id == 1


def test_get_preference_not_found(db_session_mock):
    """Returns None when the preference does not exist."""
    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    db_session_mock.query.return_value = mock_query

    result = get_preference(db_session_mock, 999)

    assert result is None


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def test_create_preference_likes_dislikes_with_islike_y(
    db_session_mock, mock_patient, mock_pref_list_likes
):
    """Creates a LikesDislikes preference with IsLike='Y'."""
    created = _make_preference(1, patient_id=1, list_id=10, is_like="Y")

    _setup_query_sequence(db_session_mock, [
        mock_patient,           # _verify_patient_exists
        mock_pref_list_likes,   # _verify_preference_list_exists
        None,                   # duplicate check
        mock_patient,           # Fetch patient name for logging (after flush)
        created,                # reload after commit
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=10, IsLike="Y"
    )

    with mock.patch("app.crud.patient_personal_preference_crud.PatientPersonalPreference") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 1
        instance.PatientID = 1
        MockModel.return_value = instance

        result = create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert result.PatientID == 1


def test_create_preference_likes_dislikes_with_islike_n(
    db_session_mock, mock_patient, mock_pref_list_likes
):
    """Creates a LikesDislikes preference with IsLike='N'."""
    created = _make_preference(2, patient_id=1, list_id=10, is_like="N")

    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_likes,
        None,
        mock_patient,
        created,
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=10, IsLike="N"
    )

    with mock.patch("app.crud.patient_personal_preference_crud.PatientPersonalPreference") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 2
        MockModel.return_value = instance

        result = create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()
    assert result.IsLike == "N"


def test_create_preference_habit_with_null_islike(
    db_session_mock, mock_patient, mock_pref_list_habit
):
    """Creates a Habit preference with IsLike=None."""
    created = _make_preference(3, patient_id=1, list_id=20, is_like=None)

    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_habit,
        None,
        created,
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=20, IsLike=None
    )

    with mock.patch("app.crud.patient_personal_preference_crud.PatientPersonalPreference") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 3
        MockModel.return_value = instance

        result = create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()


def test_create_preference_hobby_with_null_islike(
    db_session_mock, mock_patient, mock_pref_list_hobby
):
    """Creates a Hobby preference with IsLike=None."""
    created = _make_preference(4, patient_id=1, list_id=30, is_like=None)

    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_hobby,
        None,
        created,
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=30, IsLike=None
    )

    with mock.patch("app.crud.patient_personal_preference_crud.PatientPersonalPreference") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 4
        MockModel.return_value = instance

        result = create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()


def test_create_preference_invalid_islike_value_raises_400(db_session_mock):
    """Invalid IsLike value is rejected with 400 before any DB call."""
    payload = mock.MagicMock()
    payload.IsLike = "string"
    payload.PatientID = 1
    payload.PersonalPreferenceListID = 10
    payload.model_dump.return_value = {
        "PatientID": 1,
        "PersonalPreferenceListID": 10,
        "IsLike": "string",
    }

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "IsLike must be" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_likes_dislikes_null_islike_raises_400(
    db_session_mock, mock_patient, mock_pref_list_likes
):
    """LikesDislikes with IsLike=None raises 400."""
    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_likes,
    ])

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=10, IsLike=None
    )

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "IsLike must be 'Y' or 'N'" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_habit_with_islike_raises_400(
    db_session_mock, mock_patient, mock_pref_list_habit
):
    """Habit preference with IsLike set raises 400."""
    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_habit,
    ])

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=20, IsLike="Y"
    )

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "IsLike must be null" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_hobby_with_islike_raises_400(
    db_session_mock, mock_patient, mock_pref_list_hobby
):
    """Hobby preference with IsLike set raises 400."""
    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_hobby,
    ])

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=30, IsLike="N"
    )

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "IsLike must be null" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_patient_not_found_raises_404(db_session_mock):
    """Non-existent PatientID raises 404."""
    _setup_query_sequence(db_session_mock, [None])  # patient not found

    payload = PatientPersonalPreferenceCreate(
        PatientID=9999, PersonalPreferenceListID=10, IsLike="Y"
    )

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 404
    assert "Patient with ID 9999" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_list_item_not_found_raises_404(
    db_session_mock, mock_patient
):
    """Non-existent PersonalPreferenceListID raises 404."""
    _setup_query_sequence(db_session_mock, [
        mock_patient,  # patient found
        None,          # list item not found
    ])

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=9999, IsLike="Y"
    )

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 404
    assert "Personal preference list item with ID 9999" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_duplicate_raises_400(
    db_session_mock, mock_patient, mock_pref_list_likes
):
    """Same patient + same list item raises 400."""
    existing = _make_preference(1, patient_id=1, list_id=10)

    _setup_query_sequence(db_session_mock, [
        mock_patient,
        mock_pref_list_likes,
        existing,   # duplicate found
    ])

    payload = PatientPersonalPreferenceCreate(
        PatientID=1, PersonalPreferenceListID=10, IsLike="Y"
    )

    with pytest.raises(HTTPException) as exc:
        create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "already has this personal preference recorded" in exc.value.detail
    db_session_mock.add.assert_not_called()


def test_create_preference_different_patients_same_list_item_allowed(
    db_session_mock, mock_pref_list_likes
):
    """Different patients can share the same preference list item."""
    patient2 = mock.MagicMock()
    patient2.id = 2
    patient2.isDeleted = "0"

    created = _make_preference(2, patient_id=2, list_id=10)

    _setup_query_sequence(db_session_mock, [
        patient2,              # patient 2 found
        mock_pref_list_likes,  # list item found
        None,                  # no duplicate for patient 2
        created,               # reload
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceCreate(
        PatientID=2, PersonalPreferenceListID=10, IsLike="Y"
    )

    with mock.patch("app.crud.patient_personal_preference_crud.PatientPersonalPreference") as MockModel, \
         mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        instance = mock.MagicMock()
        instance.Id = 2
        MockModel.return_value = instance

        result = create_preference(db_session_mock, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.add.assert_called_once()


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def test_update_preference_remarks_success(db_session_mock, mock_pref_list_likes):
    """Successfully updates PreferenceRemarks."""
    existing = _make_preference(1, patient_id=1, list_id=10, is_like="Y")
    updated = _make_preference(1, patient_id=1, list_id=10, is_like="Y")
    updated.PreferenceRemarks = "Updated remark"

    # Create mock patient for logging queries
    mock_patient = mock.MagicMock()
    mock_patient.id = 1
    mock_patient.name = "Test patient"

    _setup_query_sequence(db_session_mock, [
        existing,            # fetch record
        mock_pref_list_likes, # load current list type
        None,                # duplicate check
        mock_patient,        # fetch patient name for logging
        mock_pref_list_likes, # fetch pref list name for logging
        updated,             # reload after commit
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceUpdate(PreferenceRemarks="Updated remark")

    with mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        result = update_preference(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.PreferenceRemarks == "Updated remark"


def test_update_preference_islike_success(db_session_mock, mock_pref_list_likes):
    """Successfully updates IsLike for a LikesDislikes preference."""
    existing = _make_preference(1, patient_id=1, list_id=10, is_like="Y")
    updated = _make_preference(1, patient_id=1, list_id=10, is_like="N")

    mock_patient = mock.MagicMock()
    mock_patient.id = 1
    mock_patient.name = "Test patient"

    _setup_query_sequence(db_session_mock, [
        existing,
        mock_pref_list_likes,
        None,
        mock_patient,
        mock_pref_list_likes,
        updated,
    ])
    db_session_mock.flush = mock.MagicMock()

    payload = PatientPersonalPreferenceUpdate(IsLike="N")

    with mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        result = update_preference(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.IsLike == "N"


def test_update_preference_not_found_returns_none(db_session_mock):
    """Returns None when the record does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    payload = PatientPersonalPreferenceUpdate(PreferenceRemarks="Anything")

    result = update_preference(db_session_mock, 999, payload, USER_ID, USER_FULL_NAME)

    assert result is None
    db_session_mock.commit.assert_not_called()


def test_update_preference_invalid_islike_raises_400(db_session_mock):
    """Invalid IsLike value raises 400 before any DB call."""
    # Use MagicMock instead of real Pydantic model so model_dump can be mocked
    payload = mock.MagicMock(spec=None)
    payload.model_dump = mock.MagicMock(return_value={"IsLike": "bad_value"})

    with pytest.raises(HTTPException) as exc:
        update_preference(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "IsLike must be" in exc.value.detail


def test_update_preference_patient_not_found_raises_404(db_session_mock):
    """Changing PatientID to a non-existent patient raises 404."""
    existing = _make_preference(1, patient_id=1, list_id=10)

    _setup_query_sequence(db_session_mock, [
        existing,   # fetch record
        None,       # patient 9999 not found
    ])

    payload = PatientPersonalPreferenceUpdate(PatientID=9999)

    with pytest.raises(HTTPException) as exc:
        update_preference(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 404
    assert "Patient with ID 9999" in exc.value.detail


def test_update_preference_list_item_not_found_raises_404(db_session_mock):
    """Changing PersonalPreferenceListID to a non-existent item raises 404."""
    existing = _make_preference(1, patient_id=1, list_id=10)

    _setup_query_sequence(db_session_mock, [
        existing,  # fetch record
        None,      # list item 9999 not found
    ])

    payload = PatientPersonalPreferenceUpdate(PersonalPreferenceListID=9999)

    with pytest.raises(HTTPException) as exc:
        update_preference(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 404
    assert "Personal preference list item with ID 9999" in exc.value.detail


def test_update_preference_duplicate_raises_400(db_session_mock, mock_pref_list_likes):
    """Updating to match an existing record for the same patient raises 400."""
    existing = _make_preference(1, patient_id=1, list_id=10)
    duplicate = _make_preference(2, patient_id=1, list_id=20)

    _setup_query_sequence(db_session_mock, [
        existing,            # fetch record
        mock_pref_list_likes, # new list item found
        duplicate,           # duplicate found
    ])

    payload = PatientPersonalPreferenceUpdate(PersonalPreferenceListID=20)

    with pytest.raises(HTTPException) as exc:
        update_preference(db_session_mock, 1, payload, USER_ID, USER_FULL_NAME)

    assert exc.value.status_code == 400
    assert "Another personal preference record" in exc.value.detail


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def test_delete_preference_success(db_session_mock, mock_pref_list_likes):
    """Successfully soft deletes a preference."""
    existing = _make_preference(1, patient_id=1, list_id=10)
    deleted = _make_preference(1,patient_id=1, list_id=10)
    deleted.IsDeleted = "1"
    deleted.ModifiedByID = USER_ID

    mock_patient = mock.MagicMock()
    mock_patient.id = 1
    mock_patient.name = "Test patient"

    _setup_query_sequence(db_session_mock, [
        existing,  # fetch record
        mock_patient,
        mock_pref_list_likes,
        deleted,   # reload after commit
    ])
    db_session_mock.flush = mock.MagicMock()

    with mock.patch("app.crud.patient_personal_preference_crud.joinedload"), \
         mock.patch("app.crud.patient_personal_preference_crud.log_crud_action"):
        result = delete_preference(db_session_mock, 1, USER_ID, USER_FULL_NAME)

    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"
    assert result.ModifiedByID == USER_ID


def test_delete_preference_not_found_returns_none(db_session_mock):
    """Returns None when the record does not exist."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_preference(db_session_mock, 999, USER_ID, USER_FULL_NAME)

    assert result is None
    db_session_mock.commit.assert_not_called()