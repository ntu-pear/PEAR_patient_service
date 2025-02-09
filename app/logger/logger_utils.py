from datetime import datetime
from .config import logger
import json
from enum import Enum
from typing import Optional

class ActionType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

def log_crud_action(
    action: ActionType,
    user: str,
    table: str,
    entity_id: Optional[int] = None,
    original_data: Optional[dict] = None,
    updated_data: Optional[dict] = None,
):

    if action == ActionType.CREATE:
        original_data = None
        entity_id = None  # Entity ID is not applicable for create
    elif action == ActionType.DELETE:
        updated_data = None
        
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action.value,
        "user": user,
        "table": table,
        "entity_id": entity_id,
        "original_data": original_data,
        "updated_data": updated_data,
    }

    log_data = {key: value for key, value in log_data.items() if value is not None}
    log_message = json.dumps(log_data)
    logger.info(log_message)

def serialize_data(data):
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data
