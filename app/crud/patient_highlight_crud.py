from sqlalchemy.orm import Session
from ..models.patient_highlight_model import PatientHighlight
from ..schemas.patient_highlight import PatientHighlightCreate, PatientHighlightUpdate
from datetime import datetime
from fastapi import HTTPException
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_all_highlights(db: Session):
    return db.query(PatientHighlight).filter(PatientHighlight.IsDeleted == "0").all()

def get_highlights_by_patient(db: Session, patient_id: int):
    return (
        db.query(PatientHighlight)
        .filter(PatientHighlight.PatientId == patient_id, PatientHighlight.IsDeleted == "0")
        .all()
    )

def create_highlight(db: Session, highlight_data: PatientHighlightCreate, created_by: str):
    db_highlight = PatientHighlight(
        **highlight_data.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(highlight_data.model_dump())
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        table="PatientHighlight",
        entity_id=db_highlight.Id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_highlight

def update_highlight(db: Session, highlight_id: int, highlight_data: PatientHighlightUpdate, modified_by: str):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.Id == highlight_id).first()

    if not db_highlight or db_highlight.IsDeleted == "1":
        raise HTTPException(status_code=404, detail="Highlight not found")

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_highlight.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    for key, value in highlight_data.model_dump(exclude_unset=True).items():
        setattr(db_highlight, key, value)

    db_highlight.ModifiedDate = datetime.now()
    db_highlight.ModifiedById = modified_by
    db.commit()
    db.refresh(db_highlight)

    updated_data_dict = serialize_data(highlight_data.model_dump())
    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        table="PatientHighlight",
        entity_id=highlight_id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )
    return db_highlight

def delete_highlight(db: Session, highlight_id: int, modified_by: str):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.Id == highlight_id).first()

    if not db_highlight or db_highlight.IsDeleted == "1":
        raise HTTPException(status_code=404, detail="Highlight not found")

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_highlight.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    db_highlight.IsDeleted = "1"
    db_highlight.ModifiedDate = datetime.now()
    db_highlight.ModifiedById = modified_by
    db.commit()

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        table="PatientHighlight",
        entity_id=highlight_id,
        original_data=original_data_dict,
        updated_data=None,
    )
    return db_highlight
