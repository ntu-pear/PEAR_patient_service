import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PatientBase(BaseModel):
    name: str  # VARCHAR (255) -> str
    nric: str  # VARCHAR (9) -> str
    address: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    tempAddress: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    homeNo: Optional[str] = None  # VARCHAR (32) -> Optional[str]
    handphoneNo: Optional[str] = None  # VARCHAR (32) -> Optional[str]
    gender: str = Field(..., pattern="^[MF]$", json_schema_extra={"example": "M"})  # Gender restricted to 'M' or 'F'
    dateOfBirth: datetime  # DATETIME -> datetime
    isApproved: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> Optional[str]
    preferredName: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    preferredLanguageId: int = Field(default="1", json_schema_extra={"example": "1"})  # INT -> Optional[int]
    updateBit: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    autoGame: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    startDate: datetime  # DATETIME -> datetime
    endDate: Optional[datetime] = None  # DATETIME -> Optional[datetime]
    isActive: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    isRespiteCare: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    privacyLevel: int  # INT -> int
    terminationReason: Optional[str] = None
    inActiveReason: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    inActiveDate: Optional[datetime] = None  # DATETIME -> Optional[datetime]
    profilePicture: Optional[str] = None
    isDeleted: Optional[int] = Field(default=0, json_schema_extra={"example": "0"})

MASK_CHAR = "*"


def mask_nric_value(nric: Optional[str]) -> Optional[str]:
    """Masked form shown to users: five '*' then the last four characters."""
    if not nric:
        return nric
    return (MASK_CHAR * 5) + nric[-4:]


def _reject_masked_nric(nric: str) -> str:
    # A masked NRIC (e.g. *****567D) must never be saved as the real value.
    if MASK_CHAR in nric:
        raise ValueError("NRIC looks masked; send the full NRIC")
    return nric


class PatientCreate(PatientBase):
    createdDate: datetime  # DATETIME -> datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    _no_masked_nric = field_validator("nric")(_reject_masked_nric)

class PatientUpdate(PatientBase):
    modifiedDate: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    _no_masked_nric = field_validator("nric")(_reject_masked_nric)


class Patient(PatientBase):
    id: int # INT -> int (primary key)
    createdDate: datetime  # DATETIME -> datetime
    modifiedDate: datetime  # DATETIME -> datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    preferred_language: Optional[str] = None
    model_config = {"from_attributes": True}


def to_patient_response(db_patient, mask: bool = True) -> Patient:
    """Build the API response for a patient row.

    The NRIC is masked on the response copy only. The ORM row is left alone,
    because it is still attached to the request's session and any later commit
    in that session would otherwise save the masked NRIC.
    """
    patient = Patient.model_validate(db_patient)
    if mask:
        patient = patient.model_copy(update={"nric": mask_nric_value(patient.nric)})
    return patient

class NewGuardianInline(BaseModel):
    """Fields for creating a brand-new guardian atomically with a new patient."""
    active: Optional[str] = 'Y'
    firstName: str
    lastName: str
    preferredName: Optional[str] = None
    gender: str = 'M'
    contactNo: str
    nric: str
    email: Optional[EmailStr] = None
    dateOfBirth: datetime
    address: str = "Testing Address"
    tempAddress: Optional[str] = None
    status: Optional[str] = None
    guardianApplicationUserId: Optional[str] = None


class PatientCreateWithAllocation(PatientCreate):
    guardianId: Optional[int] = None
    newGuardian: Optional[NewGuardianInline] = None
    guardianRelationshipName: Optional[str] = None
    doctorId: Optional[str] = None
    gameTherapistId: Optional[str] = None
    caregiverId: Optional[str] = None
    doctor2Id: Optional[str] = None
    supervisor2Id: Optional[str] = None
