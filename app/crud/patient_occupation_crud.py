from sqlalchemy.orm import Session
from ..models.patient_occupation_list_model import PatientOccupationList
from ..schemas.patient_occupation_list import PatientOccupationListCreate, PatientOccupationListUpdate


def get_all_occupation_types(db: Session):
    return db.query(PatientOccupationList).filter(PatientOccupationList.IsDeleted == "0").all()


def get_occupation_type_by_id(db: Session, occupation_type_id: int):
    return (
        db.query(PatientOccupationList)
        .filter(PatientOccupationList.Id == occupation_type_id,PatientOccupationList.IsDeleted == "0")
        .first()
    )

def create_occupation_type(db: Session, occupation_type: PatientOccupationListCreate, created_by: int):
    db_occupation_type = PatientOccupationList(
        **occupation_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    db.add(db_occupation_type)
    db.commit()
    db.refresh(db_occupation_type)
    return db_occupation_type


def update_occupation_type(
    db: Session, occupation_type_id: int, occupation_type: PatientOccupationListUpdate, modified_by: int
):
    db_occupation_type = (
        db.query(PatientOccupationList)
        .filter(PatientOccupationList.Id == occupation_type_id)
        .first()
    )

    if db_occupation_type:
        for key, value in occupation_type.model_dump(exclude_unset=True).items():
            setattr(db_occupation_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_occupation_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_occupation_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_occupation_type)
        return db_occupation_type
    return None


def delete_occupation_type(db: Session, occupation_type_id: int, modified_by: int):
    db_occupation_type = (
        db.query(PatientOccupationList)
        .filter(PatientOccupationList.Id == occupation_type_id)
        .first()
    )

    if db_occupation_type:
        # Soft delete by marking the record as inactive
        db_occupation_type.IsDeleted = "1"
        db_occupation_type.UpdatedDateTime = datetime.now()
        db_occupation_type.ModifiedById = modified_by
        db.commit()
        return db_occupation_type
    return None
