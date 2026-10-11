import os
from typing import Optional
from urllib.parse import quote

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..errors import ServiceUnavailableError
from ..models.patient_allocation_model import PatientAllocation

ROLE_COLUMN_MAP = {
    "DOCTOR": "doctorId",
    "GAME THERAPIST": "gameTherapistId",
    "CAREGIVER": "caregiverId",
    "SUPERVISOR": "supervisorId",
}


def get_active_staff_by_role(role: str, api_key: Optional[str]) -> list[str]:
    if not api_key:
        raise HTTPException(status_code=500, detail="INTERNAL_SERVICE_API_KEY is not configured.")

    user_service_url = os.environ.get("USER_SERVICE_URL", "")
    if not user_service_url:
        raise HTTPException(status_code=500, detail="USER_SERVICE_URL is not configured.")

    try:
        response = httpx.get(
            f"{user_service_url}/api/v1/supervisor/get_active_staff",
            headers={"X-Api-Key": api_key},
            timeout=10.0,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="User service is unreachable.")

    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="Invalid service API key for user service.")
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="User service returned an unexpected response.")

    try:
        users = response.json().get("users", None)
        if users is None:
            raise ValueError
    except (ValueError, AttributeError):
        raise HTTPException(status_code=503, detail="User service returned a malformed response.")

    filtered = [u.get("id") for u in users if u.get("role") == role and u.get("id")]

    if not filtered:
        raise HTTPException(
            status_code=503,
            detail=f"No active staff found for role '{role}' in user service."
        )

    return filtered


def check_nric_exists(nric: str, api_key: Optional[str]) -> bool:
    """Return True if an active user in the user service holds this NRIC.

    Fails closed: any problem reaching the user service raises, so a patient
    is never created without the check having run.
    """
    if not api_key:
        raise HTTPException(status_code=500, detail="INTERNAL_SERVICE_API_KEY is not configured.")

    user_service_url = os.environ.get("USER_SERVICE_URL", "")
    if not user_service_url:
        raise HTTPException(status_code=500, detail="USER_SERVICE_URL is not configured.")

    try:
        response = httpx.get(
            f"{user_service_url}/api/v1/internal/user/check-nric/{quote(nric, safe='')}",
            headers={"X-Api-Key": api_key},
            timeout=10.0,
        )
    except httpx.HTTPError:
        raise ServiceUnavailableError("User service is unreachable.")

    if response.status_code == 200:
        return True
    if response.status_code == 404:
        return False
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="Invalid service API key for user service.")
    raise ServiceUnavailableError("User service returned an unexpected response.")


def get_least_loaded_staff(role: str, db: Session, api_key: Optional[str]) -> str:
    staff_ids = get_active_staff_by_role(role, api_key)

    column_name = ROLE_COLUMN_MAP.get(role)
    if not column_name:
        raise HTTPException(status_code=500, detail=f"Unknown role for allocation mapping: {role}")

    column = getattr(PatientAllocation, column_name)

    counts = {}
    for staff_id in staff_ids:
        count = (
            db.query(PatientAllocation)
            .filter(column == staff_id)
            .filter(PatientAllocation.isDeleted == "0")
            .filter(PatientAllocation.active == "Y")
            .count()
        )
        counts[staff_id] = count

    def _sort_key(sid):
        try:
            return (counts[sid], 0, int(sid), "")
        except (ValueError, TypeError):
            return (counts[sid], 1, 0, str(sid))

    return min(counts, key=_sort_key)
