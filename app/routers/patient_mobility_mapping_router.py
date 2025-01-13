from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.patient_mobility_mapping import (
    PatientMobilityCreate,
    PatientMobilityUpdate,
    PatientMobilityResponse,
)
from ..crud import patient_mobility_mapping_crud

router = APIRouter()

@router.get("/MobilityMapping/List", response_model=list[PatientMobilityResponse])
def get_all_mobility_entries(db: Session = Depends(get_db)):
    return patient_mobility_mapping_crud.get_all_mobility_entries(db)

@router.get("/MobilityMapping/List/{mobility_id}", response_model=PatientMobilityResponse)
def get_mobility_entry(mobility_id: int, db: Session = Depends(get_db)):
    return patient_mobility_mapping_crud.get_mobility_entry_by_id(db, mobility_id)

@router.post("/MobilityMapping/List", response_model=PatientMobilityResponse)
def create_mobility_entry(
    mobility_data: PatientMobilityCreate, db: Session = Depends(get_db)
):
    # Replace `1` with the current user's ID if available
    return patient_mobility_mapping_crud.create_mobility_entry(db, mobility_data, created_by=1)

@router.put("MobilityMapping/List/{mobility_id}", response_model=PatientMobilityResponse)
def update_mobility_entry(
    mobility_id: int,
    mobility_data: PatientMobilityUpdate,
    db: Session = Depends(get_db),
):
    # Replace `1` with the current user's ID if available
    return patient_mobility_mapping_crud.update_mobility_entry(
        db, mobility_id, mobility_data, modified_by=1
    )

@router.delete("/MobilityMapping/List/{mobility_id}", response_model=PatientMobilityResponse)
def delete_mobility_entry(mobility_id: int, db: Session = Depends(get_db)):
    # Replace `1` with the current user's ID if available
    return patient_mobility_mapping_crud.delete_mobility_entry(db, mobility_id, modified_by=1)
