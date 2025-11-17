from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.patient_allocation_model import PatientAllocation
from ..models.patient_guardian_model import PatientGuardian
from ..schemas.patient_allocation import PatientAllocationCreate, PatientAllocationUpdate
from datetime import datetime

def get_allocation_by_id(db: Session, allocation_id: int):
    try:
        res = db.query(PatientAllocation, PatientGuardian.guardianApplicationUserId).join(
            PatientGuardian, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.id == allocation_id
        ).first()
        
        if not res: return None
        
        allocation, guardian_user_id = res
        data = allocation.__dict__.copy()
        data["guardianApplicationUserId"] = guardian_user_id
        data.pop('_sa_instance_state',None)
        return data
    
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_allocation_by_patient(db: Session, patient_id: int):
    try:
        res = db.query(PatientAllocation, PatientGuardian.guardianApplicationUserId).join(
            PatientGuardian, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.patientId == patient_id,
            PatientAllocation.active == "Y"
        ).first()
        
        if not res: return None

        allocation, guardian_user_id = res
        data = allocation.__dict__.copy()
        data["guardianApplicationUserId"] = guardian_user_id
        data.pop('_sa_instance_state',None)
        return data
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_guardian_id_by_patient(db: Session, patient_id: int):
    try:
        res = db.query(PatientGuardian.guardianApplicationUserId).join(
            PatientAllocation, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.patientId == patient_id
        ).first()
        
        if not res: return None
        
        return res[0]
        
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_all_allocations(db: Session, skip: int = 0, limit: int = 100):
    try:
        res = db.query(PatientAllocation, PatientGuardian.guardianApplicationUserId).join(
            PatientGuardian, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.active == "Y"
        ).order_by(
            PatientAllocation.id
        ).offset(
            skip
        ).limit(
            limit
        ).all()
        if not res: return None
        allocation_list = []
        
        for allocation, guardian_user_id in res:
            data = allocation.__dict__.copy()
            data["guardianApplicationUserId"] = guardian_user_id
            data.pop('_sa_instance_state',None)
            allocation_list.append(data)
            
        return allocation_list
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def create_allocation(db: Session, allocation: PatientAllocationCreate, user_id: str, user_full_name: str):
    try:
        # Check if patient already has an active allocation
        existing = get_allocation_by_patient(db, allocation.patientId)
        if existing:
            raise ValueError("Patient already has an active allocation")

        db_allocation = PatientAllocation(
            active="Y",
            patientId=allocation.patientId,
            doctorId=allocation.doctorId,
            gameTherapistId=allocation.gameTherapistId,
            supervisorId=allocation.supervisorId,
            caregiverId=allocation.caregiverId,
            guardianId=allocation.guardianId,
            tempDoctorId=allocation.tempDoctorId,
            tempCaregiverId=allocation.tempCaregiverId,
            guardian2Id=allocation.guardian2Id,
            createdDate=datetime.now(),
            modifiedDate=datetime.now(),
            CreatedById=user_id,
            ModifiedById=user_id
        )
        db.add(db_allocation)
        db.commit()
        db.refresh(db_allocation)
        return db_allocation
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update_allocation(db: Session, allocation_id: int, allocation: PatientAllocationUpdate, user_id: str):
    try:
        db_allocation = get_allocation_by_id(db, allocation_id)
        if not db_allocation:
            return None
            
        if db_allocation.active != "Y":
            raise ValueError("Cannot update inactive allocation")
            
        update_data = allocation.model_dump(exclude_unset=True)
        update_data["modifiedDate"] = datetime.now()
        update_data["ModifiedById"] = user_id
        
        for key, value in update_data.items():
            setattr(db_allocation, key, value)
            
        db.commit()
        db.refresh(db_allocation)
        return db_allocation
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def delete_allocation(db: Session, allocation_id: int, user_id: str):
    try:
        db_allocation = get_allocation_by_id(db, allocation_id)
        if not db_allocation:
            return None
            
        if db_allocation.active != "Y":
            raise ValueError("Allocation is already inactive")
            
        db_allocation.isDeleted = "1"
        db_allocation.modifiedDate = datetime.now()
        db_allocation.ModifiedById = user_id
        db.commit()
        return db_allocation
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    