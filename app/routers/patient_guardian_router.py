from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_guardian_crud as crud_guardian
from ..schemas import patient_guardian as schemas_guardian

router = APIRouter()

@router.get("/Guardian", response_model=schemas_guardian.Guardian)
def get_guardian(guardian_id: int, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.get_guardian(db, guardian_id)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.get("/Guardian/GetGuardianByNRIC", response_model=schemas_guardian.Guardian)
def get_guardian_by_nric(nric: str, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.get_guardian_by_nric(db, nric)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.get("/Guardian/PatientGuardian", response_model=list[schemas_guardian.Guardian])
def get_patient_guardian(patient_id: int, db: Session = Depends(get_db)):
    return crud_guardian.get_patient_guardian(db, patient_id)

@router.post("/Guardian/add", response_model=schemas_guardian.Guardian)
def create_guardian(guardian: schemas_guardian.GuardianCreate, db: Session = Depends(get_db)):
    return crud_guardian.create_guardian(db, guardian)

@router.put("/Guardian/update", response_model=schemas_guardian.Guardian)
def update_guardian(guardian_id: int, guardian: schemas_guardian.GuardianUpdate, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.update_guardian(db, guardian_id, guardian)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.put("/Guardian/delete", response_model=schemas_guardian.Guardian)
def delete_guardian(guardian_id: int, guardian: schemas_guardian.GuardianUpdate, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.delete_guardian(db, guardian_id, guardian)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian
