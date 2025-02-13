from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_vital_crud as crud_vital
from ..schemas.patient_vital import PatientVital,PatientVitalCreate,PatientVitalDelete, PatientVitalUpdate
from ..schemas.response import SingleResponse, PaginatedResponse

router = APIRouter()

@router.get("/Vital", response_model=SingleResponse[PatientVital])
def get_latest_vital(patient_id: int, db: Session = Depends(get_db)):
    db_vital = crud_vital.get_latest_vital(db, patient_id)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    vital = PatientVital.model_validate(db_vital)
    return SingleResponse(data = vital)

@router.get("/Vital/list", response_model=PaginatedResponse[PatientVital])
def get_vital_list(patient_id: int, pageNo: int = 0, pageSize: int = 100, db: Session = Depends(get_db)):
    vitals, totalRecords, totalPages = crud_vital.get_vital_list(db=db, patient_id = patient_id, pageNo=pageNo, pageSize=pageSize)
    vitals = [PatientVital.model_validate(vital) for vital in vitals]
    return PaginatedResponse(data=vitals, pageNo=pageNo, pageSize=pageSize, totalRecords= totalRecords, totalPages=totalPages)

@router.post("/Vital/add", response_model=SingleResponse[PatientVital])
def create_vital(vital: PatientVitalCreate, db: Session = Depends(get_db)):
    db_vital = crud_vital.create_vital(db, vital)
    vital = PatientVital.model_validate(db_vital)
    return SingleResponse(data=vital)

@router.put("/Vital/update/{vital_id}", response_model=SingleResponse[PatientVital])
def update_vital(vital_id: int, vital: PatientVitalUpdate, db: Session = Depends(get_db)):
    db_vital = crud_vital.update_vital(db, vital_id, vital)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    vital = PatientVital.model_validate(db_vital)
    return SingleResponse(data=vital)

@router.put("/Vital/delete", response_model=SingleResponse[PatientVital])
def delete_vital(vital: PatientVitalDelete, db: Session = Depends(get_db)):
    db_vital = crud_vital.delete_vital(db, vital.Id)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    vital = PatientVital.model_validate(db_vital)
    return SingleResponse(data=vital)
