from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.patient_patient_guardian_model import PatientPatientGuardian

from ..crud import patient_guardian_relationship_mapping_crud
from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_guardian_model import PatientGuardian
from ..models.patient_model import Patient
from ..schemas.patient_guardian import PatientGuardianCreate, PatientGuardianUpdate

SYSTEM_USER_ID = "1"

def get_guardian(db: Session, guardian_id: int):
    return db.query(PatientGuardian).filter(
        PatientGuardian.id == guardian_id,
        PatientGuardian.isDeleted == "0", 
        PatientGuardian.active == "Y"     
    ).first()

def get_guardian_by_id_list(db: Session, guardian_ids: List[int]):
    return db.query(PatientGuardian).filter(
        PatientGuardian.id.in_(guardian_ids),
        PatientGuardian.isDeleted == "0",
        PatientGuardian.active == "Y"
    ).all()
  
def get_guardian_by_nric(db: Session, nric: str):
    return db.query(PatientGuardian).filter(
        PatientGuardian.nric == nric,
        PatientGuardian.isDeleted == "0",
        PatientGuardian.active == "Y"
    ).first()

def create_guardian(
    db: Session, guardian: PatientGuardianCreate
):
    guardian_data = guardian.model_dump(exclude={'patientId', 'relationshipName'})
    db_guardian = PatientGuardian(**guardian_data)
    updated_data_dict = serialize_data(guardian_data)
    db.add(db_guardian)
    db.commit()
    db.refresh(db_guardian)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        table="PatientGuardian",
        entity_id=db_guardian.id,
        original_data=None,
        updated_data=updated_data_dict,
        user_full_name="None",
        message=f"create new guardian {db_guardian.firstName} {db_guardian.lastName}",
        is_system_config= True,
        log_type= "config_guardian_info",
    )
    return db_guardian

def update_guardian(
    db: Session, guardian_id: int, guardian: PatientGuardianUpdate
):
    # 1. Get the guardian
    db_guardian = get_guardian(db, guardian_id) 
    
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    
    # 2. Validate relationshipName exists in PATIENT_GUARDIAN_RELATIONSHIP_MAPPING table
    relationship_mapping = patient_guardian_relationship_mapping_crud.get_relationshipId_by_relationshipName(
        db, guardian.relationshipName
    )
    if not relationship_mapping:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid relationshipName: '{guardian.relationshipName}'"
        )
    
    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_guardian.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"
    
    # 3. Update guardian info (excluding patientId and relationshipName)
    guardian_data = guardian.model_dump(exclude={'patientId', 'relationshipName'})
    for key, value in guardian_data.items():
        setattr(db_guardian, key, value)
    
    db.commit()
    db.refresh(db_guardian)
    
    updated_data_dict = serialize_data(guardian_data)
    log_crud_action(
        action=ActionType.UPDATE,
        user=SYSTEM_USER_ID,
        table="PatientGuardian",
        entity_id=guardian_id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        user_full_name="None",
        message=f"Update guardian {db_guardian.firstName} {db_guardian.lastName}",
        is_system_config= True,
        log_type= "config_guardian_info",
    )
    
    # 4. Update the relationship mapping in PATIENT_PATIENT_GUARDIAN table
    db_patient_guardian_relationship = (
        db.query(PatientPatientGuardian)
        .filter(
            PatientPatientGuardian.guardianId == guardian_id,
            PatientPatientGuardian.patientId == guardian.patientId,
            PatientPatientGuardian.isDeleted == "0" 
        )
        .first()
    )
    
    if not db_patient_guardian_relationship:
        raise HTTPException(
            status_code=404,
            detail=f"No relationship found between guardian {guardian_id} and patient {guardian.patientId}"
        )
    
    try:
        original_relationship_data = {
            k: serialize_data(v) for k, v in db_patient_guardian_relationship.__dict__.items() 
            if not k.startswith("_")
        }
    except Exception as e:
        original_relationship_data = "{}"
    
    # Update the relationshipId if it changed
    if db_patient_guardian_relationship.relationshipId != relationship_mapping.id:
        db_patient_guardian_relationship.relationshipId = relationship_mapping.id
        db_patient_guardian_relationship.ModifiedById = guardian.ModifiedById
        db.commit()
        db.refresh(db_patient_guardian_relationship)

        patient = db.query(Patient).filter(Patient.id == db_patient_guardian_relationship.patientId).first()
        patient_name = patient.name if patient else None

        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            table="PatientPatientGuardian",
            entity_id=db_patient_guardian_relationship.id,
            original_data=original_relationship_data,
            updated_data={"relationshipId": relationship_mapping.id},
            user_full_name="None",
            message=f"Updated relationship: {db_guardian.firstName} {db_guardian.lastName} is now {guardian.relationshipName} of {patient_name}",
            patient_id = guardian.patientId,
            patient_full_name = patient_name,
            log_type= "guardian_relationship",
        )
    
    return db_guardian

def delete_guardian(db: Session, guardian_id: int):
    db_guardian = get_guardian(db, guardian_id)

    if db_guardian:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_guardian.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_guardian, 'isDeleted', '1')
        db.commit()
        db.refresh(db_guardian)

        log_crud_action(
            action=ActionType.DELETE,
            user=SYSTEM_USER_ID,
            table="PatientGuardian",
            entity_id=db_guardian.id,
            original_data=original_data_dict,
            updated_data=None,
            user_full_name="None",
            message=f"Delete guardian {db_guardian.firstName} {db_guardian.lastName}",
            is_system_config= True,
            log_type= "config_guardian_info",
        )
    return db_guardian