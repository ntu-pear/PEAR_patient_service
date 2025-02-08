from sqlalchemy.orm import Session
from ..models.patient_pet_list_model import PatientPetList
from ..schemas.patient_pet_list import PatientPetListCreate, PatientPetListUpdate


def get_all_pet_types(db: Session):
    return db.query(PatientPetList).filter(PatientPetList.IsDeleted == "0").all()


def get_pet_type_by_id(db: Session, pet_type_id: int):
    return (
        db.query(PatientPetList)
        .filter(PatientPetList.Id == pet_type_id,PatientPetList.IsDeleted == "0")
        .first()
    )

def create_pet_type(db: Session, pet_type: PatientPetListCreate):
    db_pet_type = PatientPetList(
        **pet_type.model_dump()
    )
    db.add(db_pet_type)
    db.commit()
    db.refresh(db_pet_type)
    return db_pet_type


def update_pet_type(
    db: Session, pet_type_id: int, pet_type: PatientPetListUpdate
):
    db_pet_type = (
        db.query(PatientPetList)
        .filter(PatientPetList.Id == pet_type_id)
        .first()
    )

    if db_pet_type:
        for key, value in pet_type.model_dump(exclude_unset=True).items():
            setattr(db_pet_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_pet_type.UpdatedDateTime = datetime.now()

        db.commit()
        db.refresh(db_pet_type)
        return db_pet_type
    return None


def delete_pet_type(db: Session, pet_type_id: int):
    db_pet_type = (
        db.query(PatientPetList)
        .filter(PatientPetList.Id == pet_type_id)
        .first()
    )

    if db_pet_type:
        # Soft delete by marking the record as inactive
        db_pet_type.IsDeleted = "1"
        db_pet_type.UpdatedDateTime = datetime.now()
        db.commit()
        return db_pet_type
    return None
