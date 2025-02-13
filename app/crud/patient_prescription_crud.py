from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.patient_prescription_model import PatientPrescription
from ..schemas.patient_prescription import PatientPrescriptionCreate, PatientPrescriptionUpdate
import math

def get_prescriptions(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    db_prescription =  db.query(PatientPrescription).filter(PatientPrescription.IsDeleted == '0').order_by(PatientPrescription.Id).offset(offset).limit(pageSize).all()
    totalRecords = db.query(func.count()).select_from(PatientPrescription).filter(PatientPrescription.IsDeleted == '0').scalar()
    totalPages = math.ceil(totalRecords/pageSize)
    return db_prescription, totalRecords, totalPages

def get_patient_prescriptions(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 100):
    offset = pageNo * pageSize
    db_prescription =  db.query(PatientPrescription).filter(PatientPrescription.PatientId == patient_id, PatientPrescription.IsDeleted == '0').order_by(PatientPrescription.Id).offset(offset).limit(pageSize).all()
    totalRecords = db.query(func.count()).select_from(PatientPrescription).filter(PatientPrescription.PatientId == patient_id, PatientPrescription.IsDeleted == '0').scalar()
    totalPages = math.ceil(totalRecords/pageSize)
    return db_prescription, totalRecords, totalPages

def get_prescription(db: Session, prescription_id: int):
    return db.query(PatientPrescription).filter(PatientPrescription.Id == prescription_id).first()

def create_prescription(db: Session, prescription: PatientPrescriptionCreate):
    db_prescription = PatientPrescription(**prescription.model_dump())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def update_prescription(db: Session, prescription_id: int, prescription: PatientPrescriptionUpdate):
    db_prescription = db.query(PatientPrescription).filter(PatientPrescription.Id == prescription_id).first()
    if db_prescription:
        for key, value in prescription.model_dump().items():
            setattr(db_prescription, key, value)
        db.commit()
        db.refresh(db_prescription)
    return db_prescription

def delete_prescription(db: Session, prescription_id: int, prescription: PatientPrescriptionUpdate):
    db_prescription = db.query(PatientPrescription).filter(PatientPrescription.Id == prescription_id).first()
    if db_prescription:
        setattr(db_prescription, "IsDeleted", "1")
        db.commit()
        db.refresh(db_prescription)
    return db_prescription
