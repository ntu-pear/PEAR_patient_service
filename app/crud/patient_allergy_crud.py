from sqlalchemy.orm import Session
from ..models.patient_allergy_model import PatientAllergy
from ..schemas.patient_allergy import PatientAllergyCreate, PatientAllergyUpdate

def get_allergies(db: Session):
    return db.query(PatientAllergy).all()

def get_patient_allergy(db: Session, patient_id: int):
    return db.query(PatientAllergy).filter(PatientAllergy.patient_id == patient_id).all()

def create_allergy(db: Session, allergy: PatientAllergyCreate):
    db_allergy = PatientAllergy(**allergy.dict())
    db.add(db_allergy)
    db.commit()
    db.refresh(db_allergy)
    return db_allergy

def delete_allergy(db: Session, allergy_id: int, allergy: PatientAllergyUpdate):
    db_allergy = db.query(PatientAllergy).filter(PatientAllergy.id == allergy_id).first()
    if db_allergy:
        for key, value in allergy.dict().items():
            setattr(db_allergy, key, value)
        db.commit()
        db.refresh(db_allergy)
    return db_allergy
