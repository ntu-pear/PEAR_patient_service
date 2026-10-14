"""Doses actually given. Called by the Scheduler (with the caller's token) when
MED_ADMIN_SYNC is on. Neither route accepts the require_auth bypass."""
from datetime import date
from typing import Optional, Set, Tuple

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_role_name, get_user_id
from ..crud import patient_medication_administration_crud as crud
from ..database import get_db
from ..errors import ForbiddenError
from ..schemas.patient_medication_administration import (
    PatientMedicationAdministration,
    PatientMedicationAdministrationMark,
)
from ..schemas.response import SingleResponse

router = APIRouter()

MARK_ROLES = {"CAREGIVER", "SUPERVISOR"}
UNDO_ROLES = {"SUPERVISOR"}


def _actor(request: Request, allowed: Set[str], forbidden_detail: str) -> Tuple[str, str, str]:
    payload = extract_jwt_payload(request, require_auth=True)
    role = get_role_name(payload)
    if role not in allowed:
        raise ForbiddenError(forbidden_detail)
    return get_user_id(payload), get_full_name(payload), role


@router.put("/Medication/administration", response_model=SingleResponse[PatientMedicationAdministration])
def mark_medication_administered(
    request: Request,
    body: PatientMedicationAdministrationMark,
    db: Session = Depends(get_db),
):
    user_id, full_name, role = _actor(request, MARK_ROLES, "Only caregivers and supervisors can mark a dose as given")
    row, _created = crud.mark_administered(db, body, user_id, full_name, role)
    return SingleResponse(data=row)


@router.delete(
    "/Medication/administration",
    response_model=SingleResponse[Optional[PatientMedicationAdministration]],
)
def undo_medication_administration(
    request: Request,
    medication_id: int,
    administer_date: date,
    scheduled_time: str = Query(..., min_length=1, max_length=5),
    db: Session = Depends(get_db),
):
    user_id, full_name, role = _actor(request, UNDO_ROLES, "Only supervisors can undo a given dose")
    row = crud.undo_administration(db, medication_id, administer_date, scheduled_time, user_id, full_name, role)
    return SingleResponse(data=row)
