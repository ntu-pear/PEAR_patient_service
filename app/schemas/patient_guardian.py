from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from .patient import Patient
import pytz

class PatientGuardianBase(BaseModel):
    active: Optional[str] = 'Y'
    firstName: str
    lastName: str
    preferredName: Optional[str] = None
    gender: str
    contactNo: str
    nric: str
    email: EmailStr
    dateOfBirth: datetime
    address: str
    tempAddress: Optional[str] = None
    status: Optional[str] = None
    isDeleted: str
    guardianApplicationUserId:  Optional[str] = None


class PatientGuardianCreate(PatientGuardianBase):
    createdDate: datetime = Field(default_factory=datetime.now)
    modifiedDate: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    patientId: int
    relationshipName: str

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
    
