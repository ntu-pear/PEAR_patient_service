"""
Unit Tests for Patient Medical History CRUD

File: tests/unit/test_patient_medical_history.py

Tests for:
- Retrieving medical histories by patient (pagination, ordering, empty)
- Retrieving a single history by ID (found, not found)
- Creating medical histories (success, duplicate check, optional fields)
- Updating medical histories (success, not found, partial update, duplicate check)
- Deleting medical histories (success, not found)
"""

from datetime import date, datetime
from unittest import mock

import pytest
from fastapi import HTTPException

from app.crud.patient_medical_history_crud import (
    create_medical_history,
    delete_medical_history,
    get_medical_histories_by_patient,
    get_medical_history_by_id,
    update_medical_history,
)
from app.schemas.patient_medical_history import (
    PatientMedicalHistoryCreate,
    PatientMedicalHistoryUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_data_query(mock_results):
    """Return a mock query chain for the paginated data fetch (uses joinedload)."""
    q = mock.MagicMock()
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.all.return_value = mock_results
    return q


def _make_count_query(count):
    """Return a mock query chain for the scalar count fetch."""
    q = mock.MagicMock()
    q.select_from.return_value = q
    q.filter.return_value = q
    q.scalar.return_value = count
    return q


# ---------------------------------------------------------------------------
# get_medical_histories_by_patient
# ---------------------------------------------------------------------------

def test_get_medical_histories_by_patient_returns_list(db_session_mock):
    """Test basic retrieval returns the expected records, totalRecords, and totalPages."""
    mock_histories = [
        mock.MagicMock(Id=2, PatientID=1, MedicalDiagnosisID=2, IsDeleted='0'),
        mock.MagicMock(Id=1, PatientID=1, MedicalDiagnosisID=1, IsDeleted='0'),
    ]

    db_session_mock.query.side_effect = [
        _make_data_query(mock_histories),
        _make_count_query(2),
    ]

    histories, totalRecords, totalPages = get_medical_histories_by_patient(
        db_session_mock, patient_id=1, pageNo=0, pageSize=10
    )

    assert isinstance(histories, list)
    assert len(histories) == 2
    assert totalRecords == 2
    assert totalPages == 1


def test_get_medical_histories_by_patient_empty(db_session_mock):
    """Test retrieval for a patient with no records returns empty list and zero totals."""
    db_session_mock.query.side_effect = [
        _make_data_query([]),
        _make_count_query(0),
    ]

    histories, totalRecords, totalPages = get_medical_histories_by_patient(
        db_session_mock, patient_id=1, pageNo=0, pageSize=10
    )

    assert len(histories) == 0
    assert totalRecords == 0
    assert totalPages == 0


def test_get_medical_histories_by_patient_pagination(db_session_mock):
    """Test that pagination applies the correct offset and calculates totalPages."""
    mock_histories = [
        mock.MagicMock(Id=1, PatientID=1, MedicalDiagnosisID=1, IsDeleted='0'),
    ]

    data_query = _make_data_query(mock_histories)
    db_session_mock.query.side_effect = [
        data_query,
        _make_count_query(6),  # 6 total records
    ]

    _, totalRecords, totalPages = get_medical_histories_by_patient(
        db_session_mock, patient_id=1, pageNo=1, pageSize=5
    )

    assert totalRecords == 6
    assert totalPages == 2  # math.ceil(6 / 5) = 2
    data_query.offset.assert_called_with(5)  # pageNo=1 * pageSize=5


def test_get_medical_histories_ordered_by_id_desc(db_session_mock):
    """Test that histories are fetched with an order_by call (Id descending)."""
    data_query = _make_data_query([])
    db_session_mock.query.side_effect = [data_query, _make_count_query(0)]

    get_medical_histories_by_patient(db_session_mock, patient_id=1, pageNo=0, pageSize=10)

    data_query.order_by.assert_called()


# ---------------------------------------------------------------------------
# get_medical_history_by_id
# ---------------------------------------------------------------------------

def test_get_medical_history_by_id_found(db_session_mock):
    """Test that a valid ID returns the correct record."""
    mock_history = mock.MagicMock(Id=1, PatientID=1, MedicalDiagnosisID=1, IsDeleted='0')

    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_history
    db_session_mock.query.return_value = mock_query

    result = get_medical_history_by_id(db_session_mock, 1)

    assert result is not None
    assert result.Id == 1
    assert result.PatientID == 1


def test_get_medical_history_by_id_not_found(db_session_mock):
    """Test that a non-existent ID returns None."""
    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    db_session_mock.query.return_value = mock_query

    result = get_medical_history_by_id(db_session_mock, 999)

    assert result is None


# ---------------------------------------------------------------------------
# create_medical_history
# ---------------------------------------------------------------------------

def test_create_medical_history_success(db_session_mock):
    """Test successful creation commits to the database and returns the new record."""
    mock_instance = mock.MagicMock()
    mock_instance.Id = 1
    mock_instance.PatientID = 1
    mock_instance.MedicalDiagnosisID = 1
    mock_instance.IsDeleted = '0'

    # No existing duplicate
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = PatientMedicalHistoryCreate(
        PatientID=1,
        MedicalDiagnosisID=1,
        CreatedByID="test_user",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.PatientMedicalHistory') as mock_model:
        mock_model.return_value = mock_instance

        with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
            result = create_medical_history(db_session_mock, data, "test_user", "Test User")

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert result is not None


def test_create_medical_history_with_all_optional_fields(db_session_mock):
    """Test creation with all optional fields populated stores them on the record."""
    mock_instance = mock.MagicMock()
    mock_instance.Id = 1
    mock_instance.PatientID = 1
    mock_instance.MedicalDiagnosisID = 2
    mock_instance.DateOfDiagnosis = date(2024, 1, 15)
    mock_instance.Remarks = "Severe condition"
    mock_instance.SourceOfInformation = "Doctor"
    mock_instance.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    data = PatientMedicalHistoryCreate(
        PatientID=1,
        MedicalDiagnosisID=2,
        DateOfDiagnosis=date(2024, 1, 15),
        Remarks="Severe condition",
        SourceOfInformation="Doctor",
        CreatedByID="test_user",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.PatientMedicalHistory') as mock_model:
        mock_model.return_value = mock_instance

        with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
            result = create_medical_history(db_session_mock, data, "test_user", "Test User")

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    assert result.Remarks == "Severe condition"
    assert result.SourceOfInformation == "Doctor"
    assert result.DateOfDiagnosis == date(2024, 1, 15)


def test_create_medical_history_duplicate_raises_400(db_session_mock):
    """Test that creating a record for the same patient+diagnosis raises 400."""
    mock_existing = mock.MagicMock(Id=1, PatientID=1, MedicalDiagnosisID=1, IsDeleted='0')
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing

    data = PatientMedicalHistoryCreate(
        PatientID=1,
        MedicalDiagnosisID=1,
        CreatedByID="test_user",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.PatientMedicalHistory') as mock_model:
        mock_model.return_value = mock.MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            create_medical_history(db_session_mock, data, "test_user", "Test User")

    assert exc_info.value.status_code == 400
    assert "already has a medical history record" in exc_info.value.detail


def test_create_medical_history_no_commit_on_duplicate(db_session_mock):
    """Test that a duplicate check failure does not commit anything to the database."""
    mock_existing = mock.MagicMock(Id=1, PatientID=1, MedicalDiagnosisID=1, IsDeleted='0')
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_existing

    data = PatientMedicalHistoryCreate(
        PatientID=1,
        MedicalDiagnosisID=1,
        CreatedByID="test_user",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.PatientMedicalHistory') as mock_model:
        mock_model.return_value = mock.MagicMock()

        with pytest.raises(HTTPException):
            create_medical_history(db_session_mock, data, "test_user", "Test User")

    db_session_mock.add.assert_not_called()
    db_session_mock.commit.assert_not_called()


# ---------------------------------------------------------------------------
# update_medical_history
# ---------------------------------------------------------------------------

def test_update_medical_history_success(db_session_mock):
    """Test successful update commits and returns the updated record."""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.PatientID = 1
    mock_data.MedicalDiagnosisID = 1
    mock_data.Remarks = "Old remarks"
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    update_data = PatientMedicalHistoryUpdate(
        Remarks="Updated remarks",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = update_medical_history(db_session_mock, 1, update_data, "test_user", "Test User")

    db_session_mock.commit.assert_called_once()
    assert result is not None
    assert result.Remarks == "Updated remarks"


def test_update_medical_history_not_found_returns_none(db_session_mock):
    """Test that updating a non-existent record returns None without committing."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    update_data = PatientMedicalHistoryUpdate(
        Remarks="Updated remarks",
        ModifiedByID="test_user",
    )

    result = update_medical_history(db_session_mock, 999, update_data, "test_user", "Test User")

    assert result is None
    db_session_mock.commit.assert_not_called()


def test_update_medical_history_partial_update_only_modifies_set_fields(db_session_mock):
    """Test that a partial update only modifies the explicitly provided fields."""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.PatientID = 1
    mock_data.MedicalDiagnosisID = 1
    mock_data.Remarks = "Original remarks"
    mock_data.SourceOfInformation = None
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    update_data = PatientMedicalHistoryUpdate(
        SourceOfInformation="Hospital records",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = update_medical_history(db_session_mock, 1, update_data, "test_user", "Test User")

    db_session_mock.commit.assert_called_once()
    assert result is not None
    assert result.SourceOfInformation == "Hospital records"


def test_update_medical_history_date_update(db_session_mock):
    """Test that DateOfDiagnosis is correctly updated."""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.PatientID = 1
    mock_data.MedicalDiagnosisID = 1
    mock_data.DateOfDiagnosis = date(2020, 1, 1)
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    update_data = PatientMedicalHistoryUpdate(
        DateOfDiagnosis=date(2024, 6, 15),
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = update_medical_history(db_session_mock, 1, update_data, "test_user", "Test User")

    db_session_mock.commit.assert_called_once()
    assert result.DateOfDiagnosis == date(2024, 6, 15)


def test_update_medical_history_duplicate_raises_400_when_diagnosis_changes(db_session_mock):
    """Test that changing MedicalDiagnosisID to one already used triggers 400."""
    mock_existing = mock.MagicMock()
    mock_existing.Id = 1
    mock_existing.PatientID = 1
    mock_existing.MedicalDiagnosisID = 1
    mock_existing.IsDeleted = '0'

    mock_duplicate = mock.MagicMock()
    mock_duplicate.Id = 2
    mock_duplicate.PatientID = 1
    mock_duplicate.MedicalDiagnosisID = 2
    mock_duplicate.IsDeleted = '0'

    first_query = mock.MagicMock()
    first_query.filter.return_value.first.return_value = mock_existing

    second_query = mock.MagicMock()
    second_query.filter.return_value.first.return_value = mock_duplicate  # duplicate found

    db_session_mock.query.side_effect = [first_query, second_query]

    update_data = PatientMedicalHistoryUpdate(
        MedicalDiagnosisID=2,
        ModifiedByID="test_user",
    )

    with pytest.raises(HTTPException) as exc_info:
        update_medical_history(db_session_mock, 1, update_data, "test_user", "Test User")

    assert exc_info.value.status_code == 400
    assert "already has a medical history record" in exc_info.value.detail


def test_update_medical_history_no_duplicate_check_when_diagnosis_unchanged(db_session_mock):
    """Test that updating fields other than MedicalDiagnosisID skips the duplicate check."""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.PatientID = 1
    mock_data.MedicalDiagnosisID = 1
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    # No MedicalDiagnosisID in update — duplicate check must be skipped
    update_data = PatientMedicalHistoryUpdate(
        Remarks="No diagnosis change",
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = update_medical_history(db_session_mock, 1, update_data, "test_user", "Test User")

    # Only one db.query call (the fetch) — no second call for duplicate check
    assert db_session_mock.query.call_count == 1
    db_session_mock.commit.assert_called_once()
    assert result is not None


def test_update_medical_history_new_diagnosis_no_duplicate_succeeds(db_session_mock):
    """Test that changing MedicalDiagnosisID to an unused one succeeds."""
    mock_existing = mock.MagicMock()
    mock_existing.Id = 1
    mock_existing.PatientID = 1
    mock_existing.MedicalDiagnosisID = 1
    mock_existing.IsDeleted = '0'

    first_query = mock.MagicMock()
    first_query.filter.return_value.first.return_value = mock_existing

    second_query = mock.MagicMock()
    second_query.filter.return_value.first.return_value = None  # no duplicate

    db_session_mock.query.side_effect = [first_query, second_query]

    update_data = PatientMedicalHistoryUpdate(
        MedicalDiagnosisID=3,
        ModifiedByID="test_user",
    )

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = update_medical_history(db_session_mock, 1, update_data, "test_user", "Test User")

    db_session_mock.commit.assert_called_once()
    assert result is not None
    assert result.MedicalDiagnosisID == 3


# ---------------------------------------------------------------------------
# delete_medical_history
# ---------------------------------------------------------------------------

def test_delete_medical_history_success(db_session_mock):
    """Test soft delete sets IsDeleted to '1' and commits."""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.PatientID = 1
    mock_data.MedicalDiagnosisID = 1
    mock_data.IsDeleted = '0'

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = delete_medical_history(db_session_mock, 1, "test_user", "Test User")

    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == '1'


def test_delete_medical_history_not_found_returns_none(db_session_mock):
    """Test that deleting a non-existent record returns None without committing."""
    db_session_mock.query.return_value.filter.return_value.first.return_value = None

    result = delete_medical_history(db_session_mock, 999, "test_user", "Test User")

    assert result is None
    db_session_mock.commit.assert_not_called()


def test_delete_medical_history_modifies_modified_date(db_session_mock):
    """Test that the delete operation updates ModifiedDate on the record."""
    mock_data = mock.MagicMock()
    mock_data.Id = 1
    mock_data.IsDeleted = '0'
    mock_data.ModifiedDate = datetime(2020, 1, 1)

    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    with mock.patch('app.crud.patient_medical_history_crud.log_crud_action'):
        result = delete_medical_history(db_session_mock, 1, "test_user", "Test User")

    # ModifiedDate must have been updated (set to a new datetime by the CRUD)
    assert result.ModifiedDate != datetime(2020, 1, 1)
