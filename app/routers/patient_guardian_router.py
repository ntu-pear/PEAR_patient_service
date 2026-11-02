import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..errors import ConflictError
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
    PatientPatientGuardianUnassign,
)
from ..services.user_service import deactivate_guardian_account

router = APIRouter()

MAX_PATIENTS_PER_GUARDIAN = 2
MAX_GUARDIANS_PER_PATIENT = 2
MIN_GUARDIANS_PER_PATIENT = 1


def _actor(request: Optional[Request]) -> dict:
    """Who is making the change, for the audit log. Auth stays optional on these routes,
    so without a token the entries fall back to the system user as before."""
    payload = extract_jwt_payload(request, require_auth=False) if request is not None else None
    user_id = get_user_id(payload)
    if not user_id:
        return {}
    return {"user_id": user_id, "user_full_name": get_full_name(payload) or "None"}

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
def create_patient_guardian(guardian: PatientGuardianCreate, db: Session = Depends(get_db), request: Request = None):
    actor = _actor(request)
    db_relationship_id = crud_relationship.get_relationshipId_by_relationshipName(db, guardian.relationshipName)
    if not db_relationship_id:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db_guardian =  crud_guardian.create_guardian(db, guardian, **actor)
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
    ),
    **actor,
    )
    return db_guardian


@router.post("/Guardian/assign", response_model=PatientPatientGuardian)
def assign_guardian_to_patient(assignment: PatientPatientGuardianAssign, db: Session = Depends(get_db), request: Request = None):
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
        raise ConflictError("Guardian is already assigned to this patient")

    active_patient_count = crud_patient_patient_guardian.count_active_patients_for_guardian(db, assignment.guardianId)
    if active_patient_count >= MAX_PATIENTS_PER_GUARDIAN:
        raise HTTPException(
            status_code=400,
            detail=f"Guardian already has the maximum of {MAX_PATIENTS_PER_GUARDIAN} patients assigned"
        )

    active_guardian_count = crud_patient_patient_guardian.count_active_guardians_for_patient(db, assignment.patientId)
    if active_guardian_count >= MAX_GUARDIANS_PER_PATIENT:
        raise HTTPException(
            status_code=400,
            detail=f"Patient already has the maximum of {MAX_GUARDIANS_PER_PATIENT} guardians assigned"
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
        ),
        **_actor(request),
    )


@router.delete("/Guardian/unassign", response_model=PatientPatientGuardianUnassign)
def unassign_guardian_from_patient(patient_id: int, guardian_id: int, db: Session = Depends(get_db), request: Request = None):
    """Unlink a guardian from a patient.

    Guardians are the patient's own relatives or friends, not a pool to reassign from, so
    once a guardian has no patients left their record is soft-deleted and their login
    account deactivated. The response flags this so the FE can tell the user.
    """
    db_link = crud_patient_patient_guardian.get_patient_patient_guardian_by_guardianId_and_patientId(
        db, guardian_id, patient_id
    )
    if not db_link:
        raise HTTPException(status_code=404, detail="No active guardian assignment found for this patient")

    active_guardian_count = crud_patient_patient_guardian.count_active_guardians_for_patient(db, patient_id)
    if active_guardian_count <= MIN_GUARDIANS_PER_PATIENT:
        raise HTTPException(
            status_code=400,
            detail=f"Patient must have at least {MIN_GUARDIANS_PER_PATIENT} guardian assigned"
        )

    actor = _actor(request)
    db_deleted_link = crud_patient_patient_guardian.delete_relationship(db, db_link.id, **actor)

    if crud_patient_patient_guardian.count_active_patients_for_guardian(db, guardian_id) == 0:
        db_guardian = crud_guardian.delete_guardian(db, guardian_id, **actor)
        if db_guardian:
            db_deleted_link.guardianSoftDeleted = True
            if db_guardian.guardianApplicationUserId:
                db_deleted_link.accountDeactivated = deactivate_guardian_account(
                    db_guardian.guardianApplicationUserId,
                    os.environ.get("INTERNAL_SERVICE_API_KEY"),
                )

    return db_deleted_link


@router.put("/Guardian/update", response_model=PatientGuardian)
def update_patient_guardian(guardian_id: int, guardian: PatientGuardianUpdate, db: Session = Depends(get_db), request: Request = None):
    db_guardian = crud_guardian.update_guardian(db, guardian_id, guardian, **_actor(request))
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    return db_guardian

@router.delete("/Guardian/delete", response_model=PatientGuardianUpdate)
def delete_patient_guardian(guardian_id: int, db: Session = Depends(get_db), request: Request = None):
    actor = _actor(request)
    linked_patient_ids = crud_patient_patient_guardian.get_active_patient_ids_for_guardian(db, guardian_id)
    for patient_id in linked_patient_ids:
        active_guardian_count = crud_patient_patient_guardian.count_active_guardians_for_patient(db, patient_id)
        if active_guardian_count <= MIN_GUARDIANS_PER_PATIENT:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete guardian: patient {patient_id} must have at least {MIN_GUARDIANS_PER_PATIENT} guardian assigned"
            )

    db_guardian = crud_guardian.delete_guardian(db, guardian_id, **actor)
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")
    db_patient_patient_guardian = crud_patient_patient_guardian.delete_patient_patient_guardian_by_guardianId(db, guardian_id, **actor)
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