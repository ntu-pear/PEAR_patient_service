# app/services/highlight_helper.py
# ULTRA-SIMPLIFIED - Direct helper functions for routers

from datetime import datetime

from sqlalchemy.orm import Session

from ..logger.logger_utils import logger
from ..models.patient_highlight_model import PatientHighlight
from ..models.patient_highlight_type_model import PatientHighlightType
from ..strategies.highlights.strategy_factory import HighlightStrategyFactory

# Initialize factory once
_factory = HighlightStrategyFactory()

def create_highlight_if_needed(
    db: Session,
    source_record,
    type_code: str,
    patient_id: int,
    source_table: str,
    source_record_id: int = None,
    created_by: str = "system"
) -> bool:
    """
    Ultra-simplified helper to create highlight for a single record.
    Call this directly from your routers after creating a record.
    
    Args:
        db: Database session
        source_record: The record to check (Vital, Allergy, Problem, etc.)
        type_code: Type code ("VITAL", "ALLERGY", "PROBLEM", "MEDICATION")
        patient_id: Patient ID
        source_table: Source table name ("VITAL", "ALLERGY", etc.)
        created_by: Who created this (default: "system")
    
    Returns:
        bool: True if highlight was created, False otherwise
    
    Example:
        # In vital_router.py
        db_vital = create_vital_crud(...)
        
        create_highlight_if_needed(
            db=db,
            source_record=db_vital,
            type_code="VITAL",
            patient_id=db_vital.PatientId,
            source_table="VITAL",
            created_by=user_id
        )
    """
    try:
        # Get the highlight type from database
        highlight_type = db.query(PatientHighlightType).filter(
            PatientHighlightType.TypeCode == type_code,
            PatientHighlightType.IsEnabled == True,
            PatientHighlightType.IsDeleted == False
        ).first()
        
        if not highlight_type:
            logger.info(f"Highlight type {type_code} is not enabled or doesn't exist")
            return False
        
        # Get the strategy
        if not _factory.has_strategy(type_code):
            logger.warning(f"No strategy found for type: {type_code}")
            return False
        
        strategy = _factory.get_strategy(type_code)
        
        # Check if should generate highlight
        if not strategy.should_generate_highlight(source_record):
            logger.debug(f"Record does not meet highlight criteria for {type_code}")
            return False
        
        # Generate highlight text
        highlight_text = strategy.generate_highlight_text(source_record)
        
        # Check if highlight already exists for this source record
        existing = db.query(PatientHighlight).filter(
            PatientHighlight.PatientId == patient_id,
            PatientHighlight.HighlightTypeId == highlight_type.Id,
            PatientHighlight.SourceTable == source_table,
            PatientHighlight.SourceRecordId == source_record_id,
            PatientHighlight.IsDeleted == "0"
        ).first()
        
        if existing:
            # Update if text changed
            if existing.HighlightText != highlight_text:
                existing.HighlightText = highlight_text
                existing.ModifiedDate = datetime.now()
                existing.ModifiedById = created_by
                db.commit()
                logger.info(f"Updated highlight for {type_code}: {highlight_text}")
                return True
            else:
                logger.debug(f"Highlight already exists with same text for {type_code}")
                return False
        
        # Create new highlight
        highlight = PatientHighlight(
            PatientId=patient_id,
            HighlightTypeId=highlight_type.Id,
            HighlightText=highlight_text,
            SourceTable=source_table,
            SourceRecordId=source_record_id,
            IsDeleted="0",
            CreatedById=created_by,
            ModifiedById=created_by
        )
        
        db.add(highlight)
        db.commit()
        
        logger.info(f"Created highlight for {type_code}: {highlight_text}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating highlight for {type_code}: {e}")
        db.rollback()
        return False


def get_patient_highlights(
    db: Session,
    patient_id: int,
    type_code: str = None,
    active_only: bool = True
):
    """
    Get highlights for a patient.
    
    Args:
        db: Database session
        patient_id: Patient ID
        type_code: Optional filter by type ("VITAL", "ALLERGY", etc.)
        active_only: Only return non-deleted highlights (default: True)
    
    Returns:
        List of PatientHighlight objects
    
    Example:
        # Get all active highlights
        highlights = get_patient_highlights(db, patient_id=123)
        
        # Get only vital highlights
        vital_highlights = get_patient_highlights(db, patient_id=123, type_code="VITAL")
    """
    query = db.query(PatientHighlight).filter(
        PatientHighlight.PatientId == patient_id
    )
    
    if active_only:
        query = query.filter(PatientHighlight.IsDeleted == "0")
    
    if type_code:
        # Get type ID
        highlight_type = db.query(PatientHighlightType).filter(
            PatientHighlightType.TypeCode == type_code
        ).first()
        
        if highlight_type:
            query = query.filter(PatientHighlight.HighlightTypeId == highlight_type.Id)
    
    return query.order_by(PatientHighlight.CreatedDate.desc()).all()