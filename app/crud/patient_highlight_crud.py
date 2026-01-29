import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.strategies.highlights.strategy_factory import HighlightStrategyFactory
from app.utils.highlight_date_utils import calculate_business_days_ago

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_highlight_model import PatientHighlight
from ..models.patient_highlight_type_model import PatientHighlightType
from ..schemas.patient_highlight import PatientHighlightCreate, PatientHighlightUpdate

logger = logging.getLogger(__name__)

def _add_source_remarks_and_additional_fields(db: Session, highlights):
    """
    Add source_remarks AND additional_fields to each highlight using its strategy.
    
    This populates:
    - source_remarks: Main remarks field (e.g., VitalRemarks, AllergyRemarks)
    - additional_fields: Type-specific fields (e.g., allergy_type, prescription_name)
    """
    if not highlights:
        return highlights
    
    factory = HighlightStrategyFactory()
    
    for highlight in highlights:
        try:
            # Get strategy for this highlight type
            strategy = factory.get_strategy(highlight.highlight_type_code)
            
            if strategy:
                # Get source remarks
                highlight.source_remarks = strategy.get_source_remarks(db, highlight.SourceRecordId)
                
                # Get additional fields
                highlight.additional_fields = strategy.get_additional_fields(db, highlight.SourceRecordId)
            else:
                highlight.source_remarks = None
                highlight.additional_fields = {}
                
        except Exception as e:
            logger.error(f"Error getting data for highlight {highlight.Id}: {e}")
            highlight.source_remarks = None
            highlight.additional_fields = {}
    
    return highlights


def get_all_highlights(db: Session):
    highlights = db.query(PatientHighlight).options(joinedload(PatientHighlight._highlight_type)).filter(PatientHighlight.IsDeleted == "0").order_by(PatientHighlight.PatientId, PatientHighlight.CreatedDate.desc()).all()
    return _add_source_remarks_and_additional_fields(db, highlights)

def get_highlights_by_patient(db: Session, patient_id: int):
    highlights = db.query(PatientHighlight).options(joinedload(PatientHighlight._highlight_type)).filter(PatientHighlight.PatientId == patient_id, PatientHighlight.IsDeleted == "0").order_by(PatientHighlight.CreatedDate.desc()).all()
    return _add_source_remarks_and_additional_fields(db, highlights)

def get_enabled_highlights(db: Session):
    highlights = (
        db.query(PatientHighlight)
        .join(PatientHighlightType, PatientHighlight.HighlightTypeId == PatientHighlightType.Id)
        .options(joinedload(PatientHighlight._highlight_type))
        .filter(
            PatientHighlight.IsDeleted == "0",           # Highlight not deleted
            PatientHighlightType.IsDeleted == "0",   # Type not deleted
            PatientHighlightType.IsEnabled == "1"     # Type is enabled
        )
        .order_by(PatientHighlight.PatientId, PatientHighlight.CreatedDate.desc())
        .all()
    )
    return _add_source_remarks_and_additional_fields(db, highlights)

def get_enabled_highlights_by_patient(db: Session, patient_id: int):
    highlights = (
        db.query(PatientHighlight)
        .join(PatientHighlightType, PatientHighlight.HighlightTypeId == PatientHighlightType.Id)
        .options(joinedload(PatientHighlight._highlight_type))
        .filter(
            PatientHighlight.PatientId == patient_id,  # Specific patient
            PatientHighlight.IsDeleted == "0",           # Highlight not deleted
            PatientHighlightType.IsDeleted == "0",   # Type not deleted
            PatientHighlightType.IsEnabled == "1"     # Type is enabled
        )
        .order_by(PatientHighlight.CreatedDate.desc())
        .all()
    )
    return _add_source_remarks_and_additional_fields(db, highlights)

def create_highlight(db: Session, highlight_data: PatientHighlightCreate, created_by: str, user_full_name:str):
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
        user_full_name= user_full_name,
        message= "Created Patient Highlight",
        table="PatientHighlight",
        entity_id=db_highlight.Id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_highlight

def update_highlight(db: Session, highlight_id: int, highlight_data: PatientHighlightUpdate, modified_by: str,  user_full_name:str):
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
        user_full_name= user_full_name,
        message= "Updated Patient Highlight",
        table="PatientHighlight",
        entity_id=highlight_id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )
    return db_highlight

