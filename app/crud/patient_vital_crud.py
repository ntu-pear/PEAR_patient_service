import logging
import math
from datetime import datetime

from app.models.patient_highlight_model import PatientHighlight
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.services.highlight_helper import create_highlight_if_needed

from ..config import Config
from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_vital_model import PatientVital
from ..schemas.patient_vital import (
    PatientVitalCreate,
    PatientVitalDelete,
    PatientVitalUpdate,
)

config = Config().Vital

# Get the latest vital by patient ID
def get_latest_vital(db: Session, patient_id: int):
    """
    Returns the latest (most recently created) vital entry for the given PatientId,
    and does not filter IsDeleted. If you want to include only active (non-deleted)
    records, add a filter(PatientVital.IsDeleted == '0').
    """
    return (
        db.query(PatientVital)
        .filter(PatientVital.PatientId == patient_id)
        .order_by(PatientVital.CreatedDateTime.desc())
        .first()
    )

# Get a paginated list of vitals by patient ID (only non-deleted)
def get_vital_list(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 100):
    offset = pageNo * pageSize
    query = db.query(PatientVital).filter(
        PatientVital.PatientId == patient_id,
        PatientVital.IsDeleted == '0'
    )
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    vitals = (
        query.order_by(PatientVital.Id.desc())
             .offset(offset)
             .limit(pageSize)
             .all()
    )

    return vitals, totalRecords, totalPages
logger = logging.getLogger(__name__)
# Create a new vital record
def create_vital(
    db: Session,
    vital_data: PatientVitalCreate,
    created_by: str,
    user_full_name: str
):
    """
    Creates a new PatientVital record, sets CreatedDateTime, ModifiedDateTime, 
    CreatedById, and ModifiedById. Validates vital thresholds before saving.
    """
    try:
        # Validate thresholds before creation
        validate_vital_threshold(vital_data)

        # Prepare data for insertion
        data_to_create = vital_data.model_dump(
            exclude={"CreatedDateTime", "ModifiedDateTime", "CreatedById", "ModifiedById"}
        )

        new_vital = PatientVital(
            **data_to_create,
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=created_by,
            ModifiedById=created_by,
            # IsDeleted="0"  # Mark as active
        )

        updated_data_dict = serialize_data(vital_data.model_dump())
        db.add(new_vital)
        db.commit()
        db.refresh(new_vital)
        
        # Check if the new record needs to be inserted into Highlight table
        try:
            logger.info(f"Checking if highlight needed for vital: PatientId={new_vital.PatientId}, VitalId={new_vital.Id}")
            
            create_highlight_if_needed(
                db=db,
                source_record=new_vital,
                type_code="VITAL",
                patient_id=new_vital.PatientId,
                source_table="PATIENT_VITAL",
                source_record_id=new_vital.Id,
                created_by=created_by
            )
            
            logger.info(f"Highlight check completed for vital: VitalId={new_vital.Id}")
            
        except Exception as e:
            logger.error(f"Failed to create highlight for vital {new_vital.Id}: {str(e)}", exc_info=True)
    
        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message="Created vital record",
            table="PatientVital",
            entity_id=new_vital.Id,
            original_data=None,
            updated_data=updated_data_dict,
        )
        return new_vital

    except ValueError as e:
        # If validation fails
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Update an existing vital record
def update_vital(
    db: Session,
    vital_id: int,
    vital_data: PatientVitalUpdate,
    modified_by: str,
    user_full_name: str
):
    """
    Updates a PatientVital record by ID, sets ModifiedDateTime and ModifiedById, 
    and validates thresholds before saving. Returns the updated record.
    """
    try:
        validate_vital_threshold(vital_data)

        db_vital = (
            db.query(PatientVital)
            .filter(PatientVital.Id == vital_id, PatientVital.IsDeleted == '0')
            .first()
        )

        # If no record is found or is soft-deleted
        if not db_vital:
            raise HTTPException(status_code=404, detail=f"Vital record with ID {vital_id} not found or deleted.")

        # Log original data
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_vital.__dict__.items() if not k.startswith("_")
            }
        except Exception:
            original_data_dict = "{}"

        # Apply updates
        update_data = vital_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_vital, key, value)

        # Update metadata
        db_vital.ModifiedDateTime = datetime.now()
        db_vital.ModifiedById = modified_by

        db.commit()
        db.refresh(db_vital)
        
        
        # Check if the new record needs to be inserted into Highlight table
        try:
            logger.info(f"Checking if highlight needed for vital: PatientId={db_vital.PatientId}, VitalId={db_vital.Id}")
            
            create_highlight_if_needed(
                db=db,
                source_record=db_vital,
                type_code="VITAL",
                patient_id=db_vital.PatientId,
                source_table="PATIENT_VITAL",
                source_record_id=db_vital.Id,
                created_by=db_vital.CreatedById
            )
            
            logger.info(f"Highlight check completed for vital: VitalId={db_vital.Id}")
            
        except Exception as e:
            logger.error(f"Failed to create highlight for vital {db_vital.Id}: {str(e)}", exc_info=True)
        

        updated_data_dict = serialize_data(update_data)
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated vital record",
            table="PatientVital",
            entity_id=vital_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )

        return db_vital

    except ValueError as e:
        # If threshold validation fails
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Reraise HTTP exceptions to preserve them
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Soft delete a vital record (set IsDeleted to '1')
def delete_vital(
    db: Session,
    vital_id: int,
    modified_by: str,
    user_full_name: str
):
    """
    Marks a PatientVital record as deleted by setting IsDeleted='1', updates 
    ModifiedDateTime and ModifiedById, and logs the action.
    """
    db_vital = (
        db.query(PatientVital)
        .filter(PatientVital.Id == vital_id, PatientVital.IsDeleted == '0')
        .first()
    )
    if not db_vital:
        raise HTTPException(
            status_code=404,
            detail=f"Vital record with ID {vital_id} not found or already deleted."
        )

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_vital.__dict__.items() if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    db_vital.IsDeleted = "1"
    db_vital.ModifiedDateTime = datetime.now()
    db_vital.ModifiedById = modified_by

    db.commit()
    
    try:
        highlights = db.query(PatientHighlight).filter(
            PatientHighlight.SourceTable == "PATIENT_VITAL",
            PatientHighlight.SourceRecordId == vital_id,
            PatientHighlight.IsDeleted == 0
        ).all()
        
        for highlight in highlights:
            highlight.IsDeleted = 1
            highlight.ModifiedDate = datetime.now()
            highlight.ModifiedById = modified_by
        
        if highlights:
            logger.info(f"Deleted {len(highlights)} highlights for vital {vital_id}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to delete highlights for vital {vital_id}: {e}")
    
    db.refresh(db_vital)

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Soft deleted vital record",
        table="PatientVital",
        entity_id=vital_id,
        original_data=original_data_dict,
        updated_data=serialize_data(db_vital),
    )
    return db_vital

