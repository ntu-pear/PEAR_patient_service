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
    PatientPatientGuardianByPatient,
    PatientPatientGuardianCreate
) 

from ..schemas.patient_guardian import (
    PatientGuardian,
    PatientGuardianCreate,
    PatientGuardianUpdate,
) #TODO :note that this needs to be fixed

router = APIRouter()

@router.get("/Guardian/GetPatientGuardianByGuardianId", response_model=PatientPatientGuardianByGuardian)
def get_patient_guardian_by_guardianId(guardian_userid: str, db: Session = Depends(get_db)):
    db_guardian = crud_patient_patient_guardian.get_all_patient_patient_guardian_by_guardianId(db,guardian_userid)
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
    print(PatientPatientGuardianCreate.model_fields)
    db_patient_patient_guardian = crud_patient_patient_guardian.create_patient_patient_guardian(
    db,
    PatientPatientGuardianCreate(
        guardianId = db_guardian.id,
        patientId = guardian.patientId,
        relationshipId = db_relationship_id.id,
        CreatedById= db_guardian.CreatedById,
        ModifiedById= db_guardian.ModifiedById,
        isDeleted=db_guardian.isDeleted
    )
)
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
    relationshipName = crud_relationship.get_relationship_mapping(db, db_patient_patient_guardian.relationshipId).relationshipName
    return PatientGuardianUpdate(
            id=db_guardian.id,
            active=db_guardian.active,
            firstName=db_guardian.firstName,
            lastName=db_guardian.lastName,
            preferredName= db_guardian.preferredName,
            gender=db_guardian.gender,
            contactNo=db_guardian.contactNo,
            nric=db_guardian.nric,
            email=db_guardian.email,
            dateOfBirth=db_guardian.dateOfBirth,
            address=db_guardian.address,
            tempAddress=db_guardian.tempAddress,
            status=db_guardian.status,
            isDeleted=db_guardian.isDeleted,
            guardianApplicationUserId=db_guardian.guardianApplicationUserId,
            modifiedDate=db_guardian.modifiedDate,
            ModifiedById=db_guardian.ModifiedById,
            patientId=db_patient_patient_guardian.patientId,
            relationshipName=relationshipName)
