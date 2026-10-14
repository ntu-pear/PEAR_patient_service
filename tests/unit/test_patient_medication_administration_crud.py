"""Marking and undoing a dose. DB lookups and the audit log are stubbed."""
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.crud import patient_medication_administration_crud as crud
from app.errors import BadRequestError
from app.logger.logger_utils import ActionType
from app.schemas.patient_medication_administration import PatientMedicationAdministrationMark

MED = SimpleNamespace(Id=7, PatientId=3, PrescriptionListId=11, AdministerTime="0800,1400", Dosage="2 tabs", IsDeleted="0")


@pytest.fixture
def env(monkeypatch):
    state = SimpleNamespace(medication=MED, live=[], logs=[], events=[], lookups=[])
    db = MagicMock()
    db.commit.side_effect = lambda: state.events.append("commit")

    def refresh(row):
        if getattr(row, "Id", None) is None:
            row.Id = 99  # what the identity column would give

    db.refresh.side_effect = refresh

    def find_live(db_, medication_id, administer_date, slot):
        state.lookups.append((medication_id, administer_date, slot))
        return state.live.pop(0) if state.live else None

    def log(**kwargs):
        state.events.append("log")
        state.logs.append(kwargs)

    monkeypatch.setattr(crud, "_find_medication", lambda db_, mid, include_deleted=False: state.medication)
    monkeypatch.setattr(crud, "_find_live", find_live)
    monkeypatch.setattr(crud, "_names", lambda db_, med: ("Paracetamol", "Tan Ah Kow"))
    monkeypatch.setattr(crud, "log_crud_action", log)
    state.db = db
    return state


def _mark(env, **body):
    data = PatientMedicationAdministrationMark(**{
        "MedicationId": 7,
        "ScheduledTime": "0800",
        "AdministerDate": "2026-10-14",
        "ActualAdministerTime": "2026-10-14T00:05:00Z",
        **body,
    })
    return crud.mark_administered(env.db, data, "U1", "Sam Lee", "CAREGIVER")


def test_insert_creates_row_and_logs_after_commit(env):
    row, created = _mark(env)
    assert created is True
    assert (row.MedicationId, row.PatientId, row.ScheduledTime) == (7, 3, "0800")
    assert row.AdministerDate == date(2026, 10, 14)
    assert row.ActualAdministerTime == datetime(2026, 10, 14, 0, 5)
    assert (row.AdministeredById, row.CreatedById, row.ModifiedById, row.IsDeleted) == ("U1", "U1", "U1", "0")
    assert env.events == ["commit", "log"]
    entry = env.logs[0]
    assert entry["action"] is ActionType.CREATE
    assert entry["table"] == "PATIENT_MEDICATION_ADMINISTRATION"
    assert (entry["user"], entry["user_full_name"], entry["role"]) == ("U1", "Sam Lee", "CAREGIVER")
    assert (entry["patient_id"], entry["patient_full_name"], entry["entity_id"]) == (3, "Tan Ah Kow", 99)
    assert entry["message"] == "Medication administered: Paracetamol 2 tabs (08:00 slot, 2026-10-14)"
    assert entry["updated_data"] == {
        "Id": 99,
        "MedicationId": 7,
        "MedicationName": "Paracetamol",
        "Dosage": "2 tabs",
        "AdministerDate": "2026-10-14",
        "ScheduledTime": "08:00",
        "ActualAdministerTime": "2026-10-14T00:05:00+00:00",
        "AdministeredById": "U1",
        "AdministeredByName": "Sam Lee",
    }


def test_identical_repeat_returns_existing_without_log(env):
    existing = SimpleNamespace(Id=5)
    env.live = [existing]
    row, created = _mark(env)
    assert row is existing and created is False
    env.db.add.assert_not_called()
    env.db.commit.assert_not_called()
    assert env.logs == []


def test_unknown_or_deleted_medication_is_400(env):
    env.medication = None  # _find_medication filters IsDeleted='0', so a deleted course also returns None
    with pytest.raises(BadRequestError) as exc:
        _mark(env)
    assert exc.value.status_code == 400
    assert env.logs == []


def test_wrong_slot_is_400(env):
    with pytest.raises(BadRequestError) as exc:
        _mark(env, ScheduledTime="0900")
    assert exc.value.status_code == 400
    env.db.add.assert_not_called()


def test_slot_spelling_and_spaces_match_the_course(env):
    env.medication = SimpleNamespace(**{**vars(MED), "AdministerTime": "0800, 1400"})
    row, created = _mark(env, ScheduledTime="14:00")
    assert created is True and row.ScheduledTime == "1400"
    assert env.lookups == [(7, date(2026, 10, 14), "1400")]


def test_concurrent_insert_returns_the_winner(env):
    winner = SimpleNamespace(Id=6)
    env.live = [None, winner]
    env.db.commit.side_effect = IntegrityError("INSERT", {}, Exception("UX_PatientMedicationAdministration_Slot"))
    row, created = _mark(env)
    assert row is winner and created is False
    env.db.rollback.assert_called_once()
    assert env.logs == []


def test_failed_commit_writes_no_log(env):
    env.db.commit.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError):
        _mark(env)
    assert env.logs == []


def test_log_failure_does_not_fail_the_dose(env, monkeypatch):
    def broken(**kwargs):
        raise RuntimeError("log disk full")
    monkeypatch.setattr(crud, "log_crud_action", broken)
    row, created = _mark(env)
    assert created is True and row.Id == 99


@pytest.mark.parametrize("given_at, expected_day", [
    ("2026-10-13T15:59:00Z", date(2026, 10, 13)),  # 23:59 SGT
    ("2026-10-13T16:00:00Z", date(2026, 10, 14)),  # 00:00 SGT next day
])
def test_sgt_date_around_midnight_utc(env, given_at, expected_day):
    row, _ = _mark(env, AdministerDate=None, ActualAdministerTime=given_at)
    assert row.AdministerDate == expected_day


def test_offset_time_is_stored_as_utc(env):
    row, _ = _mark(env, ActualAdministerTime="2026-10-14T08:05:00+08:00")
    assert row.ActualAdministerTime == datetime(2026, 10, 14, 0, 5)


def test_naive_time_is_read_as_utc(env):
    row, _ = _mark(env, ActualAdministerTime="2026-10-14T00:05:00")
    assert row.ActualAdministerTime == datetime(2026, 10, 14, 0, 5)


def test_display_slot():
    assert crud.display_slot("0800") == "08:00"
    assert crud.display_slot("08:00") == "08:00"
    assert crud.display_slot("8am") == "8am"
