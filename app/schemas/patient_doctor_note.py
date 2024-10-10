from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientDoctorNoteBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    doctorId: int
    doctorRemarks: Optional[str] = None

class PatientDoctorNoteCreate(PatientDoctorNoteBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientDoctorNoteUpdate(PatientDoctorNoteBase):
    modifiedDate: datetime
    modifiedById: int

class PatientDoctorNote(PatientDoctorNoteBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        from_attributes = True
