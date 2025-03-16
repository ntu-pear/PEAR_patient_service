from sqlalchemy.orm import Session
from ..models.patient_allocation_model import PatientAllocation

def get_guardian_id_by_patient(db: Session, patient_id: int):
    return db.query(PatientAllocation).filter(PatientAllocation.patientId == patient_id).first()