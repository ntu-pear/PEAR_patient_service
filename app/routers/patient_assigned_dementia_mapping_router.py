from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_assigned_dementia_mapping_crud as crud_assigned_dementia
from ..schemas import patient_assigned_dementia_mapping as schemas_assigned_dementia

router = APIRouter()

@router.get("/PatientAssignedDementia", response_model=list[schemas_assigned_dementia.PatientAssignedDementia])
def get_assigned_dementias(patient_id: int, db: Session = Depends(get_db)):
    return crud_assigned_dementia.get_assigned_dementias(db, patient_id)

@router.post("/PatientAssignedDementia/add", response_model=schemas_assigned_dementia.PatientAssignedDementia)
def create_assigned_dementia(assigned_dementia: schemas_assigned_dementia.PatientAssignedDementiaCreate, db: Session = Depends(get_db)):
    return crud_assigned_dementia.create_assigned_dementia(db, assigned_dementia)

@router.put("/PatientAssignedDementia/delete", response_model=schemas_assigned_dementia.PatientAssignedDementia)
def delete_assigned_dementia(assigned_dementia_id: int, assigned_dementia: schemas_assigned_dementia.PatientAssignedDementiaUpdate, db: Session = Depends(get_db)):
    db_assigned_dementia = crud_assigned_dementia.delete_assigned_dementia(db, assigned_dementia_id, assigned_dementia)
    if not db_assigned_dementia:
        raise HTTPException(status_code=404, detail="Assigned dementia not found")
    return db_assigned_dementia
