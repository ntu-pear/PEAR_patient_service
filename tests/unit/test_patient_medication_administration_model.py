"""The model matches sql/17_patient_medication_administration_14_10_2026/01_create_table.sql."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.patient_medication_administration_model import PatientMedicationAdministration
from app.schemas.patient_medication_administration import PatientMedicationAdministrationMark

TABLE = PatientMedicationAdministration.__table__
SQL = Path("sql/17_patient_medication_administration_14_10_2026/01_create_table.sql")


def _index(name):
    return next(i for i in TABLE.indexes if i.name == name)


def test_columns_match_the_sql_script():
    assert TABLE.name == "PATIENT_MEDICATION_ADMINISTRATION"
    assert [c.name for c in TABLE.columns] == [
        "Id", "MedicationId", "PatientId", "AdministerDate", "ScheduledTime",
        "ActualAdministerTime", "AdministeredById", "IsDeleted",
        "CreatedDateTime", "UpdatedDateTime", "CreatedById", "ModifiedById",
    ]


def test_foreign_keys():
    assert {fk.target_fullname for fk in TABLE.foreign_keys} == {"PATIENT_MEDICATION.Id", "PATIENT.id"}


def test_one_live_row_per_slot():
    index = _index("UX_PatientMedicationAdministration_Slot")
    assert index.unique is True
    assert [c.name for c in index.columns] == ["MedicationId", "AdministerDate", "ScheduledTime"]
    assert str(index.dialect_options["mssql"]["where"]) == "IsDeleted = '0'"


def test_patient_date_index():
    index = _index("IX_PatientMedicationAdministration_Patient_Date")
    assert [c.name for c in index.columns] == ["PatientId", "AdministerDate"]


def test_sql_script_is_committed_with_the_same_index_names():
    text = SQL.read_text(encoding="utf-8")
    assert "UX_PatientMedicationAdministration_Slot" in text
    assert "IX_PatientMedicationAdministration_Patient_Date" in text
    assert "WHERE IsDeleted = '0'" in text


def test_mark_body_rejects_a_slot_longer_than_the_column():
    with pytest.raises(ValidationError):
        PatientMedicationAdministrationMark(MedicationId=1, ScheduledTime="08:00:00")


def test_mark_body_defaults():
    body = PatientMedicationAdministrationMark(MedicationId=1, ScheduledTime="0800")
    assert body.AdministerDate is None and body.ActualAdministerTime is None