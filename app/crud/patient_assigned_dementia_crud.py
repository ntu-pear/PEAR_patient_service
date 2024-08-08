from sqlalchemy.orm import Session
from ..models.patient_assigned_dementia_model import PatientAssignedDementia
from ..schemas.patient_assigned_dementia import PatientAssignedDementiaCreate, PatientAssignedDementiaUpdate

def get_assigned_dementias(db: Session, patient_id: int):
    return db.query(PatientAssignedDementia).filter(PatientAssignedDementia.patient_id == patient_id).all()

def create_assigned_dementia(db: Session, assigned_dementia: PatientAssignedDementiaCreate):
    db_assigned_dementia = PatientAssignedDementia(**assigned_dementia.dict())
    db.add(db_assigned_dementia)
    db.commit()
    db.refresh(db_assigned_dementia)
    return db_assigned_dementia

def delete_assigned_dementia(db: Session, assigned_dementia_id: int, assigned_dementia: PatientAssignedDementiaUpdate):
    db_assigned_dementia = db.query(PatientAssignedDementia).filter(PatientAssignedDementia.id == assigned_dementia_id).first()
    if db_assigned_dementia:
        for key, value in assigned_dementia.dict().items():
            setattr(db_assigned_dementia, key, value)
        db.commit()
        db.refresh(db_assigned_dementia)
    return db_assigned_dementia
