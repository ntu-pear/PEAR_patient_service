from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class PatientBase(BaseModel):
    Name: str  # VARCHAR (255) -> str
    Nric: str  # VARCHAR (9) -> str
    Address: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    TempAddress: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    HomeNo: Optional[str] = None  # VARCHAR (32) -> Optional[str]
    HandphoneNo: Optional[str] = None  # VARCHAR (32) -> Optional[str]
    Gender: str = Field(..., pattern="^[MF]$", json_schema_extra={"example": "M"})  # Gender restricted to 'M' or 'F'
    DateOfBirth: datetime  # DATETIME -> datetime
    IsApproved: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> Optional[str]
    PreferredName: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    PreferredLanguageId: int = Field(default="1", json_schema_extra={"example": "1"})  # INT -> Optional[int]
    UpdateBit: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    AutoGame: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    StartDate: datetime  # DATETIME -> datetime
    EndDate: Optional[datetime] = None  # DATETIME -> Optional[datetime]
    IsActive: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    IsRespiteCare: str = Field(..., pattern="^[01]$", json_schema_extra={"example": "1"})  # VARCHAR (1) -> str
    PrivacyLevel: int  # INT -> int
    TerminationReason: Optional[str] = None
    InActiveReason: Optional[str] = None  # VARCHAR (255) -> Optional[str]
    InActiveDate: Optional[datetime] = None  # DATETIME -> Optional[datetime]
    ProfilePicture: Optional[str] = None
    IsDeleted: Optional[int] = Field(default=0, json_schema_extra={"example": "0"})

class PatientCreate(PatientBase):
    CreatedDate: datetime  # DATETIME -> datetime
    ModifiedDate: datetime
    CreatedById: str  
    ModifiedById: str 

class PatientUpdate(PatientBase):
    ModifiedDate: datetime
    ModifiedById: str 

class Patient(PatientBase):
    id: int # INT -> int (primary key)
    CreatedDate: datetime  # DATETIME -> datetime
    ModifiedDate: datetime  # DATETIME -> datetime
    CreatedById: str  # INT -> str
    ModifiedById: str  # INT -> str
    model_config = ConfigDict(from_attributes=True)
