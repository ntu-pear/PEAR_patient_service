from datetime import datetime
from typing import List, Optional

import pytz
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .patient import Patient


class PatientGuardianBase(BaseModel):
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
    isDeleted: str = "0"
    guardianApplicationUserId:  Optional[str] = None


class PatientGuardianCreate(PatientGuardianBase):
    createdDate: datetime = Field(default_factory=datetime.now)
    modifiedDate: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    patientId: int
    relationshipName: str = "Husband"

class PatientGuardianUpdate(PatientGuardianBase):
    modifiedDate: datetime = Field(default_factory=datetime.now)
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    patientId: int
    relationshipName: str

class PatientGuardian(PatientGuardianBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    model_config = ConfigDict(from_attributes=True)
    
