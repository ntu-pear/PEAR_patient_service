from sqlalchemy.orm import Session
from ..models.patient_prescription_model import PatientPrescription
from ..schemas.patient_prescription import PatientPrescriptionCreate, PatientPrescriptionUpdate

def get_prescriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PatientPrescription).order_by(PatientPrescription.id).offset(skip).limit(limit).all()

def get_patient_prescriptions(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return db.query(PatientPrescription).filter(PatientPrescription.patientId == patient_id).order_by(PatientPrescription.id).offset(skip).limit(limit).all()

def get_prescription(db: Session, prescription_id: int):
    return db.query(PatientPrescription).filter(PatientPrescription.id == prescription_id).first()

def create_prescription(db: Session, prescription: PatientPrescriptionCreate):
    db_prescription = PatientPrescription(**prescription.dict())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def update_prescription(db: Session, prescription_id: int, prescription: PatientPrescriptionUpdate):
    db_prescription = db.query(PatientPrescription).filter(PatientPrescription.id == prescription_id).first()
    if db_prescription:
        for key, value in prescription.dict().items():
            setattr(db_prescription, key, value)
        db.commit()
        db.refresh(db_prescription)
    return db_prescription

def delete_prescription(db: Session, prescription_id: int, prescription: PatientPrescriptionUpdate):
    db_prescription = db.query(PatientPrescription).filter(PatientPrescription.id == prescription_id).first()
    if db_prescription:
        setattr(db_prescription, "active", "0")
        db.commit()
        db.refresh(db_prescription)
    return db_prescription
