from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, field_validator

VALID_PREFERENCE_TYPES = ("LikesDislikes", "Habit", "Hobby")


class PatientPersonalPreferenceListBase(BaseModel):
    PreferenceType: str
    PreferenceName: str

    @field_validator("PreferenceType")
    @classmethod
    def validate_preference_type(cls, v: str) -> str:
        if v not in VALID_PREFERENCE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"PreferenceType must be one of: {', '.join(VALID_PREFERENCE_TYPES)}"
            )
        return v

    @field_validator("PreferenceName")
    @classmethod
    def validate_preference_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise HTTPException(
                status_code=400,
                detail="PreferenceName must not be empty"
            )
        if len(v) > 255:
            raise HTTPException(
                status_code=400,
                detail="PreferenceName must not exceed 255 characters"
            )
        return v


class PatientPersonalPreferenceListCreate(PatientPersonalPreferenceListBase):
    pass


class PatientPersonalPreferenceListUpdate(BaseModel):
    PreferenceType: Optional[str] = None
    PreferenceName: Optional[str] = None

    @field_validator("PreferenceType")
    @classmethod
    def validate_preference_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PREFERENCE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"PreferenceType must be one of: {', '.join(VALID_PREFERENCE_TYPES)}"
            )
        return v

    @field_validator("PreferenceName")
    @classmethod
    def validate_preference_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise HTTPException(
                    status_code=400,
                    detail="PreferenceName must not be empty"
                )
            if len(v) > 255:
                raise HTTPException(
                    status_code=400,
                    detail="PreferenceName must not exceed 255 characters"
                )
        return v


class PatientPersonalPreferenceList(PatientPersonalPreferenceListBase):
    Id: int
    IsDeleted: str
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedByID: str
    ModifiedByID: str

    model_config = {"from_attributes": True}