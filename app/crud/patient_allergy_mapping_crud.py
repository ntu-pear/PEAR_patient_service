
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.patient_allergy_mapping_model import PatientAllergyMapping
from ..schemas.patient_allergy_mapping import PatientAllergyCreate
from ..models.allergy_type_model import AllergyType
from ..models.allergy_reaction_type_model import AllergyReactionType


def get_all_allergies(db: Session):
    results = (
        db.query(
            PatientAllergyMapping.Patient_AllergyID,
            PatientAllergyMapping.PatientID,
            PatientAllergyMapping.AllergyRemarks,
            AllergyType.Value.label('AllergyTypeValue'),
            AllergyType.Active.label('AllergyTypeActive'),
            AllergyReactionType.Value.label('AllergyReactionTypeValue'),
            AllergyReactionType.Active.label('AllergyReactionTypeActive'),
            PatientAllergyMapping.CreatedDateTime,
            PatientAllergyMapping.UpdatedDateTime,
        )
        .join(AllergyType, PatientAllergyMapping.AllergyListID == AllergyType.AllergyTypeID)
        .join(AllergyReactionType, PatientAllergyMapping.AllergyReactionListID == AllergyReactionType.AllergyReactionTypeID)
        .all()
    )

    # Handle "Active" logic
    patient_allergies = []
    for result in results:
        allergy_type_value = result.AllergyTypeValue if result.AllergyTypeActive == "1" else "No allergy type"
        allergy_reaction_value = result.AllergyReactionTypeValue if result.AllergyReactionTypeActive == "1" else "No allergy reaction"
        
        patient_allergies.append({
            "Patient_AllergyID": result.Patient_AllergyID,
            "PatientID": result.PatientID,
            "AllergyRemarks": result.AllergyRemarks,
            "AllergyTypeValue": allergy_type_value,
            "AllergyReactionTypeValue": allergy_reaction_value,
            "CreatedDateTime": result.CreatedDateTime,
            "UpdatedDateTime": result.UpdatedDateTime,
        })

    return patient_allergies


def get_patient_allergies(db: Session, patient_id: int):
    results = (
        db.query(
            PatientAllergyMapping.Patient_AllergyID,
            PatientAllergyMapping.PatientID,
            PatientAllergyMapping.AllergyRemarks,
            AllergyType.Value.label('AllergyTypeValue'),
            AllergyType.Active.label('AllergyTypeActive'),
            AllergyReactionType.Value.label('AllergyReactionTypeValue'),
            AllergyReactionType.Active.label('AllergyReactionTypeActive'),  
            PatientAllergyMapping.CreatedDateTime,
            PatientAllergyMapping.UpdatedDateTime,
        )
        .join(AllergyType, PatientAllergyMapping.AllergyListID == AllergyType.AllergyTypeID)
        .join(AllergyReactionType, PatientAllergyMapping.AllergyReactionListID == AllergyReactionType.AllergyReactionTypeID)
        .filter(PatientAllergyMapping.PatientID == patient_id)
        .all()
    )

    # Handle "Active" logic
    patient_allergies = []
    for result in results:
        allergy_type_value = result.AllergyTypeValue if result.AllergyTypeActive == "1" else "No allergy type"
        allergy_reaction_value = result.AllergyReactionTypeValue if result.AllergyReactionTypeActive == "1" else "No allergy reaction"
        
        patient_allergies.append({
            "Patient_AllergyID": result.Patient_AllergyID,
            "PatientID": result.PatientID,
            "AllergyRemarks": result.AllergyRemarks,
            "AllergyTypeValue": allergy_type_value,
            "AllergyReactionTypeValue": allergy_reaction_value,
            "CreatedDateTime": result.CreatedDateTime,
            "UpdatedDateTime": result.UpdatedDateTime,
        })

    return patient_allergies

def create_patient_allergy(db: Session, allergy_data: PatientAllergyCreate):
    # Check if the AllergyTypeID exists in the AllergyType table
    allergy_type = db.query(AllergyType).filter(AllergyType.AllergyTypeID == allergy_data.AllergyTypeID).first()
    if not allergy_type or allergy_type.Active != "1":
        raise HTTPException(status_code=400, detail="Invalid or inactive Allergy Type")
    
    # Check if the AllergyReactionTypeID exists in the AllergyReactionType table
    allergy_reaction_type = db.query(AllergyReactionType).filter(AllergyReactionType.AllergyReactionTypeID == allergy_data.AllergyReactionTypeID, AllergyReactionType.Active == "1").first()
    if not allergy_reaction_type:
        raise HTTPException(status_code=400, detail="Invalid or inactive Allergy Reaction Type")

    # Check if the patient already has this combination of AllergyTypeID and AllergyReactionTypeID
    existing_allergy = db.query(PatientAllergyMapping).filter(
        PatientAllergyMapping.PatientID == allergy_data.PatientID,
        PatientAllergyMapping.AllergyListID == allergy_data.AllergyTypeID,
        PatientAllergyMapping.AllergyReactionListID == allergy_data.AllergyReactionTypeID,
    ).first()

    if existing_allergy:
        raise HTTPException(status_code=400, detail="Patient already has this allergy and reaction combination")
    
    # Create the patient allergy mapping
    db_allergy = PatientAllergyMapping(
        PatientID=allergy_data.PatientID,
        AllergyListID=allergy_data.AllergyTypeID,
        AllergyReactionListID=allergy_data.AllergyReactionTypeID,
        AllergyRemarks=allergy_data.AllergyRemarks,
        Active=allergy_data.Active
    )
    db.add(db_allergy)
    db.commit()
    db.refresh(db_allergy)
    return db_allergy
