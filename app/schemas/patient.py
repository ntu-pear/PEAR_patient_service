import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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

class PatientCreate(PatientBase):
    createdDate: datetime  # DATETIME -> datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientUpdate(PatientBase):
    modifiedDate: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class Patient(PatientBase):
    id: int # INT -> int (primary key)
    createdDate: datetime  # DATETIME -> datetime
    modifiedDate: datetime  # DATETIME -> datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    preferred_language: Optional[str] = None
    model_config = {"from_attributes": True}

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
