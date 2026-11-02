"""Marking and undoing a dose. DB lookups and the audit log are stubbed."""
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.crud import patient_medication_administration_crud as crud
from app.errors import BadRequestError, ForbiddenError
from app.logger.logger_utils import ActionType
from app.schemas.patient_medication_administration import PatientMedicationAdministrationMark

MED = SimpleNamespace(Id=7, PatientId=3, PrescriptionListId=11, AdministerTime="0800,1400", Dosage="2 tabs", IsDeleted="0")


@pytest.fixture
def env(monkeypatch):
    state = SimpleNamespace(medication=MED, live=[], logs=[], events=[], lookups=[])
    db = MagicMock()
    db.commit.side_effect = lambda: state.events.append("commit")

    def flush():
        for row in db.add.call_args_list:
            if getattr(row.args[0], "Id", None) is None:
                row.args[0].Id = 99  # what the identity column would give

    db.flush.side_effect = flush

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
    state.allocated = True
    monkeypatch.setattr(crud, "_is_allocated_caregiver", lambda db_, patient_id, user_id: state.allocated)
    state.db = db
    return state


def _full_row(Id):
    return SimpleNamespace(
        Id=Id, MedicationId=7, PatientId=3, AdministerDate=date(2026, 10, 14), ScheduledTime="0800",
        ActualAdministerTime=datetime(2026, 10, 14, 0, 5), AdministeredById="CG1", IsDeleted="0",
        CreatedDateTime=datetime(2026, 10, 14, 0, 5), UpdatedDateTime=datetime(2026, 10, 14, 0, 5),
        CreatedById="CG1", ModifiedById="CG1",
    )


class _ExpiringRow(SimpleNamespace):
    """Like an ORM row after commit: reading any column fails (the lazy reload went wrong)."""

    def __getattribute__(self, name):
        if name.startswith("__") or not object.__getattribute__(self, "__dict__").get("_expired"):
            return object.__getattribute__(self, name)
        raise RuntimeError("row expired")


def _expire_on_commit(env, *rows):
    def commit():
        env.events.append("commit")
        for r in rows:
            r.__dict__["_expired"] = True

    env.db.commit.side_effect = commit


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
    existing = _full_row(5)
    env.live = [existing]
    row, created = _mark(env)
    assert row.Id == 5 and created is False
    env.db.add.assert_not_called()
    env.db.commit.assert_not_called()
    assert env.logs == []


def test_caregiver_not_allocated_to_the_patient_is_403(env):
    env.allocated = False
    with pytest.raises(ForbiddenError):
        _mark(env)
    env.db.add.assert_not_called()
    assert env.logs == []


def test_supervisor_can_mark_any_patient(env):
    env.allocated = False
    data = PatientMedicationAdministrationMark(MedicationId=7, ScheduledTime="0800", AdministerDate="2026-10-14")
    row, created = crud.mark_administered(env.db, data, "S1", "Sue Supervisor", "SUPERVISOR")
    assert created is True


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
    winner = _full_row(6)
    env.live = [None, winner]
    env.db.commit.side_effect = IntegrityError("INSERT", {}, Exception("UX_PatientMedicationAdministration_Slot"))
    row, created = _mark(env)
    assert row.Id == 6 and created is False
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


def _live_row():
    return SimpleNamespace(
        Id=5, MedicationId=7, PatientId=3, AdministerDate=date(2026, 10, 14), ScheduledTime="0800",
        ActualAdministerTime=datetime(2026, 10, 14, 0, 5), AdministeredById="CG1", IsDeleted="0",
        CreatedDateTime=datetime(2026, 10, 14, 0, 5), CreatedById="CG1",
        UpdatedDateTime=datetime(2026, 10, 14, 0, 5), ModifiedById="CG1",
    )


def _undo(env, slot="0800"):
    return crud.undo_administration(env.db, 7, date(2026, 10, 14), slot, "S1", "Sue Supervisor", "SUPERVISOR")


def test_undo_soft_deletes_and_logs_after_commit(env):
    row = _live_row()
    env.live = [row]
    result = _undo(env)
    assert result.Id == 5 and result.IsDeleted == "1" and result.ModifiedById == "S1"
    assert (row.IsDeleted, row.ModifiedById) == ("1", "S1")
    assert env.events == ["commit", "log"]
    entry = env.logs[0]
    assert entry["action"] is ActionType.DELETE
    assert (entry["user"], entry["user_full_name"], entry["role"]) == ("S1", "Sue Supervisor", "SUPERVISOR")
    assert entry["table"] == "PATIENT_MEDICATION_ADMINISTRATION" and entry["entity_id"] == 5
    assert entry["patient_id"] == 3
    assert entry["message"] == "Medication administration undone: Paracetamol 2 tabs (08:00 slot, 2026-10-14)"
    assert entry["original_data"]["AdministeredById"] == "CG1"
    assert "AdministeredByName" not in entry["original_data"]


def test_undo_with_nothing_live_is_a_no_op(env):
    assert _undo(env) is None
    env.db.commit.assert_not_called()
    assert env.logs == []


def test_undo_unknown_medication_is_400(env):
    env.medication = None
    with pytest.raises(BadRequestError):
        _undo(env)


def test_undo_accepts_colon_slot(env):
    env.live = [_live_row()]
    _undo(env, slot="08:00")
    assert env.lookups == [(7, date(2026, 10, 14), "0800")]


def test_slot_can_be_marked_again_after_undo(env):
    env.live = [_live_row(), None]
    _undo(env)
    row, created = _mark(env)
    assert created is True and row.IsDeleted == "0"


def test_undo_commit_failure_rolls_back_and_logs_nothing(env):
    env.live = [_live_row()]
    env.db.commit.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError):
        _undo(env)
    env.db.rollback.assert_called_once()
    assert env.logs == []


class _ExpiringMedication:
    """Reads fine until the session commits or rolls back, then every read raises,
    like an expired ORM instance whose reload fails."""

    def __init__(self, values):
        self._values = values
        self.expired = False

    def __getattr__(self, name):
        if name in ("_values", "expired"):
            raise AttributeError(name)
        if self.expired:
            raise RuntimeError("reload failed")
        return self._values[name]


def _expiring(env):
    medication = _ExpiringMedication(vars(MED))
    env.medication = medication
    env.db.commit.side_effect = lambda: (setattr(medication, "expired", True), env.events.append("commit"))
    env.db.refresh.side_effect = RuntimeError("reload failed")
    return medication


def test_failing_reload_after_commit_still_returns_the_saved_row(env):
    _expiring(env)
    row, created = _mark(env)
    assert created is True
    assert (row.MedicationId, row.PatientId) == (7, 3)
    assert env.events == ["commit", "log"]
    entry = env.logs[0]
    assert (entry["entity_id"], entry["patient_id"], entry["patient_full_name"]) == (99, 3, "Tan Ah Kow")
    assert entry["message"] == "Medication administered: Paracetamol 2 tabs (08:00 slot, 2026-10-14)"
    assert entry["updated_data"]["Dosage"] == "2 tabs"


def test_failing_reload_after_rollback_still_returns_the_winner(env):
    medication = _expiring(env)
    winner = _full_row(6)
    env.live = [None, winner]
    env.db.commit.side_effect = IntegrityError("INSERT", {}, Exception("UX_PatientMedicationAdministration_Slot"))
    env.db.rollback.side_effect = lambda: setattr(medication, "expired", True)
    row, created = _mark(env)
    assert row.Id == 6 and created is False
    assert env.lookups[-1] == (7, date(2026, 10, 14), "0800")


def test_undo_survives_failing_reload_after_commit(env):
    _expiring(env)
    row = _live_row()
    env.live = [row]
    assert _undo(env).Id == 5
    assert row.IsDeleted == "1"
    entry = env.logs[0]
    assert (entry["entity_id"], entry["patient_id"], entry["patient_full_name"]) == (5, 3, "Tan Ah Kow")
    assert entry["message"] == "Medication administration undone: Paracetamol 2 tabs (08:00 slot, 2026-10-14)"


def test_mark_result_survives_the_row_expiring_on_commit(env, monkeypatch):
    made = []

    def make(**kw):
        row = _ExpiringRow(**kw)
        made.append(row)
        return row

    monkeypatch.setattr(crud, "PatientMedicationAdministration", make)
    env.db.commit.side_effect = lambda: (env.events.append("commit"), [r.__dict__.update(_expired=True) for r in made])
    result, created = _mark(env)
    assert created is True and made[0].__dict__["_expired"] is True
    assert (result.Id, result.MedicationId, result.ScheduledTime, result.IsDeleted) == (99, 7, "0800", "0")
    assert env.events == ["commit", "log"]
    assert env.logs[0]["entity_id"] == 99


def test_undo_result_survives_the_row_expiring_on_commit(env):
    row = _ExpiringRow(**vars(_full_row(5)))
    env.live = [row]
    _expire_on_commit(env, row)
    result = _undo(env)
    assert row.__dict__["_expired"] is True
    assert (result.Id, result.IsDeleted, result.ModifiedById) == (5, "1", "S1")
    assert env.events == ["commit", "log"]
