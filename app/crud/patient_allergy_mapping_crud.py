from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.patient_allergy_mapping_model import PatientAllergyMapping
from ..schemas.patient_allergy_mapping import (
    PatientAllergyCreate,
    PatientAllergyUpdateReq,
)
from ..models.allergy_type_model import AllergyType
from ..models.allergy_reaction_type_model import AllergyReactionType
from datetime import datetime


def get_all_allergies(db: Session):
    results = (
        db.query(
            PatientAllergyMapping.Patient_AllergyID,
            PatientAllergyMapping.PatientID,
            PatientAllergyMapping.AllergyRemarks,
            AllergyType.Value.label("AllergyTypeValue"),
            AllergyType.IsDeleted.label("AllergyTypeIsDeleted"),
            AllergyReactionType.Value.label("AllergyReactionTypeValue"),
            AllergyReactionType.IsDeleted.label("AllergyReactionTypeIsDeleted"),
            PatientAllergyMapping.CreatedDateTime,
            PatientAllergyMapping.UpdatedDateTime,
            PatientAllergyMapping.CreatedById,
            PatientAllergyMapping.ModifiedById,
        )
        .join(
            AllergyType,
            PatientAllergyMapping.AllergyTypeID == AllergyType.AllergyTypeID,
        )
        .join(
            AllergyReactionType,
            PatientAllergyMapping.AllergyReactionTypeID
            == AllergyReactionType.AllergyReactionTypeID,
        )
        .all()
    )

    # Handle "Active" logic
    patient_allergies = []
    for result in results:
        allergy_type_value = (
            result.AllergyTypeValue
            if result.AllergyTypeIsDeleted == "0"
            else "No allergy type"
        )
        allergy_reaction_value = (
            result.AllergyReactionTypeValue
            if result.AllergyReactionTypeIsDeleted == "0"
            else "No allergy reaction"
        )

        patient_allergies.append(
            {
                "Patient_AllergyID": result.Patient_AllergyID,
                "PatientID": result.PatientID,
                "AllergyRemarks": result.AllergyRemarks,
                "AllergyTypeValue": allergy_type_value,
                "AllergyReactionTypeValue": allergy_reaction_value,
                "CreatedDateTime": result.CreatedDateTime,
                "UpdatedDateTime": result.UpdatedDateTime,
                "CreatedById": result.CreatedById,
                "ModifiedById": result.ModifiedById,
            }
        )

    return patient_allergies


def get_patient_allergies(db: Session, patient_id: int):
    results = (
        db.query(
            PatientAllergyMapping.Patient_AllergyID,
            PatientAllergyMapping.PatientID,
            PatientAllergyMapping.AllergyRemarks,
            AllergyType.Value.label("AllergyTypeValue"),
            AllergyType.IsDeleted.label("AllergyTypeIsDeleted"),
            AllergyReactionType.Value.label("AllergyReactionTypeValue"),
            AllergyReactionType.IsDeleted.label("AllergyReactionTypeIsDeleted"),
            PatientAllergyMapping.CreatedDateTime,
            PatientAllergyMapping.UpdatedDateTime,
            PatientAllergyMapping.CreatedById,
            PatientAllergyMapping.ModifiedById,
        )
        .join(
            AllergyType,
            PatientAllergyMapping.AllergyTypeID == AllergyType.AllergyTypeID,
        )
        .join(
            AllergyReactionType,
            PatientAllergyMapping.AllergyReactionTypeID
            == AllergyReactionType.AllergyReactionTypeID,
        )
        .filter(PatientAllergyMapping.PatientID == patient_id)
        .all()
    )

    # Handle "Active" logic
    patient_allergies = []
    for result in results:
        allergy_type_value = (
            result.AllergyTypeValue
            if result.AllergyTypeIsDeleted == "0"
            else "No allergy type"
        )
        allergy_reaction_value = (
            result.AllergyReactionTypeValue
            if result.AllergyReactionTypeValue == "0"
            else "No allergy reaction"
        )

        patient_allergies.append(
            {
                "Patient_AllergyID": result.Patient_AllergyID,
                "PatientID": result.PatientID,
                "AllergyRemarks": result.AllergyRemarks,
                "AllergyTypeValue": allergy_type_value,
                "AllergyReactionTypeValue": allergy_reaction_value,
                "CreatedDateTime": result.CreatedDateTime,
                "UpdatedDateTime": result.UpdatedDateTime,
                "CreatedById": result.CreatedById,
                "ModifiedById": result.ModifiedById,
            }
        )

    return patient_allergies


def create_patient_allergy(
    db: Session, allergy_data: PatientAllergyCreate, created_by: int
):
    # Check if the AllergyTypeID exists in the AllergyType table
    allergy_type = (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_data.AllergyTypeID)
        .first()
    )
    if not allergy_type or allergy_type.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Allergy Type")

    # Check if the AllergyReactionTypeID exists in the AllergyReactionType table
    allergy_reaction_type = (
        db.query(AllergyReactionType)
        .filter(
            AllergyReactionType.AllergyReactionTypeID
            == allergy_data.AllergyReactionTypeID,
            AllergyReactionType.IsDeleted == "0",
        )
        .first()
    )
    if not allergy_reaction_type:
        raise HTTPException(
            status_code=400, detail="Invalid or inactive Allergy Reaction Type"
        )

    # Check if the patient already has this combination of AllergyTypeID and AllergyReactionTypeID
    existing_allergy = (
        db.query(PatientAllergyMapping)
        .filter(
            PatientAllergyMapping.PatientID == allergy_data.PatientID,
            PatientAllergyMapping.AllergyTypeID == allergy_data.AllergyTypeID,
            PatientAllergyMapping.AllergyReactionTypeID
            == allergy_data.AllergyReactionTypeID,
        )
        .first()
    )

    if existing_allergy:
        raise HTTPException(
            status_code=400,
            detail="Patient already has this allergy and reaction combination",
        )

    # Create the patient allergy mapping
    db_allergy = PatientAllergyMapping(
        PatientID=allergy_data.PatientID,
        AllergyTypeID=allergy_data.AllergyTypeID,
        AllergyReactionTypeID=allergy_data.AllergyReactionTypeID,
        AllergyRemarks=allergy_data.AllergyRemarks,
        IsDeleted=allergy_data.IsDeleted,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )

    db.add(db_allergy)
    db.commit()
    db.refresh(db_allergy)

    return db_allergy


def update_patient_allergy(
    db: Session,
    patient_id: int,
    allergy_data: PatientAllergyUpdateReq,
    modified_by: int,
):
    # Check if the record exists
    db_allergy = (
        db.query(PatientAllergyMapping)
        .filter(
            PatientAllergyMapping.Patient_AllergyID == allergy_data.Patient_AllergyID,
            PatientAllergyMapping.PatientID == patient_id,
        )
        .first()
    )

    if not db_allergy:
        raise HTTPException(status_code=404, detail="Patient allergy record not found")

    # Check if the AllergyTypeID exists and is active
    allergy_type = (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_data.AllergyTypeID)
        .first()
    )
    if not allergy_type or allergy_type.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Allergy Type")

    # Check if the AllergyReactionTypeID exists and is active
    allergy_reaction_type = (
        db.query(AllergyReactionType)
        .filter(
            AllergyReactionType.AllergyReactionTypeID
            == allergy_data.AllergyReactionTypeID,
            AllergyReactionType.IsDeleted == "0",
        )
        .first()
    )
    if not allergy_reaction_type:
        raise HTTPException(
            status_code=400, detail="Invalid or inactive Allergy Reaction Type"
        )

    # Update the allergy record
    db_allergy.AllergyTypeID = allergy_data.AllergyTypeID
    db_allergy.AllergyReactionTypeID = allergy_data.AllergyReactionTypeID
    db_allergy.AllergyRemarks = allergy_data.AllergyRemarks
    db_allergy.IsDeleted = allergy_data.IsDeleted
    db_allergy.UpdatedDateTime = datetime.now()
    db_allergy.ModifiedById = modified_by  # Set the user who modified it

    # Commit the changes to the database
    db.commit()
    db.refresh(db_allergy)

    return db_allergy


def delete_patient_allergy(db: Session, patient_allergy_id: int, modified_by: int):
    # Check if the record exists
    db_allergy = (
        db.query(PatientAllergyMapping)
        .filter(PatientAllergyMapping.Patient_AllergyID == patient_allergy_id)
        .first()
    )

    if not db_allergy:
        raise HTTPException(status_code=404, detail="Patient allergy record not found")

    # Soft delete the allergy by setting Active to "0"
    db_allergy.IsDeleted = "1"
    db_allergy.UpdatedDateTime = datetime.now()
    db_allergy.ModifiedById = modified_by

    # Commit the changes to the database
    db.commit()
    db.refresh(db_allergy)

    return db_allergy
