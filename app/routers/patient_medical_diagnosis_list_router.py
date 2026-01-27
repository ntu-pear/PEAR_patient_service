from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_medical_diagnosis_list_crud as crud_diagnosis
from ..database import get_db
from ..schemas.patient_medical_diagnosis_list import (
    PatientMedicalDiagnosisList,
    PatientMedicalDiagnosisListCreate,
    PatientMedicalDiagnosisListUpdate,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()


@router.get("/MedicalDiagnosisList", response_model=PaginatedResponse[PatientMedicalDiagnosisList])
def get_all_diagnosis_list(request: Request, pageNo: int = 0, pageSize: int = 10, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    
    db_diagnosis_list, totalRecords, totalPages = crud_diagnosis.get_all_diagnosis_list(
        db=db, pageNo=pageNo, pageSize=pageSize
    )
    diagnosis_list = [PatientMedicalDiagnosisList.model_validate(diagnosis) for diagnosis in db_diagnosis_list]
    return PaginatedResponse(data=diagnosis_list, pageNo=pageNo, pageSize=pageSize, totalRecords=totalRecords, totalPages=totalPages)


@router.get("/MedicalDiagnosisList/{diagnosis_id}", response_model=SingleResponse[PatientMedicalDiagnosisList])
def get_diagnosis_by_id(request: Request, diagnosis_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    
    db_diagnosis = crud_diagnosis.get_diagnosis_by_id(db, diagnosis_id)
    if not db_diagnosis:
        raise HTTPException(status_code=404, detail="Medical diagnosis not found")
    
    diagnosis = PatientMedicalDiagnosisList.model_validate(db_diagnosis)
    return SingleResponse(data=diagnosis)


@router.post("/MedicalDiagnosisList/add", response_model=SingleResponse[PatientMedicalDiagnosisList])
def create_diagnosis(request: Request, diagnosis: PatientMedicalDiagnosisListCreate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_diagnosis = crud_diagnosis.create_diagnosis(db, diagnosis, user_id, user_full_name)
    diagnosis_response = PatientMedicalDiagnosisList.model_validate(db_diagnosis)
    return SingleResponse(data=diagnosis_response)


@router.put("/MedicalDiagnosisList/update", response_model=SingleResponse[PatientMedicalDiagnosisList])
def update_diagnosis(request: Request, diagnosis_id: int, diagnosis: PatientMedicalDiagnosisListUpdate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_diagnosis = crud_diagnosis.update_diagnosis(db, diagnosis_id, diagnosis, user_id, user_full_name)
    if not db_diagnosis:
        raise HTTPException(status_code=404, detail="Medical diagnosis not found")
    
    diagnosis_response = PatientMedicalDiagnosisList.model_validate(db_diagnosis)
    return SingleResponse(data=diagnosis_response)


@router.delete("/MedicalDiagnosisList/delete", response_model=SingleResponse[PatientMedicalDiagnosisList])
def delete_diagnosis(request: Request, diagnosis_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_diagnosis = crud_diagnosis.delete_diagnosis(db, diagnosis_id, user_id, user_full_name)
    if not db_diagnosis:
        raise HTTPException(status_code=404, detail="Medical diagnosis not found")
    
    diagnosis_response = PatientMedicalDiagnosisList.model_validate(db_diagnosis)
    return SingleResponse(data=diagnosis_response)