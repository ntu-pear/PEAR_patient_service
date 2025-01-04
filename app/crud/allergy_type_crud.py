from sqlalchemy.orm import Session
from ..models.allergy_type_model import AllergyType
from ..schemas.allergy_type import AllergyTypeCreate, AllergyTypeUpdate
from datetime import datetime


def get_all_allergy_types(db: Session):
    return db.query(AllergyType).all()


def get_allergy_type_by_id(db: Session, allergy_type_id: int):
    return (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_type_id)
        .first()
    )


def create_allergy_type(db: Session, allergy_type: AllergyTypeCreate, created_by: int):
    db_allergy_type = AllergyType(
        **allergy_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    db.add(db_allergy_type)
    db.commit()
    db.refresh(db_allergy_type)
    return db_allergy_type


def update_allergy_type(
    db: Session, allergy_type_id: int, allergy_type: AllergyTypeUpdate, modified_by: int
):
    db_allergy_type = (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_type_id)
        .first()
    )

    if db_allergy_type:
        for key, value in allergy_type.dict(exclude_unset=True).items():
            setattr(db_allergy_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_allergy_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_allergy_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_allergy_type)
        return db_allergy_type
    return None


def delete_allergy_type(db: Session, allergy_type_id: int, modified_by: int):
    db_allergy_type = (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_type_id)
        .first()
    )

    if db_allergy_type:
        # Soft delete by marking the record as inactive
        db_allergy_type.IsDeleted = "1"
        db_allergy_type.UpdatedDateTime = datetime.now()
        db_allergy_type.ModifiedById = modified_by
        db.commit()
        return db_allergy_type
    return None
