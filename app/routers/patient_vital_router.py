from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_vital_crud as crud_vital
from ..schemas import patient_vital as schemas_vital

router = APIRouter()

@router.get("/Vital", response_model=schemas_vital.PatientVital)
def get_latest_vital(patient_id: int, db: Session = Depends(get_db)):
    db_vital = crud_vital.get_latest_vital(db, patient_id)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    return db_vital

@router.get("/Vital/list", response_model=list[schemas_vital.PatientVital])
def get_vital_list(patient_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_vital.get_vital_list(db, patient_id, skip=skip, limit=limit)

@router.post("/Vital/add", response_model=schemas_vital.PatientVital)
def create_vital(vital: schemas_vital.PatientVitalCreate, db: Session = Depends(get_db)):
    return crud_vital.create_vital(db, vital)

@router.put("/Vital/update/{vital_id}", response_model=schemas_vital.PatientVital)
def update_vital(vital_id: int, vital: schemas_vital.PatientVitalUpdate, db: Session = Depends(get_db)):
    db_vital = crud_vital.update_vital(db, vital_id, vital)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    return db_vital

@router.put("/Vital/delete", response_model=schemas_vital.PatientVital)
def delete_vital(vital: schemas_vital.PatientVitalDelete, db: Session = Depends(get_db)):
    db_vital = crud_vital.delete_vital(db, vital.Id)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    return db_vital
