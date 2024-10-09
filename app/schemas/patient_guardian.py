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
    createdDate: datetime = Field(default_factory=lambda: datetime.now(pytz.timezone('Asia/Singapore')))
    modifiedDate: datetime = Field(default_factory=lambda: datetime.now(pytz.timezone('Asia/Singapore')))
    createdById: int
    modifiedById: int
    patientId: int
    relationshipName: str

class PatientGuardianUpdate(PatientGuardianBase):
    modifiedDate: datetime
    modifiedById: int

class PatientGuardian(PatientGuardianBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int
    model_config = ConfigDict(from_attributes=True)
