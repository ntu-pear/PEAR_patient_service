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
        user: str, table: str, 
        entity_id: Optional[int] = None, 
        original_data: Optional[dict] = None,
        updated_data: Optional[dict] = None 
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
        "updated_data": updated_data
    }

    # Remove any None values to avoid logging unnecessary keys
    log_data = {key: value for key, value in log_data.items() if value is not None}

    # Convert to JSON string for logging (structured data)
    log_message = json.dumps(log_data, default=str)

    logger.info(log_message)