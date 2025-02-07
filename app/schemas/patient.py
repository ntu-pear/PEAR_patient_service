from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import re

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
    createdById: int  # INT -> int
    modifiedById: int 

class PatientUpdate(PatientBase):
    modifiedDate: datetime
    modifiedById: int 

class Patient(PatientBase):
    id: int # INT -> int (primary key)
    createdDate: datetime  # DATETIME -> datetime
    modifiedDate: datetime  # DATETIME -> datetime
    createdById: int  # INT -> int
    modifiedById: int  # INT -> int
    model_config = {"from_attributes": True}
