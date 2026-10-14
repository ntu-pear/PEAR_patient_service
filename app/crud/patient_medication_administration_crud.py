"""Doses actually given (PATIENT_MEDICATION_ADMINISTRATION).

A dose slot is (MedicationId, AdministerDate, ScheduledTime). There is at most one live
row per slot: marking a slot that is already given returns the existing row and logs
nothing, so a retry from the Scheduler is safe. Audit entries are written only after
the commit succeeds, and a failed audit write never fails the dose.
"""
import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pytz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..errors import BadRequestError
from ..logger.logger_utils import ActionType, log_crud_action
from ..models.patient_medication_administration_model import PatientMedicationAdministration
from ..models.patient_medication_model import PatientMedication
from ..models.patient_model import Patient
from ..models.patient_prescription_list_model import PatientPrescriptionList
from ..schemas.patient_medication_administration import PatientMedicationAdministrationMark

logger = logging.getLogger(__name__)

TABLE = "PATIENT_MEDICATION_ADMINISTRATION"
SGT = pytz.timezone("Asia/Singapore")


def to_utc_naive(value: Optional[datetime]) -> datetime:
    """UTC without tzinfo, like datetime.utcnow(). A naive input is taken to be UTC already."""
    if value is None:
        return datetime.utcnow()
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def sgt_date(utc_naive: datetime) -> date:
    return pytz.utc.localize(utc_naive).astimezone(SGT).date()


def _course_slots(administer_time: Optional[str]) -> List[str]:
    return [s.strip() for s in (administer_time or "").split(",") if s.strip()]


def _slot_key(slot: str) -> str:
    return slot.strip().replace(":", "")


def match_slot(requested: str, administer_time: Optional[str]) -> Optional[str]:
    """The course's own spelling of the requested slot, or None if it isn't one of its times."""
    key = _slot_key(requested)
    return next((s for s in _course_slots(administer_time) if _slot_key(s) == key), None)


def display_slot(slot: str) -> str:
    key = _slot_key(slot)
    return f"{key[:2]}:{key[2:]}" if len(key) == 4 and key.isdigit() else slot


def _find_medication(db: Session, medication_id: int, include_deleted: bool = False):
    conditions = [PatientMedication.Id == medication_id]
    if not include_deleted:
        conditions.append(PatientMedication.IsDeleted == "0")
    return db.query(PatientMedication).filter(*conditions).first()


def _find_live(db: Session, medication_id: int, administer_date: date, slot: str):
    return db.query(PatientMedicationAdministration).filter(
        PatientMedicationAdministration.MedicationId == medication_id,
        PatientMedicationAdministration.AdministerDate == administer_date,
        PatientMedicationAdministration.ScheduledTime == slot,
        PatientMedicationAdministration.IsDeleted == "0",
    ).first()


def _names(db: Session, medication) -> Tuple[Optional[str], Optional[str]]:
    """(prescription name, patient name) for the audit entry; None when unavailable."""
    try:
        prescription = db.query(PatientPrescriptionList).filter(
            PatientPrescriptionList.Id == medication.PrescriptionListId
        ).first()
        patient = db.query(Patient).filter(Patient.id == medication.PatientId).first()
        return (prescription.Value if prescription else None, patient.name if patient else None)
    except Exception:
        logger.warning("Could not load audit names for medication %s", medication.Id)
        return None, None


def _dose_label(prescription_name: Optional[str], dosage: Optional[str], slot: str, day: date) -> str:
    name = prescription_name or "Unknown medication"
    if dosage:
        name = f"{name} {dosage}"
    return f"{name} ({display_slot(slot)} slot, {day.isoformat()})"


def _audit_data(row, prescription_name: Optional[str], dosage: Optional[str],
                given_by_name: Optional[str]) -> Dict[str, Any]:
    data = {
        "Id": row.Id,
        "MedicationId": row.MedicationId,
        "MedicationName": prescription_name,
        "Dosage": dosage,
        "AdministerDate": row.AdministerDate.isoformat(),
        "ScheduledTime": display_slot(row.ScheduledTime),
        "ActualAdministerTime": pytz.utc.localize(row.ActualAdministerTime).isoformat(),
        "AdministeredById": row.AdministeredById,
    }
    if given_by_name:
        data["AdministeredByName"] = given_by_name
    return data


