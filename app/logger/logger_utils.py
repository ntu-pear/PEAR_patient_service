from datetime import datetime, date
from .config import logger
import json
from enum import Enum
from typing import Optional


class ActionType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


EXCLUDED_KEYS = {"CreatedById", "ModifiedById", "ModifiedDate", "CreatedDate", "IsDeleted", "isDeleted"}


def filter_data(data: dict) -> dict:
    """Removes unwanted keys from the given dictionary."""
    return {k: v for k, v in data.items() if k not in EXCLUDED_KEYS} if data else {}


def log_crud_action(
        action: ActionType,
        user: str,
        user_full_name: str,
        message: str,
        table: str,
        entity_id: Optional[int] = None,
        original_data: Optional[dict] = None,
        updated_data: Optional[dict] = None,
        patient_id: Optional[int] = None,
        patient_full_name: Optional[str] = None,
        log_type: Optional[str] = None,
        prescription_name: Optional[str] = None,
        allergy_name: Optional[str] = None,
        medicine_name: Optional[str] = None,
        problem_name: Optional[str] = None,
        preference_name: Optional[str] = None,
        reaction_name: Optional[str] = None,
        dementia_type_name: Optional[str] = None,
        dementia_stage_name: Optional[str] = None,
        guardian_name: Optional[str] = None,
        is_system_config: bool = False,
):
    """
    Log CRUD actions in format compatible with Elasticsearch log service

    Enriched fields for frontend display:
    - patient_id / patient_full_name: Patient associated with this record (if applicable)
    - log_type: category for filtering (allergy, prescription, medicine, etc.)
    - prescription_name/ allergy_name/ medicine_name/ problem_name/ preference_name: Human-readable names
    """
    if action == ActionType.CREATE:
        original_data = None
    elif action == ActionType.DELETE:
        updated_data = None

    # Create the message object that the log service expects
    log_message = {
        "entity_id": entity_id,
        "original_data": filter_data(original_data),
        "updated_data": filter_data(updated_data),
    }

    # Create extra fields for the conditional formatter
    extra = {
        "table": table,
        "user": user,
        "action": action.value,  # This maps to "method" in log service
        "user_full_name": user_full_name,
        "log_text": message,
        "prescription_name": prescription_name,
        "allergy_name": allergy_name,
        "medicine_name": medicine_name,
        "problem_name": problem_name,
        "preference_name": preference_name,
        "reaction_name": reaction_name,
        "dementia_type_name": dementia_type_name,
        "dementia_stage_name": dementia_stage_name,
        "guardian_name": guardian_name,
        "is_system_config": is_system_config,
    }

    # IMPORTANT: Pass the message object, not a JSON string
    # The conditional formatter will handle the JSON serialization
    logger.info(log_message, extra=extra)


def serialize_data(data):
    """Serialize datetime and other objects for JSON compatibility"""
    if isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data