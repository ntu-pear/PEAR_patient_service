from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_mobility_crud as crud_mobility
from ..schemas import patient_mobility as schemas_mobility

router = APIRouter()

@router.get("/Mobility/PatientMobility", response_model=list[schemas_mobility.PatientMobility])
def get_patient_mobility(patient_id: int, db: Session = Depends(get_db)):
    return crud_mobility.get_patient_mobility(db, patient_id)

@router.post("/Mobility/add", response_model=schemas_mobility.PatientMobility)
def create_patient_mobility(mobility: schemas_mobility.PatientMobilityCreate, db: Session = Depends(get_db)):
    return crud_mobility.create_patient_mobility(db, mobility)

@router.put("/Mobility/update", response_model=schemas_mobility.PatientMobility)
def update_patient_mobility(mobility_id: int, mobility: schemas_mobility.PatientMobilityUpdate, db: Session = Depends(get_db)):
    db_mobility = crud_mobility.update_patient_mobility(db, mobility_id, mobility)
    if not db_mobility:
        raise HTTPException(status_code=404, detail="Patient mobility not found")
    return db_mobility

@router.put("/Mobility/delete", response_model=schemas_mobility.PatientMobility)
def delete_patient_mobility(mobility_id: int, mobility: schemas_mobility.PatientMobilityUpdate, db: Session = Depends(get_db)):
    db_mobility = crud_mobility.delete_patient_mobility(db, mobility_id, mobility)
    if not db_mobility:
        raise HTTPException(status_code=404, detail="Patient mobility not found")
    return db_mobility
