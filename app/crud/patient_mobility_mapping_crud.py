import math
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
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

# Get all mobility entries
def get_all_mobility_entries(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientMobility).filter(PatientMobility.IsDeleted == False)
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    db_entries = (
        query.order_by(PatientMobility.MobilityID.desc())
             .offset(offset)
             .limit(pageSize)
             .all()
    )
    return db_entries, totalRecords, totalPages

def get_mobility_entry_by_mobility_id(db: Session, mobility_id: int):
    db_entry =  db.query(PatientMobility).filter(PatientMobility.IsDeleted == False, PatientMobility.MobilityID == mobility_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail=f"No mobility entries found for Mobility ID {mobility_id}.")
    return db_entry

# Get mobility entries by Patient ID
def get_mobility_entries_by_patient_id(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientMobility).filter(
        PatientMobility.PatientID == patient_id,
        PatientMobility.IsDeleted == False
    )
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    db_entries = (
        query.order_by(PatientMobility.MobilityID.desc())
             .offset(offset)
             .limit(pageSize)
             .all()
    )
    
    if not db_entries:
        raise HTTPException(status_code=404, detail=f"No mobility entries found for Patient ID {patient_id}.")

    return db_entries, totalRecords, totalPages

# Create a new mobility entry
def create_mobility_entry(db: Session, mobility_data: PatientMobilityCreate, created_by: str, user_full_name: str):
    # Validate PatientID
    patient = db.query(Patient).filter(Patient.id == mobility_data.PatientID).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid PatientID. No matching patient found.")

    # Validate MobilityListId
    mobility_list = db.query(PatientMobilityList).filter(PatientMobilityList.MobilityListId == mobility_data.MobilityListId).first()
    if not mobility_list:
        raise HTTPException(status_code=400, detail="Invalid MobilityListId. No matching mobility list found.")

    patient_not_recovered = db.query(PatientMobility).filter(
        PatientMobility.PatientID == mobility_data.PatientID,
        PatientMobility.IsRecovered == False,
        PatientMobility.IsDeleted == False
        ).first()
    
    if patient_not_recovered:
        existing_mobility = patient_not_recovered.MobilityListId != 0
        
        if existing_mobility:
            raise HTTPException(status_code=400, detail="Patient already has an existing mobility aid.")    

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

    updated_data_dict = serialize_data(mobility_data.model_dump())
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created mobility mapping entry",
        table="PatientMobility",
        entity_id=new_entry.MobilityID,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return new_entry

# Update an existing mobility entry
def update_mobility_entry(db: Session, mobility_id: int, mobility_data: PatientMobilityUpdate, modified_by: str, user_full_name: str):
    db_entry = db.query(PatientMobility).filter(
        PatientMobility.MobilityID == mobility_id,
        PatientMobility.IsDeleted == False,
    ).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail=f"Mobility entry with ID {mobility_id} not found.")

    original_data_dict = serialize_data(mobility_data.model_dump())

    for key, value in mobility_data.model_dump(exclude_unset=True).items():
        setattr(db_entry, key, value)

    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    db.commit()
    db.refresh(db_entry)

    updated_data_dict = serialize_data(mobility_data.model_dump())
    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Updated mobility mapping entry",
        table="PatientMobility",
        entity_id=db_entry.MobilityID,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )
    return db_entry

# Soft delete a mobility entry
def delete_mobility_entry(db: Session, mobility_id: int, modified_by: str, user_full_name: str):
    db_entry = db.query(PatientMobility).filter(
        PatientMobility.MobilityID == mobility_id,
        PatientMobility.IsDeleted == False,
    ).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail=f"Mobility entry with ID {mobility_id} not found.")

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    db_entry.IsDeleted = True
    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    db.commit()

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Deleted mobility mapping entry",
        table="PatientMobility",
        entity_id=db_entry.MobilityID,
        original_data=original_data_dict,
        updated_data=None,
    )
    return db_entry
