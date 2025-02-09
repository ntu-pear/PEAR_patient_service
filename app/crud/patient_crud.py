from sqlalchemy.orm import Session
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

# To Change
user = 1
def mask_nric(nric: str):
    return ("*" * 5) + nric[-4:]


def get_patient(db: Session, patient_id: int, mask: bool = True):
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
    if db_patient and mask:
        db_patient.nric = mask_nric(db_patient.nric)
    return db_patient


def get_patients(db: Session, mask: bool = True, skip: int = 0, limit: int = 10):
    db_patients = (
        db.query(Patient)
        .filter(Patient.isDeleted == "0")
        .order_by(Patient.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = mask_nric(db_patient.nric)
    return db_patients


def create_patient(db: Session, patient: PatientCreate):
    db_patient = Patient(**patient.model_dump())
    
    updated_data_dict = serialize_data(patient.model_dump())
    if db_patient:
        db_patient.modifiedDate = datetime.now()
        db_patient.createdDate = datetime.now()
        db_patient.createdById = user
        db_patient.modifiedById = user
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        log_crud_action(
            action=ActionType.CREATE,
            user=user,
            table="Patient",
            entity_id=db_patient.id,
            original_data=None,
            updated_data=updated_data_dict,
        )
    return db_patient


def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        try: 
            original_data_dict = {
                k: serialize_data(v) for k, v in db_patient.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in patient.model_dump().items():
            setattr(db_patient, key, value)
        db_patient.modifiedDate = datetime.now()
        db_patient.modifiedById = user
        db.commit()
        db.refresh(db_patient)

        updated_data_dict = serialize_data(patient.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=user,
            table="Patient",
            entity_id=patient_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
    return db_patient


def delete_patient(db: Session, patient_id: int):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_patient.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        setattr(db_patient, "isDeleted", "1")
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=user,
            table="Patient",
            entity_id=patient_id,
            original_data=original_data_dict,
            updated_data=None,
        )
    return db_patient
