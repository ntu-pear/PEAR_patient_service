from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_personal_preference_crud as crud_pref
from ..database import get_db
from ..schemas.patient_personal_preference import (
    PatientPersonalPreference,
    PatientPersonalPreferenceCreate,
    PatientPersonalPreferenceUpdate,
    PatientPersonalPreferenceWithDetails,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()


def _build_with_details(db_pref) -> PatientPersonalPreferenceWithDetails:
    """Merge base fields with denormalised list fields from relationship."""
    base = PatientPersonalPreference.model_validate(db_pref).model_dump()
    base["PreferenceType"] = (
        db_pref.preference_list.PreferenceType if db_pref.preference_list else None
    )
    base["PreferenceName"] = (
        db_pref.preference_list.PreferenceName if db_pref.preference_list else None
    )
    return PatientPersonalPreferenceWithDetails(**base)


@router.get(
    "/PersonalPreferences",
    response_model=PaginatedResponse[PatientPersonalPreferenceWithDetails],
)
def get_preferences(
    request: Request,
    pageNo: int = Query(default=0, ge=0),
    pageSize: int = Query(default=10, ge=1, le=200),
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    _ = extract_jwt_payload(request, require_auth)

    items, totalRecords, totalPages = crud_pref.get_preferences(
        db, pageNo=pageNo, pageSize=pageSize
    )

    return PaginatedResponse(
        data=[_build_with_details(i) for i in items],
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages,
    )


@router.get(
    "/PersonalPreferences/by-patient-id/{patient_id}",
    response_model=PaginatedResponse[PatientPersonalPreferenceWithDetails],
)
def get_patient_preferences(
    request: Request,
    patient_id: int,
    pageNo: int = Query(default=0, ge=0),
    pageSize: int = Query(default=100, ge=1, le=500),
    preferenceType: Optional[str] = Query(
        default=None,
        description="Filter by preference type: LikesDislikes | Habit | Hobby",
    ),
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    _ = extract_jwt_payload(request, require_auth)

    items, totalRecords, totalPages = crud_pref.get_patient_preferences(
        db,
        patient_id=patient_id,
        pageNo=pageNo,
        pageSize=pageSize,
        preference_type=preferenceType,
    )

    return PaginatedResponse(
        data=[_build_with_details(i) for i in items],
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages,
    )


@router.get(
    "/PersonalPreferences/by-preference-id/{preference_id}",
    response_model=SingleResponse[PatientPersonalPreferenceWithDetails],
)
def get_preference(
    request: Request,
    preference_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    _ = extract_jwt_payload(request, require_auth)

    db_pref = crud_pref.get_preference(db, preference_id)
    if not db_pref:
        raise HTTPException(status_code=404, detail="Personal preference not found")

    return SingleResponse(data=_build_with_details(db_pref))


@router.post(
    "/PersonalPreferences/add",
    response_model=SingleResponse[PatientPersonalPreferenceWithDetails],
    status_code=201,
)
def create_preference(
    request: Request,
    preference: PatientPersonalPreferenceCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_pref = crud_pref.create_preference(db, preference, user_id, user_full_name)

    return SingleResponse(data=_build_with_details(db_pref))


@router.put(
    "/PersonalPreferences/update/{preference_id}",
    response_model=SingleResponse[PatientPersonalPreferenceWithDetails],
)
def update_preference(
    request: Request,
    preference_id: int,
    preference: PatientPersonalPreferenceUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_pref = crud_pref.update_preference(
        db, preference_id, preference, user_id, user_full_name
    )

    if not db_pref:
        raise HTTPException(status_code=404, detail="Personal preference not found")

    return SingleResponse(data=_build_with_details(db_pref))


@router.delete(
    "/PersonalPreferences/delete/{preference_id}",
    response_model=SingleResponse[PatientPersonalPreferenceWithDetails],
)
def delete_preference(
    request: Request,
    preference_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_pref = crud_pref.delete_preference(
        db, preference_id, user_id, user_full_name
    )

    if not db_pref:
        raise HTTPException(status_code=404, detail="Personal preference not found")

    return SingleResponse(data=_build_with_details(db_pref))