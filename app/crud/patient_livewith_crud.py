from sqlalchemy.orm import Session
from ..models.patient_livewith_list_model import PatientLiveWithList
from ..schemas.patient_livewith_list import PatientLiveWithListCreate, PatientLiveWithListUpdate


def get_all_livewith_types(db: Session):
    return db.query(PatientLiveWithList).filter(PatientLiveWithList.IsDeleted == "0").all()


def get_livewith_type_by_id(db: Session, livewith_type_id: int):
    return (
        db.query(PatientLiveWithList)
        .filter(PatientLiveWithList.Id == livewith_type_id,PatientLiveWithList.IsDeleted == "0")
        .first()
    )

def create_livewith_type(db: Session, livewith_type: PatientLiveWithListCreate, created_by: int):
    db_livewith_type = PatientLiveWithList(
        **livewith_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    db.add(db_livewith_type)
    db.commit()
    db.refresh(db_livewith_type)
    return db_livewith_type


def update_livewith_type(
    db: Session, livewith_type_id: int, livewith_type: PatientLiveWithListUpdate, modified_by: int
):
    db_livewith_type = (
        db.query(PatientLiveWithList)
        .filter(PatientLiveWithList.Id == livewith_type_id)
        .first()
    )

    if db_livewith_type:
        for key, value in livewith_type.model_dump(exclude_unset=True).items():
            setattr(db_livewith_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_livewith_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_livewith_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_livewith_type)
        return db_livewith_type
    return None


def delete_livewith_type(db: Session, livewith_type_id: int, modified_by: int):
    db_livewith_type = (
        db.query(PatientLiveWithList)
        .filter(PatientLiveWithList.Id == livewith_type_id)
        .first()
    )

    if db_livewith_type:
        # Soft delete by marking the record as inactive
        db_livewith_type.IsDeleted = "1"
        db_livewith_type.UpdatedDateTime = datetime.now()
        db_livewith_type.ModifiedById = modified_by
        db.commit()
        return db_livewith_type
    return None
