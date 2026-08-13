from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud import patient_crud as crud_patient
from ..crud import patient_guardian_crud as crud_guardian
from ..crud import patient_guardian_relationship_mapping_crud as crud_relationship
from ..crud import patient_patient_guardian_crud as crud_patient_patient_guardian
from ..database import get_db
from ..schemas.patient_guardian import (  # TODO :note that this needs to be fixed
    PatientGuardian,
    PatientGuardianCreate,
    PatientGuardianUpdate,
)
from ..schemas.patient_patient_guardian import (
    PatientPatientGuardian,
    PatientPatientGuardianAssign,
    PatientPatientGuardianByGuardian,
    PatientPatientGuardianByPatient,
    PatientPatientGuardianCreate,
)

router = APIRouter()

MAX_PATIENTS_PER_GUARDIAN = 2

# NOTE: guardian lookup is by NRIC only (see GetPatientGuardianByNRIC below), not a
# bulk "list all guardians" endpoint - a guardian provides their own NRIC in person
# when signing up a new patient, so an exact-match lookup is both sufficient and the
# right amount of data exposure. A browsable/paginated list of every guardian's PII
# would be unnecessary exposure for this use case.

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
    db_guardian = crud_patient_patient_guardian.get_all_patient_patient_guardian_by_guardianNRIC(db,nric)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Error")
    return db_guardian

@router.get("/Guardian/GetPatientGuardianByPatientId", response_model=PatientPatientGuardianByPatient)
def get_patient_guardian_by_patient_id(patient_id: int, db: Session = Depends(get_db)):
    patient_patient_guardian = crud_patient_patient_guardian.get_all_patient_guardian_by_patientId(db, patient_id)
    return patient_patient_guardian

@router.post("/Guardian/add", response_model=PatientGuardian)
def create_patient_guardian(guardian: PatientGuardianCreate, db: Session = Depends(get_db)):
    db_relationship_id = crud_relationship.get_relationshipId_by_relationshipName(db, guardian.relationshipName)
    if not db_relationship_id:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db_guardian =  crud_guardian.create_guardian(db, guardian)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Error when creating patient guardian")
    db_patient = crud_patient.get_patient(db, guardian.patientId, mask=False)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
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
    return db_guardian


@router.post("/Guardian/assign", response_model=PatientPatientGuardian)
def assign_guardian_to_patient(assignment: PatientPatientGuardianAssign, db: Session = Depends(get_db)):
    """Link an existing guardian to a patient, without creating a new guardian record."""
    db_patient = crud_patient.get_patient(db, assignment.patientId, mask=False)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db_guardian = crud_guardian.get_guardian(db, assignment.guardianId)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")

    existing_link = crud_patient_patient_guardian.get_patient_patient_guardian_by_guardianId_and_patientId(
        db, assignment.guardianId, assignment.patientId
    )
    if existing_link:
        raise HTTPException(status_code=400, detail="Guardian is already assigned to this patient")

    active_patient_count = crud_patient_patient_guardian.count_active_patients_for_guardian(db, assignment.guardianId)
    if active_patient_count >= MAX_PATIENTS_PER_GUARDIAN:
        raise HTTPException(
            status_code=400,
            detail=f"Guardian already has the maximum of {MAX_PATIENTS_PER_GUARDIAN} patients assigned"
        )

    db_relationship_id = crud_relationship.get_relationshipId_by_relationshipName(db, assignment.relationshipName)
    if not db_relationship_id:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return crud_patient_patient_guardian.create_patient_patient_guardian(
        db,
        PatientPatientGuardianCreate(
            guardianId=assignment.guardianId,
            patientId=assignment.patientId,
            relationshipId=db_relationship_id.id,
            CreatedById=assignment.CreatedById,
            ModifiedById=assignment.ModifiedById,
            isDeleted="0",
        )
    )


@router.delete("/Guardian/unassign", response_model=PatientPatientGuardian)
def unassign_guardian_from_patient(patient_id: int, guardian_id: int, db: Session = Depends(get_db)):
    """Unlink a guardian from a patient, without deleting the guardian record itself."""
    db_link = crud_patient_patient_guardian.get_patient_patient_guardian_by_guardianId_and_patientId(
        db, guardian_id, patient_id
    )
    if not db_link:
        raise HTTPException(status_code=404, detail="No active guardian assignment found for this patient")

    return crud_patient_patient_guardian.delete_relationship(db, db_link.id)


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
    
    mapping = crud_relationship.get_relationship_mapping(db, db_patient_patient_guardian.relationshipId)
    relationshipName = mapping.relationshipName if mapping else "Unknown/Deleted"

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