from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_guardian_crud as crud_guardian
from ..schemas.patient_guardian import (
    PatientGuardian,
    PatientGuardianCreate,
    PatientGuardianUpdate
) #TODO :note that this needs to be fixed

router = APIRouter()

@router.get("/Guardian", response_model=PatientGuardian)
def get_guardian(guardian_id: int, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.get_guardian(db, guardian_id)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.get("/Guardian/GetGuardianByNRIC", response_model=PatientGuardian)
def get_guardian_by_nric(nric: str, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.get_guardian_by_nric(db, nric)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.get("/Guardian/PatientGuardian", response_model=list[PatientGuardian])
def get_patient_guardian(patient_id: int, db: Session = Depends(get_db)):
    return crud_guardian.get_patient_guardian(db, patient_id)

@router.post("/Guardian/add", response_model=PatientGuardian)
def create_guardian(guardian: PatientGuardianCreate, db: Session = Depends(get_db)):
    return crud_guardian.create_guardian(db, guardian)

@router.put("/Guardian/update", response_model=PatientGuardian)
def update_guardian(guardian_id: int, guardian: PatientGuardianUpdate, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.update_guardian(db, guardian_id, guardian)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.delete("/Guardian/delete", response_model=PatientGuardian)
def delete_guardian(guardian_id: int, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.delete_guardian(db, guardian_id)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian
