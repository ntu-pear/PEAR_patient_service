from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import re

class PatientBase(BaseModel):
    firstName: str                                      # VARCHAR (255) -> str
    lastName: str                                       # VARCHAR (255) -> str
    nric: str                                           # VARCHAR (9) -> str                               
    address: Optional[str] = None                       # VARCHAR (255) -> Optional[str]
    tempAddress: Optional[str] = None                   # VARCHAR (255) -> Optional[str]
    homeNo: Optional[str] = None                        # VARCHAR (32) -> Optional[str]
    handphoneNo: Optional[str] = None                   # VARCHAR (32) -> Optional[str]
    gender: str = Field(..., pattern="^[MF]$", example="M")  # Gender restricted to 'M' or 'F'
    dateOfBirth: datetime                               # DATETIME -> datetime
    guardianId: Optional[int] = None                    # INT -> Optional[int]
    isApproved: str = Field(..., pattern="^[01]$", example="1")  # VARCHAR (1) -> Optional[str]              
    preferredName: Optional[str] = None                 # VARCHAR (255) -> Optional[str]             
    preferredLanguageId: Optional[int] = None           # INT -> Optional[int] 
    updateBit: str = Field(..., pattern="^[01]$", example="1") # VARCHAR (1) -> str
    autoGame: str = Field(..., pattern="^[01]$", example="1")  # VARCHAR (1) -> str    
    startDate: datetime                                 # DATETIME -> datetime                   
    endDate: Optional[datetime] = None                  # DATETIME -> Optional[datetime]
    isActive: str = Field(..., pattern="^[01]$", example="1")                                       # VARCHAR (1) -> str
    isRespiteCare: str = Field(..., pattern="^[01]$", example="1")                                # VARCHAR (1) -> str
    privacyLevel: int                                   # INT -> int
    terminationReason: Optional[str] = None
    inActiveReason: Optional[str] = None                # VARCHAR (255) -> Optional[str]
    inActiveDate: Optional[datetime] = None             # DATETIME -> Optional[datetime]
    profilePicture: Optional[str] = None
    createdDate: datetime                               # DATETIME -> datetime
    modifiedDate: datetime                              # DATETIME -> datetime
    createdById: int                                    # INT -> int
    modifiedById: int                                   # INT -> int

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int # INT -> int (primary key)
    model_config = ConfigDict(from_attributes=True)
