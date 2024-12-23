from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientDoctorNoteBase(BaseModel):
    isDeleted: str = '0'
    patientId: int
    doctorId: int
    doctorRemarks: Optional[str] = None

class PatientDoctorNoteCreate(PatientDoctorNoteBase):
    createdById: int
    modifiedById: int

class PatientDoctorNoteUpdate(PatientDoctorNoteBase):
    modifiedById: int

class PatientDoctorNote(PatientDoctorNoteBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        from_attributes = True
