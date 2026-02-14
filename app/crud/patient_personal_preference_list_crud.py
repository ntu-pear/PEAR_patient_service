import logging
import math
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_personal_preference_list_model import PatientPersonalPreferenceList
from ..schemas.patient_personal_preference_list import (
    PatientPersonalPreferenceListCreate,
    PatientPersonalPreferenceListUpdate,
)

logger = logging.getLogger(__name__)

VALID_PREFERENCE_TYPES = ("LikesDislikes", "Habit", "Hobby")

def get_preference_lists(
    db: Session,
    pageNo: int = 0,
    pageSize: int = 100,
    preference_type: Optional[str] = None,
):
    """Return all active preference list items with optional type filter and pagination."""
    query = db.query(PatientPersonalPreferenceList).filter(
        PatientPersonalPreferenceList.IsDeleted == "0"
    )

    if preference_type and preference_type.upper() != "ALL":
        if preference_type not in VALID_PREFERENCE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid preferenceType. Must be one of: ALL, {', '.join(VALID_PREFERENCE_TYPES)}",
            )
        query = query.filter(
            PatientPersonalPreferenceList.PreferenceType == preference_type
        )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    offset = pageNo * pageSize

    items = (
        query.order_by(
            PatientPersonalPreferenceList.PreferenceType.asc(),
            PatientPersonalPreferenceList.Id.asc(),
        )
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    return items, totalRecords, totalPages


def get_preference_list_by_id(db: Session, preference_list_id: int):
    """Return a single active preference list item by primary key."""
    return (
        db.query(PatientPersonalPreferenceList)
        .filter(
            PatientPersonalPreferenceList.Id == preference_list_id,
            PatientPersonalPreferenceList.IsDeleted == "0",
        )
        .first()
    )

def create_preference_list(
    db: Session,
    preference_list: PatientPersonalPreferenceListCreate,
    created_by: str,
    user_full_name: str,
):
    """Create a new preference list item. Raises 400 if (type, name) already exists."""

    # Validate preference type
    if preference_list.PreferenceType not in VALID_PREFERENCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"PreferenceType must be one of: {', '.join(VALID_PREFERENCE_TYPES)}",
        )

    # Duplicate check: same type + same name (case-insensitive) among active records
    existing = (
        db.query(PatientPersonalPreferenceList)
        .filter(
            PatientPersonalPreferenceList.PreferenceType == preference_list.PreferenceType,
            PatientPersonalPreferenceList.PreferenceName.ilike(preference_list.PreferenceName.strip()),
            PatientPersonalPreferenceList.IsDeleted == "0",
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"A preference list entry with type '{preference_list.PreferenceType}' "
                   f"and name '{preference_list.PreferenceName}' already exists",
        )

    try:
        now = datetime.now()
        db_item = PatientPersonalPreferenceList(
            **preference_list.model_dump(),
            CreatedDate=now,
            ModifiedDate=now,
            CreatedByID=created_by,
            ModifiedByID=created_by,
            IsDeleted="0",
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message="Created personal preference list record",
            table="PatientPersonalPreferenceList",
            entity_id=db_item.Id,
            original_data=None,
            updated_data=serialize_data(preference_list.model_dump()),
        )

        return db_item

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create preference list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_preference_list(
    db: Session,
    preference_list_id: int,
    preference_list: PatientPersonalPreferenceListUpdate,
    modified_by: str,
    user_full_name: str,
):
    """Update a preference list item. Returns None if not found."""
    db_item = (
        db.query(PatientPersonalPreferenceList)
        .filter(
            PatientPersonalPreferenceList.Id == preference_list_id,
            PatientPersonalPreferenceList.IsDeleted == "0",
        )
        .first()
    )
    if not db_item:
        return None

    update_data = preference_list.model_dump(exclude_unset=True)

    # Resolve effective values after update for validation + duplicate check
    new_type = update_data.get("PreferenceType", db_item.PreferenceType)
    new_name = update_data.get("PreferenceName", db_item.PreferenceName)

    # Validate preference type
    if new_type not in VALID_PREFERENCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"PreferenceType must be one of: {', '.join(VALID_PREFERENCE_TYPES)}",
        )

    # Duplicate check (exclude the current record)
    duplicate = (
        db.query(PatientPersonalPreferenceList)
        .filter(
            PatientPersonalPreferenceList.Id != preference_list_id,
            PatientPersonalPreferenceList.PreferenceType == new_type,
            PatientPersonalPreferenceList.PreferenceName.ilike(new_name.strip()),
            PatientPersonalPreferenceList.IsDeleted == "0",
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail=f"Another preference list entry with type '{new_type}' "
                   f"and name '{new_name}' already exists",
        )

    try:
        original_data = {
            k: serialize_data(v)
            for k, v in db_item.__dict__.items()
            if not k.startswith("_")
        }

        for key, value in update_data.items():
            setattr(db_item, key, value)

        db_item.ModifiedDate = datetime.now()
        db_item.ModifiedByID = modified_by

        db.commit()
        db.refresh(db_item)

        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated personal preference list record",
            table="PatientPersonalPreferenceList",
            entity_id=db_item.Id,
            original_data=original_data,
            updated_data=serialize_data(update_data),
        )

        return db_item

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update preference list {preference_list_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_preference_list(
    db: Session,
    preference_list_id: int,
    modified_by: str,
    user_full_name: str,
):
    """Soft-delete a preference list item. Returns None if not found."""
    db_item = (
        db.query(PatientPersonalPreferenceList)
        .filter(
            PatientPersonalPreferenceList.Id == preference_list_id,
            PatientPersonalPreferenceList.IsDeleted == "0",
        )
        .first()
    )
    if not db_item:
        return None

    try:
        original_data = {
            k: serialize_data(v)
            for k, v in db_item.__dict__.items()
            if not k.startswith("_")
        }

        db_item.IsDeleted = "1"
        db_item.ModifiedDate = datetime.now()
        db_item.ModifiedByID = modified_by

        db.commit()
        db.refresh(db_item)

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Soft deleted personal preference list record",
            table="PatientPersonalPreferenceList",
            entity_id=preference_list_id,
            original_data=original_data,
            updated_data={"IsDeleted": "1"},
        )

        return db_item

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete preference list {preference_list_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))