def validate_vital_threshold(vital: PatientVitalCreate):
    if (vital.Temperature < config.Temperature.MIN_VALUE) or (vital.Temperature > config.Temperature.MAX_VALUE):
        raise ValueError(f"Temperature must be between {config.Temperature.MIN_VALUE} and {config.Temperature.MAX_VALUE}")
    if (vital.SystolicBP < config.SystolicBP.MIN_VALUE) or (vital.SystolicBP > config.SystolicBP.MAX_VALUE):
        raise ValueError(f"Systolic blood pressure must be between {config.SystolicBP.MIN_VALUE} and {config.SystolicBP.MAX_VALUE}")
    if (vital.DiastolicBP < config.DiastolicBP.MIN_VALUE) or (vital.DiastolicBP > config.DiastolicBP.MAX_VALUE):
        raise ValueError(f"Diastolic blood pressure must be between {config.DiastolicBP.MIN_VALUE} and {config.DiastolicBP.MAX_VALUE}")
    if (vital.SpO2 < config.SpO2.MIN_VALUE) or (vital.SpO2 > config.SpO2.MAX_VALUE):
        raise ValueError(f"SpO2 must be between {config.SpO2.MIN_VALUE} and {config.SpO2.MAX_VALUE} breaths per minute")
    if (vital.BloodSugarLevel < config.BloodSugarLevel.MIN_VALUE) or (vital.BloodSugarLevel > config.BloodSugarLevel.MAX_VALUE):
        raise ValueError(f"Blood sugar level must be between {config.BloodSugarLevel.MIN_VALUE} and {config.BloodSugarLevel.MAX_VALUE}")
    if (vital.HeartRate < config.HeartRate.MIN_VALUE) or (vital.HeartRate > config.HeartRate.MAX_VALUE):
        raise ValueError(f"Heart rate must be between {config.HeartRate.MIN_VALUE} and {config.HeartRate.MAX_VALUE}")
    # if (vital.BloodSugarLevel < config.BslBeforeMeal.MIN_VALUE) or (vital.BloodSugarLevel > config.BslBeforeMeal.MAX_VALUE):
    #     raise ValueError(f"Blood sugar level before meal must be between {config.BslBeforeMeal.MIN_VALUE} and {config.BslBeforeMeal.MAX_VALUE}")
    # if (vital.BloodSugarLevel < config.BslAfterMeal.MIN_VALUE) or (vital.BloodSugarLevel > config.BslAfterMeal.MAX_VALUE):
    #     raise ValueError(f"Blood sugar level after meal must be between {config.BslAfterMeal.MIN_VALUE} and {config.BslAfterMeal.MAX_VALUE}")