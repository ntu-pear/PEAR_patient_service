from typing import List
from sqlalchemy.orm import Session
from ..models.patient_guardian_model import PatientGuardian
from ..schemas.patient_guardian import PatientGuardianCreate, PatientGuardianUpdate
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

SYSTEM_USER_ID = 1

def get_guardian(db: Session, guardian_id: int):
    return db.query(PatientGuardian).filter(PatientGuardian.id == guardian_id).first()

def get_guardian_by_id_list(db: Session, guardian_ids: List[int]):
  return db.query(PatientGuardian).filter(PatientGuardian.id.in_(guardian_ids)).all()
  
def get_guardian_by_nric(db: Session, nric: str):
    return db.query(PatientGuardian).filter(PatientGuardian.nric == nric).first()

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
        updated_data=updated_data_dict
    )
    return db_guardian

def update_guardian(
    db: Session, guardian_id: int, guardian: PatientGuardianUpdate
):
    db_guardian = (
        db.query(PatientGuardian)
        .filter(PatientGuardian.id == guardian_id)
        .first()
    )

    if db_guardian:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_guardian.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in guardian.model_dump().items():
            setattr(db_guardian, key, value)

        db.commit()
        db.refresh(db_guardian)

        updated_data_dict = serialize_data(guardian.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            table="PatientGuardian",
            entity_id=guardian_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )
    return db_guardian

def delete_guardian(db: Session, guardian_id: int):
    db_guardian = db.query(PatientGuardian).filter(PatientGuardian.id == guardian_id).first()
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
            updated_data=None
        )
    return db_guardian
