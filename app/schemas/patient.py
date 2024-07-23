from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientBase(BaseModel):
    firstName: str
    lastName: str
    nric: str
    address: Optional[str] = None
    tempAddress: Optional[str] = None
    officeNo: Optional[str] = None
    handphoneNo: Optional[str] = None
    gender: str
    dateOfBirth: datetime
    guardianId: Optional[int] = None
    isApproved: Optional[str] = None
    preferredName: Optional[str] = None
    preferredLanguageId: Optional[int] = None
    updateBit: Optional[int] = None
    autoGame: Optional[int] = None
    startDate: datetime
    endDate: Optional[datetime] = None
    patientStatus: str
    terminationReason: Optional[str] = None
    patientStatusinActiveReason: Optional[str] = None
    patientStatusInActiveDate: Optional[str] = None
    profilePicture: Optional[str] = None
    createdById: int
    modifiedById: int

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime

    class Config:
        orm_mode = True
