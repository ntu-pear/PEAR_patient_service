from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from ..models.patient_assigned_dementia_mapping_model import PatientAssignedDementiaMapping
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..schemas.patient_assigned_dementia_mapping import PatientAssignedDementiaCreate, PatientAssignedDementiaUpdate

# Get all dementia assignments for a patient
def get_assigned_dementias(db: Session, patient_id: int):
    results = (
        db.query(
            PatientAssignedDementiaMapping.id,
            PatientAssignedDementiaMapping.patientId,
            PatientAssignedDementiaMapping.active,
            PatientAssignedDementiaMapping.createdDate,
            PatientAssignedDementiaMapping.modifiedDate,
            PatientAssignedDementiaMapping.createdById,
            PatientAssignedDementiaMapping.modifiedById,
            PatientAssignedDementiaList.value.label("DementiaTypeValue"),
        )
        .join(PatientAssignedDementiaList, PatientAssignedDementiaMapping.dementiaTypeListId == PatientAssignedDementiaList.dementiaTypeListId)
        .filter(PatientAssignedDementiaMapping.patientId == patient_id, PatientAssignedDementiaMapping.active == "Y")
        .all()
    )

    dementia_assignments = []
    for result in results:
        dementia_assignments.append({
            "id": result.id,
            "patientId": result.patientId,
            "active": result.active,
            "createdDate": result.createdDate,
            "modifiedDate": result.modifiedDate,
            "createdById": result.createdById,
            "modifiedById": result.modifiedById,
            "DementiaTypeValue": result.DementiaTypeValue,
        })

    return dementia_assignments


# Create a new dementia assignment
def create_assigned_dementia(db: Session, dementia_data: PatientAssignedDementiaCreate, created_by: int):
    # Check if the dementia type exists and is not deleted
    dementia_type = db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.dementiaTypeListId == dementia_data.dementiaTypeListId,
        PatientAssignedDementiaList.isDeleted == "0",
    ).first()
    if not dementia_type:
        raise HTTPException(status_code=400, detail="Invalid or deleted dementia type")

    # Check if the patient already has this dementia type assigned
    existing_assignment = db.query(PatientAssignedDementiaMapping).filter(
        PatientAssignedDementiaMapping.patientId == dementia_data.patientId,
        PatientAssignedDementiaMapping.dementiaTypeListId == dementia_data.dementiaTypeListId,
        PatientAssignedDementiaMapping.active == "Y",
    ).first()

    if existing_assignment:
        raise HTTPException(status_code=400, detail="Patient already assigned this dementia type")

    # Create the new assignment
    new_assignment = PatientAssignedDementiaMapping(
        patientId=dementia_data.patientId,
        dementiaTypeListId=dementia_data.dementiaTypeListId,
        active="Y",
        createdDate=datetime.utcnow(),
        modifiedDate=datetime.utcnow(),
        createdById=created_by,
        modifiedById=created_by,
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


# Update a dementia assignment
def update_assigned_dementia(db: Session, dementia_id: int, dementia_data: PatientAssignedDementiaUpdate, modified_by: int):
    db_assignment = db.query(PatientAssignedDementiaMapping).filter(
        PatientAssignedDementiaMapping.id == dementia_id,
        PatientAssignedDementiaMapping.active == "Y",
    ).first()

    if not db_assignment:
        raise HTTPException(status_code=404, detail="Dementia assignment not found")

    # Update the assignment
    for key, value in dementia_data.dict(exclude_unset=True).items():
        setattr(db_assignment, key, value)

    # Update metadata
    db_assignment.modifiedDate = datetime.utcnow()
    db_assignment.modifiedById = modified_by

    db.commit()
    db.refresh(db_assignment)
    return db_assignment


# Soft delete a dementia assignment (set active to "N")
def delete_assigned_dementia(db: Session, dementia_id: int, modified_by: int):
    db_assignment = db.query(PatientAssignedDementiaMapping).filter(
        PatientAssignedDementiaMapping.id == dementia_id,
        PatientAssignedDementiaMapping.active == "Y",
    ).first()

    if not db_assignment:
        raise HTTPException(status_code=404, detail="Dementia assignment not found")

    # Soft delete the assignment
    db_assignment.active = "N"
    db_assignment.modifiedDate = datetime.utcnow()
    db_assignment.modifiedById = modified_by

    db.commit()
    db.refresh(db_assignment)
    return db_assignment
