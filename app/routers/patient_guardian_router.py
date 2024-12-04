from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import (
    patient_crud as crud_patient,
    patient_guardian_crud as crud_guardian,
    patient_patient_guardian_crud as crud_patient_patient_guardian,
    patient_guardian_relationship_mapping_crud as crud_relationship
)
from ..schemas.patient_patient_guardian import (
    PatientPatientGuardianByGuardian,
    PatientPatientGuardianByPatient
) 

from ..schemas.patient_guardian import (
    PatientGuardian,
    PatientGuardianCreate,
    PatientGuardianUpdate,
) #TODO :note that this needs to be fixed

router = APIRouter()

@router.get("/Guardian/GetPatientGuardianByGuardianId", response_model=PatientPatientGuardianByGuardian)
def get_patient_guardian_by_guardianId(guardian_id: int, db: Session = Depends(get_db)):
    db_guardian = crud_patient_patient_guardian.get_all_patient_patient_guardian_by_guardianId(db,guardian_id)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian


@router.get("/Guardian/GetPatientGuardianByNRIC", response_model=PatientPatientGuardianByGuardian)
def get_patient_guardian_by_nric(nric: str, db: Session = Depends(get_db)):
    guardian = crud_guardian.get_guardian_by_nric(db, nric)
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    db_guardian = crud_patient_patient_guardian.get_all_patient_patient_guardian_by_guardianId(db,guardian.id)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Error")
    return db_guardian

@router.get("/Guardian/GetPatientGuardianByPatientId", response_model=PatientPatientGuardianByPatient)
def get_patient_guardian_by_patient_id(patient_id: int, db: Session = Depends(get_db)):
    patient_patient_guardian = crud_patient_patient_guardian.get_all_patient_guardian_by_patientId(db, patient_id)
    return patient_patient_guardian

@router.post("/Guardian/add", response_model=PatientGuardianCreate)
def create_patient_guardian(guardian: PatientGuardianCreate, db: Session = Depends(get_db)):
    db_relationship_id = crud_relationship.get_relationshipId_by_relationshipName(db, guardian.relationshipName)
    if not db_relationship_id:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db_guardian =  crud_guardian.create_guardian(db, guardian)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Error when creating patient guardian")
    db_patient = crud_patient.get_patient(db, guardian.patientId)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_patient_patient_guardian = {
        "guardianId" : db_guardian.id,
        "patientId" : guardian.patientId,
        "relationshipId" : db_relationship_id.id,
        "createdById": db_guardian.createdById,
        "modifiedById": db_guardian.modifiedById
    }
    db_patient_patient_guardian = crud_patient_patient_guardian.create_patient_patient_guardian(db,db_patient_patient_guardian)
    return guardian


@router.put("/Guardian/update", response_model=PatientGuardian)
def update_patient_guardian(guardian_id: int, guardian: PatientGuardianUpdate, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.update_guardian(db, guardian_id, guardian)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.delete("/Guardian/delete", response_model=PatientGuardianUpdate)
def delete_patient_guardian(guardian_id: int, db: Session = Depends(get_db)):
    db_guardian = crud_guardian.delete_guardian(db, guardian_id)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    db_patient_patient_guardian = crud_patient_patient_guardian.delete_patient_patient_guardian_by_guardianId(db, guardian_id)
    if not db_patient_patient_guardian:
        raise HTTPException(status_code=404, detail="No patient patient guardian relationship found")
    return db_guardian