def delete_highlight(db: Session, highlight_id: int, modified_by: str,  user_full_name:str):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.Id == highlight_id).first()

    if not db_highlight or db_highlight.IsDeleted == "1":
        raise HTTPException(status_code=404, detail="Highlight not found")

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_highlight.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    db_highlight.IsDeleted = 1
    db_highlight.ModifiedDate = datetime.now()
    db_highlight.ModifiedById = modified_by
    db.commit()

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name= user_full_name,
        message= "Deleted Patient Highlight",
        table="PatientHighlight",
        entity_id=highlight_id,
        original_data=original_data_dict,
        updated_data=None,
    )
    return db_highlight


def cleanup_old_highlights(db: Session):
    """
    HARD DELETE old highlights based on type-specific retention periods.
    Each highlight type can have different retention (business days).
    
    HARD DELETION: Permanently removes records from database (not soft delete).
    
    RETENTION LOGIC:
    - If retention is 3 business days:
      - Highlight created Monday → Deleted Thursday 12 AM (after Mon, Tue, Wed)
      - Highlight created Tuesday → Deleted Friday 12 AM (after Tue, Wed, Thu)
    
    - The cutoff date is set to END OF DAY (23:59:59) to ensure any highlight
      created DURING that day is included in the deletion.
    
    Example:
      Today: Thursday 12:00 AM
      Retention: 3 business days
      Cutoff: Monday 23:59:59 (Thursday - 3 business days = Monday 23:59:59)
      
      Highlight A (created Monday 9:00 AM):
        Monday 9:00 AM < Monday 23:59:59? YES -> DELETED
      
      Highlight B (created Tuesday 9:00 AM):
        Tuesday 9:00 AM < Monday 23:59:59? NO -> KEPT
    
    Returns:
        dict: Summary of cleanup operation
    """
    try:
        # Get all enabled highlight types
        highlight_types = db.query(PatientHighlightType).filter(
            PatientHighlightType.IsEnabled == "1",
            PatientHighlightType.IsDeleted == "0"
        ).all()
        
        total_deleted = 0
        details = []
        
        for highlight_type in highlight_types:
            # Get retention period for this type
            retention_days = 3
            
            # Calculate cutoff date (N business days ago)
            cutoff_date = calculate_business_days_ago(retention_days, country="SG")
            
            # Set to END of that day (23:59:59.999999)
            # This ensures any highlight created during that day is included
            cutoff_date = cutoff_date.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )
            
            # Find old highlights of this type
            # Note: We check both soft-deleted (IsDeleted='1') and active (IsDeleted='0')
            # because we want to permanently delete ALL old highlights
            old_highlights = db.query(PatientHighlight).filter(
                PatientHighlight.HighlightTypeId == highlight_type.Id,
                PatientHighlight.CreatedDate < cutoff_date
            ).all()
            
            deleted_count = len(old_highlights)
            deleted_ids = []
            
            # HARD DELETE each highlight (permanently remove from database)
            for highlight in old_highlights:
                deleted_ids.append(highlight.Id)
                db.delete(highlight)  # Hard Delete instead of setting IsDeleted=1
            
            if deleted_count > 0:
                details.append({
                    "type": highlight_type.TypeName,
                    "type_code": highlight_type.TypeCode,
                    "retention_days": retention_days,
                    "cutoff_date": cutoff_date.isoformat(),
                    "deleted_count": deleted_count,
                    "deleted_ids": deleted_ids
                })
            
            total_deleted += deleted_count
        
        db.commit()
        
        # Log the cleanup
        log_crud_action(
            action=ActionType.DELETE,
            user="system_cronjob",
            user_full_name="System CronJob",
            message=f"HARD DELETED {total_deleted} old highlights across {len(details)} types",
            table="PatientHighlight",
            entity_id=None,
            original_data={"details": details},
            updated_data=None,
        )
        
        return {
            "status": "success",
            "deletion_type": "Hard",
            "total_deleted": total_deleted,
            "types_processed": len(highlight_types),
            "details": details
        }
        
    except Exception as e:
        db.rollback()
        log_crud_action(
            action=ActionType.DELETE,
            user="system_cronjob",
            user_full_name="System CronJob",
            message=f"Failed to cleanup highlights: {str(e)}",
            table="PatientHighlight",
            entity_id=None,
            original_data={"error": str(e)},
            updated_data=None,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )