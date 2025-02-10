from sqlalchemy.orm import Session
from ..models.patient_prescription_model import PatientPrescription
from ..schemas.patient_prescription import PatientPrescriptionCreate, PatientPrescriptionUpdate
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

user = 1

def get_prescriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PatientPrescription).order_by(PatientPrescription.Id).offset(skip).limit(limit).all()

def get_patient_prescriptions(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return db.query(PatientPrescription).filter(PatientPrescription.PatientId == patient_id).order_by(PatientPrescription.Id).offset(skip).limit(limit).all()

def get_prescription(db: Session, prescription_id: int):
    return db.query(PatientPrescription).filter(PatientPrescription.Id == prescription_id).first()

def create_prescription(db: Session, prescription: PatientPrescriptionCreate):
    db_prescription = PatientPrescription(**prescription.model_dump())
    updated_data_dict = serialize_data(prescription.model_dump())

    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    log_crud_action(
        action=ActionType.CREATE,
        user=user,
        table="PatientPrescription",
        entity_id=db_prescription.Id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_prescription

def update_prescription(db: Session, prescription_id: int, prescription: PatientPrescriptionUpdate):
    db_prescription = db.query(PatientPrescription).filter(PatientPrescription.Id == prescription_id).first()
    if db_prescription:
        try: 
            original_data_dict = {
            k: serialize_data(v) for k, v in db_prescription.__dict__.items() if not k.startswith("_")
        }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in prescription.model_dump().items():
            setattr(db_prescription, key, value)
        db.commit()
        db.refresh(db_prescription)

        updated_data_dict = serialize_data(prescription.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=user,
            table="PatientPrescription",
            entity_id=db_prescription.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )

    return db_prescription

def delete_prescription(db: Session, prescription_id: int, prescription: PatientPrescriptionUpdate):
    db_prescription = db.query(PatientPrescription).filter(PatientPrescription.Id == prescription_id).first()
    if db_prescription:
        try: 
            original_data_dict = {
            k: serialize_data(v) for k, v in db_prescription.__dict__.items() if not k.startswith("_")
        }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_prescription, "IsDeleted", "1")
        db.commit()
        db.refresh(db_prescription)

        log_crud_action(
            action=ActionType.DELETE,
            user=user,
            table="PatientPrescription",
            entity_id=db_prescription.Id,
            original_data=original_data_dict,
            updated_data=None,
        )
    return db_prescription
