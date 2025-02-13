from app.models.patient_mobility_list_model import PatientMobilityList
from app.models.patient_model import Patient
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from ..models.patient_mobility_mapping_model import PatientMobility
from ..schemas.patient_mobility_mapping import (
    PatientMobilityCreate,
    PatientMobilityUpdate,
    PatientMobilityResponse,
)

# Get all mobility entries
def get_all_mobility_entries(db: Session):
    return db.query(PatientMobility).filter(PatientMobility.IsDeleted == False).all()

# Get mobility entries by Patient ID
def get_mobility_entries_by_id(db: Session, patient_id: int):
    entries = db.query(PatientMobility).filter(
        PatientMobility.PatientID == patient_id,
        PatientMobility.IsDeleted == False
    ).all()

    if not entries:
        raise HTTPException(status_code=404, detail=f"No mobility entries found for Patient ID {patient_id}.")

    return entries

# Create a new mobility entry
def create_mobility_entry(db: Session, mobility_data: PatientMobilityCreate, created_by: int):
    # Validate PatientID
    patient = db.query(Patient).filter(Patient.id == mobility_data.PatientID).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid PatientID. No matching patient found.")

    # Validate MobilityListId
    mobility_list = db.query(PatientMobilityList).filter(PatientMobilityList.MobilityListId == mobility_data.MobilityListId).first()
    if not mobility_list:
        raise HTTPException(status_code=400, detail="Invalid MobilityListId. No matching mobility list found.")

    # Create entry
    new_entry = PatientMobility(
        **mobility_data.model_dump(),
        CreatedDateTime=datetime.utcnow(),
        ModifiedDateTime=datetime.utcnow(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

# Update an existing mobility entry
def update_mobility_entry(
    db: Session, patient_id: int, mobility_data: PatientMobilityUpdate, modified_by: int
):
    db_entry = db.query(PatientMobility).filter(
        PatientMobility.PatientID == patient_id,
        PatientMobility.IsDeleted == False,
    ).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail=f"Mobility entry with ID {patient_id} not found.")

    for key, value in mobility_data.model_dump(exclude_unset=True).items():
        setattr(db_entry, key, value)

    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    db.commit()
    db.refresh(db_entry)
    return db_entry

# Soft delete a mobility entry
def delete_mobility_entry(db: Session, patient_id: int, modified_by: int):
    db_entry = db.query(PatientMobility).filter(
        PatientMobility.PatientID == patient_id,
        PatientMobility.IsDeleted == False,
    ).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail=f"Mobility entry with ID {patient_id} not found.")

    db_entry.IsDeleted = True
    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    db.commit()
    return db_entry