def _safe_log(**kwargs) -> None:
    try:
        log_crud_action(**kwargs)
    except Exception:
        logger.exception("Could not write the %s audit entry", TABLE)


def mark_administered(
    db: Session,
    data: PatientMedicationAdministrationMark,
    user_id: str,
    user_full_name: str,
    role: str,
) -> Tuple[PatientMedicationAdministration, bool]:
    medication = _find_medication(db, data.MedicationId)
    if medication is None:
        raise BadRequestError("Medication not found or has been deleted")
    slot = match_slot(data.ScheduledTime, medication.AdministerTime)
    if slot is None:
        raise BadRequestError(f"{data.ScheduledTime} is not one of this medication's administer times")

    given_at = to_utc_naive(data.ActualAdministerTime)
    administer_date = data.AdministerDate or sgt_date(given_at)

    # Read everything off the ORM instance now: commit/rollback expire it, and a failed
    # reload afterwards must not turn a saved dose into a 500.
    medication_id, patient_id, dosage = medication.Id, medication.PatientId, medication.Dosage
    prescription_name, patient_name = _names(db, medication)

    existing = _find_live(db, medication_id, administer_date, slot)
    if existing is not None:
        return existing, False

    now = datetime.utcnow()
    row = PatientMedicationAdministration(
        MedicationId=medication_id,
        PatientId=patient_id,
        AdministerDate=administer_date,
        ScheduledTime=slot,
        ActualAdministerTime=given_at,
        AdministeredById=user_id,
        IsDeleted="0",
        CreatedDateTime=now,
        UpdatedDateTime=now,
        CreatedById=user_id,
        ModifiedById=user_id,
    )
    db.add(row)
    try:
        db.flush()  # assigns row.Id while the instance is still loaded
        # Everything the audit entry needs is read now: commit/rollback expire the ORM
        # instances, and a failed reload afterwards must not turn a saved dose into a 500.
        entity_id = row.Id
        audit = _audit_data(row, prescription_name, dosage, user_full_name)
        message = f"Medication administered: {_dose_label(prescription_name, dosage, slot, administer_date)}"
        db.commit()
    except IntegrityError:
        # Another request marked the same slot between our check and our insert.
        db.rollback()
        existing = _find_live(db, medication_id, administer_date, slot)
        if existing is not None:
            return existing, False
        raise
    except Exception:
        db.rollback()
        raise

    _safe_log(
        action=ActionType.CREATE,
        user=user_id,
        user_full_name=user_full_name,
        message=message,
        table=TABLE,
        entity_id=entity_id,
        updated_data=audit,
        patient_id=patient_id,
        patient_full_name=patient_name,
        log_type="medication",
        role=role,
    )
    return row, True

def undo_administration(
    db: Session,
    medication_id: int,
    administer_date: date,
    scheduled_time: str,
    user_id: str,
    user_full_name: str,
    role: str,
) -> Optional[PatientMedicationAdministration]:
    """Soft-delete the live record for a slot. Returns None (and changes nothing) when no
    live record exists, so a retried undo succeeds."""
    # A course deleted since the dose was given can still have its dose undone.
    medication = _find_medication(db, medication_id, include_deleted=True)
    if medication is None:
        raise BadRequestError("Medication not found")
    # Times may have changed since; fall back to the slot as sent.
    slot = match_slot(scheduled_time, medication.AdministerTime) or _slot_key(scheduled_time)

    medication_id_, patient_id, dosage = medication.Id, medication.PatientId, medication.Dosage
    row = _find_live(db, medication_id_, administer_date, slot)
    if row is None:
        return None

    prescription_name, patient_name = _names(db, medication)
    original = _audit_data(row, prescription_name, dosage, None)
    label = _dose_label(prescription_name, dosage, row.ScheduledTime, row.AdministerDate)
    entity_id = row.Id

    row.IsDeleted = "1"
    row.UpdatedDateTime = datetime.utcnow()
    row.ModifiedById = user_id
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    _safe_log(
        action=ActionType.DELETE,
        user=user_id,
        user_full_name=user_full_name,
        message=f"Medication administration undone: {label}",
        table=TABLE,
        entity_id=entity_id,
        original_data=original,
        patient_id=patient_id,
        patient_full_name=patient_name,
        log_type="medication",
        role=role,
    )
    return row
