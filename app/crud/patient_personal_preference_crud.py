import logging
import math
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_model import Patient
from ..models.patient_personal_preference_list_model import (
    PatientPersonalPreferenceList,
)
from ..models.patient_personal_preference_model import PatientPersonalPreference
from ..schemas.patient_personal_preference import (
    PatientPersonalPreferenceCreate,
    PatientPersonalPreferenceUpdate,
)

logger = logging.getLogger(__name__)


def _validate_is_like_for_type(is_like: Optional[str], preference_type: str):
    """
    Enforce IsLike rules based on preference type:
      - LikesDislikes: IsLike must be 'Y' or 'N' (cannot be null or empty)
      - Habit / Hobby:  IsLike must be null
    """
    if preference_type == "LikesDislikes":
        if is_like not in ("Y", "N"):
            raise HTTPException(
                status_code=400,
                detail="IsLike must be 'Y' or 'N' for preference type 'LikesDislikes'",
            )
    else:
        if is_like is not None:
            raise HTTPException(
                status_code=400,
                detail=f"IsLike must be null for preference type '{preference_type}'. "
                       "It is only applicable for 'LikesDislikes'.",
            )


def _verify_patient_exists(db: Session, patient_id: int):
    """Raise 404 if the patient does not exist or is soft-deleted."""
    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.isDeleted == "0",
        )
        .first()
    )
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found",
        )


def _verify_preference_list_exists(db: Session, preference_list_id: int):
    """Raise 404 if the preference list item does not exist or is soft-deleted.
    Returns the preference list item so the caller can use it."""
    pref_list = (
        db.query(PatientPersonalPreferenceList)
        .filter(
            PatientPersonalPreferenceList.Id == preference_list_id,
            PatientPersonalPreferenceList.IsDeleted == "0",
        )
        .first()
    )
    if not pref_list:
        raise HTTPException(
            status_code=404,
            detail=f"Personal preference list item with ID {preference_list_id} not found",
        )
    return pref_list

