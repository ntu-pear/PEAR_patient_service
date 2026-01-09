from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_crud as crud_patient
from ..crud import patient_medical_diagnosis_list_crud as crud_diagnosis
from ..crud import patient_medical_history_crud as crud_medical_history
from ..database import get_db
from ..schemas.patient_medical_history import (
    PatientMedicalHistory,
    PatientMedicalHistoryCreate,
    PatientMedicalHistoryUpdate,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()


@router.get("/MedicalHistory/GetByPatient", response_model=PaginatedResponse[PatientMedicalHistory])
def get_medical_histories_by_patient(request: Request, patient_id: int, pageNo: int = 0, pageSize: int = 10, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)

    if not crud_patient.get_patient(db, patient_id):
        raise HTTPException(status_code=404, detail="Patient does not exist")
    
    db_histories, totalRecords, totalPages = crud_medical_history.get_medical_histories_by_patient(
        db=db, patient_id=patient_id, pageNo=pageNo, pageSize=pageSize
    )
    histories = [PatientMedicalHistory.model_validate(history) for history in db_histories]
    return PaginatedResponse(data=histories, pageNo=pageNo, pageSize=pageSize, totalRecords=totalRecords, totalPages=totalPages)


@router.get("/MedicalHistory/{history_id}", response_model=SingleResponse[PatientMedicalHistory])
def get_medical_history(request: Request, history_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)

    db_medical_history = crud_medical_history.get_medical_history_by_id(db, history_id)
    if not db_medical_history:
        raise HTTPException(status_code=404, detail="Medical history record not found")
    
    medical_history = PatientMedicalHistory.model_validate(db_medical_history)
    return SingleResponse(data=medical_history)


@router.post("/MedicalHistory/add", response_model=SingleResponse[PatientMedicalHistory])
def create_medical_history(request: Request, medical_history: PatientMedicalHistoryCreate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    # Validate patient exists
    if not crud_patient.get_patient(db, medical_history.PatientID):
        raise HTTPException(status_code=404, detail="Patient does not exist")
    
    # Validate diagnosis exists
    if not crud_diagnosis.get_diagnosis_by_id(db, medical_history.MedicalDiagnosisID):
        raise HTTPException(status_code=404, detail="Medical diagnosis does not exist")
    
    db_medical_history = crud_medical_history.create_medical_history(db, medical_history, user_id, user_full_name)
    medical_history_response = PatientMedicalHistory.model_validate(db_medical_history)
    return SingleResponse(data=medical_history_response)


@router.put("/MedicalHistory/update", response_model=SingleResponse[PatientMedicalHistory])
def update_medical_history(request: Request, history_id: int, medical_history: PatientMedicalHistoryUpdate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    # Validate diagnosis exists if provided
    if medical_history.MedicalDiagnosisID is not None:
        if not crud_diagnosis.get_diagnosis_by_id(db, medical_history.MedicalDiagnosisID):
            raise HTTPException(status_code=404, detail="Medical diagnosis does not exist")
    
    db_medical_history = crud_medical_history.update_medical_history(db, history_id, medical_history, user_id, user_full_name)
    if not db_medical_history:
        raise HTTPException(status_code=404, detail="Medical history record not found")
    
    medical_history_response = PatientMedicalHistory.model_validate(db_medical_history)
    return SingleResponse(data=medical_history_response)


@router.delete("/MedicalHistory/delete", response_model=SingleResponse[PatientMedicalHistory])
def delete_medical_history(request: Request, history_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_medical_history = crud_medical_history.delete_medical_history(db, history_id, user_id, user_full_name)
    if not db_medical_history:
        raise HTTPException(status_code=404, detail="Medical history record not found")
    
    medical_history_response = PatientMedicalHistory.model_validate(db_medical_history)
    return SingleResponse(data=medical_history_response)