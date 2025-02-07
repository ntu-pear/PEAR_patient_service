from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PatientDoctorNoteBase(BaseModel):
    IsDeleted: str = '0'
    PatientId: int
    DoctorId: int
    DoctorRemarks: Optional[str] = None


class PatientDoctorNoteCreate(PatientDoctorNoteBase):
    CreatedById: str
    ModifiedById: str


class PatientDoctorNoteUpdate(PatientDoctorNoteBase):
    ModifiedById: int


class PatientDoctorNote(PatientDoctorNoteBase):
    id: int
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str
    ModifiedById: str


model_config = {"from_attributes": True}
