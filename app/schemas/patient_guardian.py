from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

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
    relationshipId: int
    status: Optional[str] = None
    guardianApplicationUserId: int

class PatientGuardianCreate(PatientGuardianBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientGuardianUpdate(PatientGuardianBase):
    modifiedDate: datetime
    modifiedById: int

class PatientGuardian(PatientGuardianBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        orm_mode: True
