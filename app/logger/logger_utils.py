from datetime import datetime
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
):
    """
    Log CRUD actions in format compatible with Elasticsearch log service
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
    extra = {"table": table, "user": user, "action": action.value, "user_full_name": user_full_name,
             "log_text": message}
    
    # IMPORTANT: Pass the message object, not a JSON string
    # The conditional formatter will handle the JSON serialization
    logger.info(log_message, extra=extra)

def serialize_data(data):
    """Serialize datetime and other objects for JSON compatibility"""
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data