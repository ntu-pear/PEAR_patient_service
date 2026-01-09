import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.patient_highlight_model import PatientHighlight
from app.strategies.highlights.strategy_factory import HighlightStrategyFactory

logger = logging.getLogger(__name__)


def create_highlight_if_needed(
    db: Session,
    source_record,
    type_code: str,
    patient_id: int,
    source_table: str,
    source_record_id: int,
    created_by: str
):
    """
    Creates, updates, or deletes a highlight based on whether the source record qualifies.
    
    Logic:
    1. Check if record should generate highlight (via strategy)
    2. If YES and no highlight exists - Create new highlight
    3. If YES and highlight exists - Update existing highlight (including HighlightText)
    4. If NO and highlight exists - Delete highlight (set IsDeleted=1)
    5. If NO and no highlight exists - Do nothing
    
    Args:
        db: Database session
        source_record: The source record (with relationships loaded if needed)
        type_code: Highlight type code (e.g., "VITAL", "MEDICATION", "PRESCRIPTION")
        patient_id: Patient ID
        source_table: Source table name (e.g., "PATIENT_MEDICATION")
        source_record_id: Source record ID
        created_by: User who triggered the action
    """
    try:
        # Get strategy for this type
        factory = HighlightStrategyFactory()
        strategy = factory.get_strategy(type_code)
        
        if not strategy:
            logger.warning(f"No strategy found for type_code: {type_code}")
            return
        
        # Pass db session to strategy (Vital strategies need it for historical data)
        should_highlight = strategy.should_generate_highlight(source_record, db=db)
        logger.info(f"Strategy evaluation for {source_table}:{source_record_id} - should_highlight: {should_highlight}")
        
        # Check if highlight already exists
        existing_highlight = db.query(PatientHighlight).filter(
            PatientHighlight.SourceTable == source_table,
            PatientHighlight.SourceRecordId == source_record_id,
            PatientHighlight.IsDeleted == 0
        ).first()
        
        logger.info(f"Existing highlight check: {'Found' if existing_highlight else 'Not found'}")
        
        # Case 1: Should highlight AND no existing highlight -> CREATE
        if should_highlight and not existing_highlight:
            highlight_text = strategy.generate_highlight_text(source_record)
            logger.info(f"Generating NEW highlight text: '{highlight_text}'")
            
            # Get highlight type ID from database
            from app.models.patient_highlight_type_model import PatientHighlightType
            highlight_type = db.query(PatientHighlightType).filter(
                PatientHighlightType.TypeCode == type_code,
                PatientHighlightType.IsDeleted == False
            ).first()
            
            if not highlight_type:
                logger.error(f"Highlight type not found for code: {type_code}")
                return
            
            # Create new highlight
            new_highlight = PatientHighlight(
                PatientId=patient_id,
                HighlightTypeId=highlight_type.Id,
                HighlightText=highlight_text,
                SourceTable=source_table,
                SourceRecordId=source_record_id,
                CreatedDate=datetime.now(),
                ModifiedDate=datetime.now(),
                IsDeleted=0,
                CreatedById=created_by,
                ModifiedById=created_by
            )
            
            db.add(new_highlight)
            db.flush()
            db.commit()
            logger.info(f"Created highlight {new_highlight.Id} with text: '{highlight_text}'")
        
        # Case 2: Should highlight and existing highlight -> UPDATE
        elif should_highlight and existing_highlight:
            old_text = existing_highlight.HighlightText
            new_text = strategy.generate_highlight_text(source_record)
            
            logger.info(f"Updating highlight {existing_highlight.Id}:")
            logger.info(f"Old text: '{old_text}'")
            logger.info(f"New text: '{new_text}'")
            
            # Update the highlight
            existing_highlight.HighlightText = new_text
            existing_highlight.ModifiedDate = datetime.now()
            existing_highlight.ModifiedById = created_by
            
            db.flush()
            db.commit()
            
            # Verify the update
            db.refresh(existing_highlight)
            logger.info(f"Updated highlight {existing_highlight.Id} - Current text: '{existing_highlight.HighlightText}'")
        
        # Case 3: Should NOT highlight but existing highlight -> DELETE
        elif not should_highlight and existing_highlight:
            logger.info(f"Deleting highlight {existing_highlight.Id} (no longer qualifies)")
            
            existing_highlight.IsDeleted = 1
            existing_highlight.ModifiedDate = datetime.now()
            existing_highlight.ModifiedById = created_by
            
            db.flush()
            db.commit()
            logger.info(f"Deleted highlight {existing_highlight.Id} for {source_table}:{source_record_id}")
        
        # Case 4: Should NOT highlight and no existing highlight -> Do nothing
        else:
            logger.debug(f"No highlight action needed for {source_table}:{source_record_id}")
        
    except Exception as e:
        logger.error(f"Error in create_highlight_if_needed: {e}", exc_info=True)
        db.rollback()