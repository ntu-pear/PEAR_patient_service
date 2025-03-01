from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from ..models.patient_model import Patient  # Ensure you import the Patient model correctly
from ..models.patient_social_history_model import PatientSocialHistory
from ..schemas.patient_social_history import PatientSocialHistoryCreate, PatientSocialHistoryUpdate
from ..models.patient_list_diet_model import PatientDietList
from ..models.patient_list_education_model import PatientEducationList
from ..models.patient_list_livewith_model import PatientLiveWithList
from ..models.patient_list_occupation_model import PatientOccupationList
from ..models.patient_list_pet_model import PatientPetList
from ..models.patient_list_religion_model import PatientReligionList

from ..schemas.patient_social_history import (
    PatientSocialHistoryCreate,
    PatientSocialHistoryUpdate,
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data


def get_all_social_histories(db: Session):
    """
    Retrieve all social history records joined with their list values.
    """
    results = (
        db.query(
            PatientSocialHistory.id,
            PatientSocialHistory.patientId,
            PatientSocialHistory.sexuallyActive,
            PatientSocialHistory.secondHandSmoker,
            PatientSocialHistory.alcoholUse,
            PatientSocialHistory.caffeineUse,
            PatientSocialHistory.tobaccoUse,
            PatientSocialHistory.drugUse,
            PatientSocialHistory.exercise,
            PatientSocialHistory.dietListId,
            PatientSocialHistory.educationListId,
            PatientSocialHistory.liveWithListId,
            PatientSocialHistory.occupationListId,
            PatientSocialHistory.petListId,
            PatientSocialHistory.religionListId,
            PatientSocialHistory.createdDate,
            PatientSocialHistory.modifiedDate,
            PatientSocialHistory.createdById,
            PatientSocialHistory.modifiedById,
            PatientDietList.Value.label("DietValue"),
            PatientDietList.IsDeleted.label("DietIsDeleted"),
            PatientEducationList.Value.label("EducationValue"),
            PatientEducationList.IsDeleted.label("EducationIsDeleted"),
            PatientLiveWithList.Value.label("LiveWithValue"),
            PatientLiveWithList.IsDeleted.label("LiveWithIsDeleted"),
            PatientOccupationList.Value.label("OccupationValue"),
            PatientOccupationList.IsDeleted.label("OccupationIsDeleted"),
            PatientPetList.Value.label("PetValue"),
            PatientPetList.IsDeleted.label("PetIsDeleted"),
            PatientReligionList.Value.label("ReligionValue"),
            PatientReligionList.IsDeleted.label("ReligionIsDeleted"),
        )
        .join(PatientDietList, PatientSocialHistory.dietListId == PatientDietList.Id)
        .join(PatientEducationList, PatientSocialHistory.educationListId == PatientEducationList.Id)
        .join(PatientLiveWithList, PatientSocialHistory.liveWithListId == PatientLiveWithList.Id)
        .join(PatientOccupationList, PatientSocialHistory.occupationListId == PatientOccupationList.Id)
        .join(PatientPetList, PatientSocialHistory.petListId == PatientPetList.Id)
        .join(PatientReligionList, PatientSocialHistory.religionListId == PatientReligionList.Id)
        .all()
    )

    social_histories = []
    for result in results:
        print(result)
        # Provide human-readable list values only if the list record is active.
        diet_value = result.DietValue if result.DietIsDeleted == "0" else "N/A"
        education_value = result.EducationValue if result.EducationIsDeleted == "0" else "N/A"
        livewith_value = result.LiveWithValue if result.LiveWithIsDeleted == "0" else "N/A"
        occupation_value = result.OccupationValue if result.OccupationIsDeleted == "0" else "N/A"
        pet_value = result.PetValue if result.PetIsDeleted == "0" else "N/A"
        religion_value = result.ReligionValue if result.ReligionIsDeleted == "0" else "N/A"

        social_histories.append({
            "id": result.id,
            "patientId": result.patientId,
            "sexuallyActive": result.sexuallyActive,
            "secondHandSmoker": result.secondHandSmoker,
            "alcoholUse": result.alcoholUse,
            "caffeineUse": result.caffeineUse,
            "tobaccoUse": result.tobaccoUse,
            "drugUse": result.drugUse,
            "exercise": result.exercise,
            "dietListId": result.dietListId,
            "dietValue": diet_value,
            "educationListId": result.educationListId,
            "educationValue": education_value,
            "liveWithListId": result.liveWithListId,
            "liveWithValue": livewith_value,
            "occupationListId": result.occupationListId,
            "occupationValue": occupation_value,
            "petListId": result.petListId,
            "petValue": pet_value,
            "religionListId": result.religionListId,
            "religionValue": religion_value,
            "createdDate": result.createdDate,
            "modifiedDate": result.modifiedDate,
            "createdById": result.createdById,
            "modifiedById": result.modifiedById,
        })

    return social_histories


def get_patient_social_history(db: Session, patient_id: int):
    """
    Retrieve the social history record for a specific patient.
    """
    record = (
        db.query(
            PatientSocialHistory.id,
            PatientSocialHistory.patientId,
            PatientSocialHistory.sexuallyActive,
            PatientSocialHistory.secondHandSmoker,
            PatientSocialHistory.alcoholUse,
            PatientSocialHistory.caffeineUse,
            PatientSocialHistory.tobaccoUse,
            PatientSocialHistory.drugUse,
            PatientSocialHistory.exercise,
            PatientSocialHistory.dietListId,
            PatientSocialHistory.educationListId,
            PatientSocialHistory.liveWithListId,
            PatientSocialHistory.occupationListId,
            PatientSocialHistory.petListId,
            PatientSocialHistory.religionListId,
            PatientSocialHistory.createdDate,
            PatientSocialHistory.modifiedDate,
            PatientSocialHistory.createdById,
            PatientSocialHistory.modifiedById,
            PatientDietList.Value.label("DietValue"),
            PatientDietList.IsDeleted.label("DietIsDeleted"),
            PatientEducationList.Value.label("EducationValue"),
            PatientEducationList.IsDeleted.label("EducationIsDeleted"),
            PatientLiveWithList.Value.label("LiveWithValue"),
            PatientLiveWithList.IsDeleted.label("LiveWithIsDeleted"),
            PatientOccupationList.Value.label("OccupationValue"),
            PatientOccupationList.IsDeleted.label("OccupationIsDeleted"),
            PatientPetList.Value.label("PetValue"),
            PatientPetList.IsDeleted.label("PetIsDeleted"),
            PatientReligionList.Value.label("ReligionValue"),
            PatientReligionList.IsDeleted.label("ReligionIsDeleted"),
        )
        .join(PatientDietList, PatientSocialHistory.dietListId == PatientDietList.Id)
        .join(PatientEducationList, PatientSocialHistory.educationListId == PatientEducationList.Id)
        .join(PatientLiveWithList, PatientSocialHistory.liveWithListId == PatientLiveWithList.Id)
        .join(PatientOccupationList, PatientSocialHistory.occupationListId == PatientOccupationList.Id)
        .join(PatientPetList, PatientSocialHistory.petListId == PatientPetList.Id)
        .join(PatientReligionList, PatientSocialHistory.religionListId == PatientReligionList.Id)
        .filter(PatientSocialHistory.patientId == patient_id, PatientSocialHistory.isDeleted == "0")
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Social history record not found for the patient")
    
    # Provide human-readable list values only if the list record is active.
    diet_value = record.DietValue if record.DietIsDeleted == "0" else "N/A"
    education_value = record.EducationValue if record.EducationIsDeleted == "0" else "N/A"
    livewith_value = record.LiveWithValue if record.LiveWithIsDeleted == "0" else "N/A"
    occupation_value = record.OccupationValue if record.OccupationIsDeleted == "0" else "N/A"
    pet_value = record.PetValue if record.PetIsDeleted == "0" else "N/A"
    religion_value = record.ReligionValue if record.ReligionIsDeleted == "0" else "N/A"

    return {
        "id": record.id,
        "patientId": record.patientId,
        "sexuallyActive": record.sexuallyActive,
        "secondHandSmoker": record.secondHandSmoker,
        "alcoholUse": record.alcoholUse,
        "caffeineUse": record.caffeineUse,
        "tobaccoUse": record.tobaccoUse,
        "drugUse": record.drugUse,
        "exercise": record.exercise,
        "dietListId": record.dietListId,
        "dietValue": diet_value,
        "educationListId": record.educationListId,
        "educationValue": education_value,
        "liveWithListId": record.liveWithListId,
        "liveWithValue": livewith_value,
        "occupationListId": record.occupationListId,
        "occupationValue": occupation_value,
        "petListId": record.petListId,
        "petValue": pet_value,
        "religionListId": record.religionListId,
        "religionValue": religion_value,
        "createdDate": record.createdDate,
        "modifiedDate": record.modifiedDate,
        "createdById": record.createdById,
        "modifiedById": record.modifiedById,
    }
    

def create_patient_social_history(db: Session, social_data: PatientSocialHistoryCreate, created_by: str, user_full_name: str):
    """
    Create a new patient social history record. Validates that all referenced list records are active.
    """
    if not social_data.patientId:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    # Validate referenced list records
    diet = db.query(PatientDietList).filter(PatientDietList.Id == social_data.dietListId, PatientDietList.IsDeleted == "0").first()
    if not diet:
        raise HTTPException(status_code=400, detail="Invalid or inactive Diet type")
    
    education = db.query(PatientEducationList).filter(PatientEducationList.Id == social_data.educationListId, PatientEducationList.IsDeleted == "0").first()
    if not education:
        raise HTTPException(status_code=400, detail="Invalid or inactive Education type")
    
    livewith = db.query(PatientLiveWithList).filter(PatientLiveWithList.Id == social_data.liveWithListId, PatientLiveWithList.IsDeleted == "0").first()
    if not livewith:
        raise HTTPException(status_code=400, detail="Invalid or inactive Living arrangement type")
    
    occupation = db.query(PatientOccupationList).filter(PatientOccupationList.Id == social_data.occupationListId, PatientOccupationList.IsDeleted == "0").first()
    if not occupation:
        raise HTTPException(status_code=400, detail="Invalid or inactive Occupation type")
    
    pet = db.query(PatientPetList).filter(PatientPetList.Id == social_data.petListId, PatientPetList.IsDeleted == "0").first()
    if not pet:
        raise HTTPException(status_code=400, detail="Invalid or inactive Pet type")
    
    religion = db.query(PatientReligionList).filter(PatientReligionList.Id == social_data.religionListId, PatientReligionList.IsDeleted == "0").first()
    if not religion:
        raise HTTPException(status_code=400, detail="Invalid or inactive Religion type")

    # Optional: Check if the patient already has a social history record if your business logic requires uniqueness.
    existing = db.query(PatientSocialHistory).filter(PatientSocialHistory.patientId == social_data.patientId, PatientSocialHistory.isDeleted == "0").first()
    if not existing:
        raise HTTPException(status_code=400, detail=f"Patient with id {PatientSocialHistory.patientId} does not exist.")

    new_record = PatientSocialHistory(
        patientId=social_data.patientId,
        sexuallyActive=social_data.sexuallyActive,
        secondHandSmoker=social_data.secondHandSmoker,
        alcoholUse=social_data.alcoholUse,
        caffeineUse=social_data.caffeineUse,
        tobaccoUse=social_data.tobaccoUse,
        drugUse=social_data.drugUse,
        exercise=social_data.exercise,
        dietListId=social_data.dietListId,
        educationListId=social_data.educationListId,
        liveWithListId=social_data.liveWithListId,
        occupationListId=social_data.occupationListId,
        petListId=social_data.petListId,
        religionListId=social_data.religionListId,
        isDeleted=social_data.isDeleted,
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        createdById=created_by,
        modifiedById=created_by,
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    updated_data_dict = serialize_data(new_record.model_dump())
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created Patient Social history",
        table="Patient Social history",
        entity_id=None,
        original_data=None,
        updated_data= updated_data_dict,
    )

    return new_record


def update_patient_social_history(db: Session, patient_id: int, social_data: PatientSocialHistoryUpdate, modified_by: str, user_full_name: str):
    """
    Update an existing patient social history record after validating list references.
    """
    record = (
        db.query(PatientSocialHistory)
        .filter(PatientSocialHistory.id == social_data.id, PatientSocialHistory.patientId == patient_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"Social history record id {social_data.id} for patient with id {patient_id} not found.")
    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in record.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"
    # Validate list records if updated
    diet = db.query(PatientDietList).filter(PatientDietList.Id == social_data.dietListId).first()
    if not diet or diet.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Diet type")
    
    education = db.query(PatientEducationList).filter(PatientEducationList.Id == social_data.educationListId).first()
    if not education or education.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Education type")
    
    livewith = db.query(PatientLiveWithList).filter(PatientLiveWithList.Id == social_data.liveWithListId).first()
    if not livewith or livewith.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Living arrangement type")
    
    occupation = db.query(PatientOccupationList).filter(PatientOccupationList.Id == social_data.occupationListId).first()
    if not occupation or occupation.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Occupation type")
    
    pet = db.query(PatientPetList).filter(PatientPetList.Id == social_data.petListId).first()
    if not pet or pet.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Pet type")
    
    religion = db.query(PatientReligionList).filter(PatientReligionList.Id == social_data.religionListId).first()
    if not religion or religion.IsDeleted != "0":
        raise HTTPException(status_code=400, detail="Invalid or inactive Religion type")

    # Update fields
    record.sexuallyActive = social_data.sexuallyActive
    record.secondHandSmoker = social_data.secondHandSmoker
    record.alcoholUse = social_data.alcoholUse
    record.caffeineUse = social_data.caffeineUse
    record.tobaccoUse = social_data.tobaccoUse
    record.drugUse = social_data.drugUse
    record.exercise = social_data.exercise
    record.dietListId = social_data.dietListId
    record.educationListId = social_data.educationListId
    record.liveWithListId = social_data.liveWithListId
    record.occupationListId = social_data.occupationListId
    record.petListId = social_data.petListId
    record.religionListId = social_data.religionListId
    record.isDeleted = social_data.isDeleted
    record.modifiedDate = datetime.now()
    record.modifiedById = modified_by

    db.commit()
    db.refresh(record)

    try:
        updated_data_dict = {
            k: serialize_data(v)
            for k, v in record.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        updated_data_dict = "{}"
    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Updated Patient Social History",
        table="Patient Social History",
        entity_id=record.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )

    return record


def delete_patient_social_history(db: Session, patient_id: int, modified_by: str, user_full_name: str):
    """
    Soft delete a social history record by setting isDeleted to "1".
    """
    record = db.query(PatientSocialHistory).filter(PatientSocialHistory.patientId == patient_id, PatientSocialHistory.isDeleted == "0").first()
    if not record:
        raise HTTPException(status_code=404, detail="Social history record not found")

    record.isDeleted = "1"
    record.modifiedDate = datetime.now()
    record.modifiedById = modified_by

    db.commit()
    db.refresh(record)

    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in record.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Deleted Patient Social History",
        table="Patient Social History",
        entity_id=record.id,
        original_data=original_data_dict,
        updated_data= None,
    )
    return record
