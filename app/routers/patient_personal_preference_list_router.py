from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_personal_preference_list_crud as crud_pref_list
from ..database import get_db
from ..schemas.patient_personal_preference_list import (
    PatientPersonalPreferenceList,
    PatientPersonalPreferenceListCreate,
    PatientPersonalPreferenceListUpdate,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()

VALID_PREFERENCE_TYPES = ("LikesDislikes", "Habit", "Hobby")


@router.get(
    "/PersonalPreferenceList",
    response_model=PaginatedResponse[PatientPersonalPreferenceList],
)
def get_preference_lists(
    request: Request,
    pageNo: int = Query(default=0, ge=0),
    pageSize: int = Query(default=100, ge=1, le=500),
    preferenceType: Optional[str] = Query(
        default=None,
        description="Filter by preference type: All | LikesDislikes | Habit | Hobby. Leaving blank or passing All returns all types.",
    ),
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    _ = extract_jwt_payload(request, require_auth)

    items, totalRecords, totalPages = crud_pref_list.get_preference_lists(
        db,
        pageNo=pageNo,
        pageSize=pageSize,
        preference_type=preferenceType,
    )

    return PaginatedResponse(
        data=[PatientPersonalPreferenceList.model_validate(i) for i in items],
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages,
    )


@router.get(
    "/PersonalPreferenceList/by-preference-list-id/{preference_list_id}",
    response_model=SingleResponse[PatientPersonalPreferenceList],
)
def get_preference_list(
    request: Request,
    preference_list_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    _ = extract_jwt_payload(request, require_auth)

    db_item = crud_pref_list.get_preference_list_by_id(db, preference_list_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Personal preference list item not found")

    return SingleResponse(data=PatientPersonalPreferenceList.model_validate(db_item))


@router.post(
    "/PersonalPreferenceList/add",
    response_model=SingleResponse[PatientPersonalPreferenceList],
    status_code=201,
)
def create_preference_list(
    request: Request,
    preference_list: PatientPersonalPreferenceListCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_item = crud_pref_list.create_preference_list(
        db, preference_list, user_id, user_full_name
    )

    return SingleResponse(data=PatientPersonalPreferenceList.model_validate(db_item))


@router.put(
    "/PersonalPreferenceList/update/{preference_list_id}",
    response_model=SingleResponse[PatientPersonalPreferenceList],
)
def update_preference_list(
    request: Request,
    preference_list_id: int,
    preference_list: PatientPersonalPreferenceListUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_item = crud_pref_list.update_preference_list(
        db, preference_list_id, preference_list, user_id, user_full_name
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Personal preference list item not found")

    return SingleResponse(data=PatientPersonalPreferenceList.model_validate(db_item))


@router.delete(
    "/PersonalPreferenceList/delete/{preference_list_id}",
    response_model=SingleResponse[PatientPersonalPreferenceList],
)
def delete_preference_list(
    request: Request,
    preference_list_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True,
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_item = crud_pref_list.delete_preference_list(
        db, preference_list_id, user_id, user_full_name
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Personal preference list item not found")

    return SingleResponse(data=PatientPersonalPreferenceList.model_validate(db_item))