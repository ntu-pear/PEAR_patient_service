from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, field_validator


class PatientPersonalPreferenceBase(BaseModel):
    PatientID: int
    PersonalPreferenceListID: int
    IsLike: Optional[str] = None    # 'Y' = Like, 'N' = Dislike, None = not applicable (Habit/Hobby)
    PreferenceRemarks: Optional[str] = None

    @field_validator("IsLike")
    @classmethod
    def validate_is_like(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("Y", "N"):
            raise HTTPException(
                status_code=400,
                detail="IsLike must be 'Y', 'N', or null"
            )
        return v

    @field_validator("PreferenceRemarks")
    @classmethod
    def validate_remarks(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 500:
                raise HTTPException(
                    status_code=400,
                    detail="PreferenceRemarks must not exceed 500 characters"
                )
        return v


class PatientPersonalPreferenceCreate(PatientPersonalPreferenceBase):
    pass


class PatientPersonalPreferenceUpdate(BaseModel):
    PatientID: Optional[int] = None
    PersonalPreferenceListID: Optional[int] = None
    IsLike: Optional[str] = None
    PreferenceRemarks: Optional[str] = None

    @field_validator("IsLike")
    @classmethod
    def validate_is_like(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("Y", "N"):
            raise HTTPException(
                status_code=400,
                detail="IsLike must be 'Y', 'N', or null"
            )
        return v

    @field_validator("PreferenceRemarks")
    @classmethod
    def validate_remarks(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 500:
                raise HTTPException(
                    status_code=400,
                    detail="PreferenceRemarks must not exceed 500 characters"
                )
        return v


class PatientPersonalPreference(PatientPersonalPreferenceBase):
    Id: int
    IsDeleted: str
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedByID: str
    ModifiedByID: str

    model_config = {"from_attributes": True}


class PatientPersonalPreferenceWithDetails(PatientPersonalPreference):
    """Extended schema that includes denormalised list fields."""
    PreferenceType: Optional[str] = None
    PreferenceName: Optional[str] = None

    model_config = {"from_attributes": True}