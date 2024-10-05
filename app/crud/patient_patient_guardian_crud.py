from sqlalchemy.orm import Session
from ..models.patient_model import Patient
from ..models.patient_guardian_model import PatientGuardian
from ..models.patient_guardian_relationship_mapping_model import PatientGuardianRelationshipMapping
from ..models.patient_patient_guardian_model import PatientPatientGuardian
from ..schemas.patient_patient_guardian import PatientPatientGuardianCreate, PatientPatientGuardianUpdate


def get_all_patient_guardian(db: Session, id: int, limit: int = 10):
    return db.query(PatientPatientGuardian).order_by(PatientPatientGuardian.id).limit(limit).all()

def get_all_patient_guardian_by_patientId(db: Session, patientId: int):
    query = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.patientId == patientId).all()
    print(query)
    return query

def get_all_patient_patient_guardian_by_guardianId(db: Session, guardianId: int):
    return db.query(Patient).join(PatientPatientGuardian).filter(PatientPatientGuardian.guardianId == guardianId).all()

def get_patient_patient_guardian_by_guardianId_and_patientId(db: Session, guardianId: int, patientId: int):
    return db.query(PatientPatientGuardian).filter(PatientPatientGuardian.guardianId == guardianId).filter(PatientPatientGuardian.patientId == patientId).first()

def create_patient_patient_guardian(db: Session, patientPatientGuradian: PatientPatientGuardianCreate):
    db_patient_patient_guardian = PatientPatientGuardian(**patientPatientGuradian)
    db.add(db_patient_patient_guardian)
    db.commit()
    db.refresh(db_patient_patient_guardian)
    return db_patient_patient_guardian

def update_patient_patient_guardian(db: Session, id: int, patientPatientGuradian: PatientPatientGuardianUpdate):
    db_relationship = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.id == id).first()
    if db_relationship:
        for key, value in patientPatientGuradian.dict().items():
            setattr(db_relationship, key, value)
        db.commit()
        db.refresh(db_relationship)
    return db_relationship

def delete_patient_patient_guardian_by_guardianId(db: Session, guardianId: int):
    db_relationship = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.guardianId == guardianId).first()
    if db_relationship:
        setattr(db_relationship, "isDeleted", "1")
        db.commit()
        db.refresh(db_relationship)
    return db_relationship

def delete_relationship(db: Session, id: int):
    db_relationship = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.id == id).first()
    if db_relationship:
        setattr(db_relationship, "isDeleted", "1")
        db.commit()
    return db_relationship
