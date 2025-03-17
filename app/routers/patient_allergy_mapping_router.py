from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_allergy_mapping_crud
from ..schemas.patient_allergy_mapping import PatientAllergy, PatientAllergyCreate, PatientAllergyCreateResp, PatientAllergyUpdateReq
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..schemas.response import PaginatedResponse

router = APIRouter()

@router.get(
    "/get_all_patient_allergies",
    response_model=PaginatedResponse[PatientAllergy],
    description="Get paginated patient allergies."
)
def get_all_patient_allergies(
    request: Request,
    db: Session = Depends(get_db),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)

    allergies, totalRecords, totalPages = patient_allergy_mapping_crud.get_all_allergies(db, pageNo, pageSize)

    if not allergies:
        raise HTTPException(status_code=404, detail="No allergies found")

    return PaginatedResponse(
        data=allergies,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

@router.get(
    "/get_patient_allergy/{patient_id}",
    response_model=PaginatedResponse[PatientAllergy],
    description="Get paginated patient allergies by patient ID."
)
def get_patient_allergy(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)

    allergies, totalRecords, totalPages = patient_allergy_mapping_crud.get_patient_allergies(db, patient_id, pageNo, pageSize)

    if not allergies:
        raise HTTPException(status_code=404, detail="No allergies found for this patient")

    return PaginatedResponse(
        data=allergies,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )
@router.post("/create_patient_allergy", response_model=PatientAllergyCreateResp, description="Create a new patient allergy record.")
def create_patient_allergy(
    request: Request,
    allergy_data: PatientAllergyCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    return patient_allergy_mapping_crud.create_patient_allergy(db, allergy_data, user_id, user_full_name)

@router.put("/update_patient_allergy/{patient_id}", response_model=PatientAllergyCreateResp, description="Update an existing patient allergy record. Patient_AllergyID is the key of the patient allergy record itself.")
def update_patient_allergy(
    request: Request,
    patient_id: int,
    allergy_data: PatientAllergyUpdateReq,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    return patient_allergy_mapping_crud.update_patient_allergy(db, patient_id, allergy_data, user_id, user_full_name)

@router.delete("/delete_patient_allergy/{patient_allergy_id}", response_model=PatientAllergyCreateResp, description="Soft delete a patient allergy record by marking it as inactive.")
def delete_patient_allergy(
    request: Request,
    patient_allergy_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    return patient_allergy_mapping_crud.delete_patient_allergy(db, patient_allergy_id, user_id, user_full_name)