def get_preferences(
    db: Session,
    pageNo: int = 0,
    pageSize: int = 10,
):
    """Return all active patient preferences (all patients) with pagination."""
    offset = pageNo * pageSize

    query = (
        db.query(PatientPersonalPreference)
        .options(joinedload(PatientPersonalPreference._preference_list))
        .filter(PatientPersonalPreference.IsDeleted == "0")
    )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0

    items = (
        query.order_by(PatientPersonalPreference.Id.asc())
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    return items, totalRecords, totalPages


def get_patient_preferences(
    db: Session,
    patient_id: int,
    pageNo: int = 0,
    pageSize: int = 100,
    preference_type: Optional[str] = None,
):
    """Return all active preferences for a specific patient.
    Optionally filter by PreferenceType (LikesDislikes | Habit | Hobby)."""
    offset = pageNo * pageSize

    query = (
        db.query(PatientPersonalPreference)
        .options(joinedload(PatientPersonalPreference._preference_list))
        .filter(
            PatientPersonalPreference.PatientID == patient_id,
            PatientPersonalPreference.IsDeleted == "0",
        )
    )

    if preference_type:
        query = query.join(
            PatientPersonalPreferenceList,
            PatientPersonalPreference.PersonalPreferenceListID
            == PatientPersonalPreferenceList.Id,
        ).filter(
            PatientPersonalPreferenceList.PreferenceType == preference_type
        )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0

    items = (
        query.order_by(PatientPersonalPreference.Id.asc())
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    return items, totalRecords, totalPages


def get_preference(db: Session, preference_id: int):
    """Return a single active patient preference by primary key."""
    return (
        db.query(PatientPersonalPreference)
        .options(joinedload(PatientPersonalPreference._preference_list))
        .filter(
            PatientPersonalPreference.Id == preference_id,
            PatientPersonalPreference.IsDeleted == "0",
        )
        .first()
    )

def create_preference(
    db: Session,
    preference_data: PatientPersonalPreferenceCreate,
    created_by: str,
    user_full_name: str,
):
    """Create a new patient personal preference entry."""

    # 1. Validate IsLike value before any DB calls
    if preference_data.IsLike is not None and preference_data.IsLike not in ("Y", "N"):
        raise HTTPException(
            status_code=400,
            detail="IsLike must be 'Y', 'N', or null",
        )

    # 2. Verify patient exists
    _verify_patient_exists(db, preference_data.PatientID)

    # 3. Verify preference list item exists and get its type
    pref_list = _verify_preference_list_exists(db, preference_data.PersonalPreferenceListID)

    # 4. Validate IsLike against the preference type
    _validate_is_like_for_type(preference_data.IsLike, pref_list.PreferenceType)

    # 5. Duplicate check (same patient + same list item, active records only)
    existing = (
        db.query(PatientPersonalPreference)
        .filter(
            PatientPersonalPreference.PatientID == preference_data.PatientID,
            PatientPersonalPreference.PersonalPreferenceListID == preference_data.PersonalPreferenceListID,
            PatientPersonalPreference.IsDeleted == "0",
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Patient already has this personal preference recorded",
        )

    # 6. DB write
    try:
        now = datetime.now()
        new_pref = PatientPersonalPreference(
            **preference_data.model_dump(),
            CreatedDate=now,
            ModifiedDate=now,
            CreatedByID=created_by,
            ModifiedByID=created_by,
            IsDeleted="0",
        )
        db.add(new_pref)
        db.flush()

        # Fetch patient name and preference name for logging
        patient = db.query(Patient).filter(Patient.id == preference_data.PatientID).first()
        patient_name = patient.name if patient else None
        preference_name = pref_list.PreferenceName if pref_list else None

        updated_data_dict = serialize_data(preference_data.model_dump())
        updated_data_dict['PatientName'] = patient_name
        updated_data_dict['PreferenceName'] = preference_name

        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message=f"Created personal preference: {preference_name or 'Unknown'} for {patient_name or 'Unknown'}",
            table="PatientPersonalPreference",
            entity_id=new_pref.Id,
            original_data=None,
            updated_data=updated_data_dict,
            patient_id = new_pref.PatientID,
            patient_full_name = patient_name,
            log_type = 'personal_preference',
            is_system_config = False,
        )

        db.commit()

        result = (
            db.query(PatientPersonalPreference)
            .options(joinedload(PatientPersonalPreference._preference_list))
            .filter(PatientPersonalPreference.Id == new_pref.Id)
            .first()
        )

        logger.info(
            f"Created personal preference {new_pref.Id} for patient {new_pref.PatientID}"
        )
        return result

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create personal preference: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create personal preference: {str(e)}"
        )


def update_preference(
    db: Session,
    preference_id: int,
    preference_data: PatientPersonalPreferenceUpdate,
    modified_by: str,
    user_full_name: str,
):
    """Update a patient personal preference entry. Returns None if not found."""

    # 1. Validate IsLike value before any DB calls
    update_data = preference_data.model_dump(exclude_unset=True)
    if "IsLike" in update_data and update_data["IsLike"] not in ("Y", "N", None):
        raise HTTPException(
            status_code=400,
            detail="IsLike must be 'Y', 'N', or null",
        )

    # 2. Fetch existing record
    db_pref = (
        db.query(PatientPersonalPreference)
        .filter(
            PatientPersonalPreference.Id == preference_id,
            PatientPersonalPreference.IsDeleted == "0",
        )
        .first()
    )
    if not db_pref:
        return None

    # 3. Resolve effective values after update
    new_patient_id = update_data.get("PatientID", db_pref.PatientID)
    new_list_id = update_data.get("PersonalPreferenceListID", db_pref.PersonalPreferenceListID)
    new_is_like = update_data.get("IsLike", db_pref.IsLike)

    # 4. Verify patient exists if PatientID is being changed
    if "PatientID" in update_data:
        _verify_patient_exists(db, new_patient_id)

    # 5. Verify preference list item exists if it is being changed, get its type
    if "PersonalPreferenceListID" in update_data:
        pref_list = _verify_preference_list_exists(db, new_list_id)
        effective_type = pref_list.PreferenceType
    else:
        current_list = (
            db.query(PatientPersonalPreferenceList)
            .filter(PatientPersonalPreferenceList.Id == db_pref.PersonalPreferenceListID)
            .first()
        )
        effective_type = current_list.PreferenceType if current_list else None

    # 6. Validate IsLike against the effective preference type
    if effective_type and ("IsLike" in update_data or "PersonalPreferenceListID" in update_data):
        _validate_is_like_for_type(new_is_like, effective_type)

    # 7. Duplicate check (exclude current record)
    duplicate = (
        db.query(PatientPersonalPreference)
        .filter(
            PatientPersonalPreference.PatientID == new_patient_id,
            PatientPersonalPreference.PersonalPreferenceListID == new_list_id,
            PatientPersonalPreference.IsDeleted == "0",
            PatientPersonalPreference.Id != preference_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another personal preference record with this preference already exists for this patient",
        )

    # 8. DB write
    try:
        original_data = {
            k: serialize_data(v)
            for k, v in db_pref.__dict__.items()
            if not k.startswith("_")
        }

        for key, value in update_data.items():
            setattr(db_pref, key, value)

        db_pref.ModifiedDate = datetime.now()
        db_pref.ModifiedByID = modified_by

        db.flush()

        # Fetch patient name and preference name for logging
        patient = db.query(Patient).filter(Patient.id == db_pref.PatientID).first()
        patient_name = patient.name if patient else None
        pref_list_for_name = db.query(PatientPersonalPreferenceList).filter(
            PatientPersonalPreferenceList.Id == db_pref.PersonalPreferenceListID
        ).first()
        preference_name = pref_list_for_name.PreferenceName if pref_list_for_name else None

        original_data['PatientName']= patient_name
        original_data['PreferenceName'] = preference_name

        updated_data_with_names = serialize_data(update_data)
        updated_data_with_names["PatientName"] = patient_name
        updated_data_with_names["PreferenceName"] = preference_name

        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Updated personal preference: {preference_name or 'Unknown'} for {patient_name or 'Unknown'}",
            table="PatientPersonalPreference",
            entity_id=db_pref.Id,
            original_data=original_data,
            updated_data=updated_data_with_names,
            patient_id = db_pref.PatientID,
            patient_full_name = patient_name,
            log_type = 'personal_preference',
            is_system_config = False,
        )

        db.commit()

        result = (
            db.query(PatientPersonalPreference)
            .options(joinedload(PatientPersonalPreference._preference_list))
            .filter(PatientPersonalPreference.Id == db_pref.Id)
            .first()
        )

        logger.info(
            f"Updated personal preference {db_pref.Id} for patient {db_pref.PatientID}"
        )
        return result

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update personal preference {preference_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update personal preference: {str(e)}"
        )


def delete_preference(
    db: Session,
    preference_id: int,
    modified_by: str,
    user_full_name: str,
):
    """Soft-delete a patient personal preference. Returns None if not found."""
    db_pref = (
        db.query(PatientPersonalPreference)
        .filter(
            PatientPersonalPreference.Id == preference_id,
            PatientPersonalPreference.IsDeleted == "0",
        )
        .first()
    )
    if not db_pref:
        return None

    try:
        original_data = {
            k: serialize_data(v)
            for k, v in db_pref.__dict__.items()
            if not k.startswith("_")
        }

        db_pref.IsDeleted = "1"
        db_pref.ModifiedDate = datetime.now()
        db_pref.ModifiedByID = modified_by

        db.flush()

        # Fetch patient name and preference name for logging
        patient = db.query(Patient).filter(Patient.id == db_pref.PatientID).first()
        patient_name = patient.name if patient else None
        pref_list_for_name = db.query(PatientPersonalPreferenceList).filter(
            PatientPersonalPreferenceList.Id == db_pref.PersonalPreferenceListID
        ).first()
        preference_name = pref_list_for_name.PreferenceName if pref_list_for_name else None

        original_data['PatientName'] = patient_name
        original_data['PreferenceName'] = preference_name

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Deleted personal preference: {preference_name or 'Unknown'} for {patient_name or 'Unknown'}",
            table="PatientPersonalPreference",
            entity_id=preference_id,
            original_data=original_data,
            updated_data={"IsDeleted": "1"},
            patient_id = db_pref.PatientID,
            patient_full_name = patient_name,
            log_type = 'personal_preference',
            is_system_config = False,
        )

        db.commit()

        result = (
            db.query(PatientPersonalPreference)
            .options(joinedload(PatientPersonalPreference._preference_list))
            .filter(PatientPersonalPreference.Id == db_pref.Id)
            .first()
        )

        logger.info(
            f"Deleted personal preference {db_pref.Id} for patient {db_pref.PatientID}"
        )
        return result

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete personal preference {preference_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete personal preference: {str(e)}"
        )