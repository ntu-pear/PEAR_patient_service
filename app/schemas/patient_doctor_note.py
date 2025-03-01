from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientDoctorNoteBase(BaseModel):
    isDeleted: str = "0"
    patientId: int
    doctorId: str
    doctorRemarks: Optional[str] = None


class PatientDoctorNoteCreate(PatientDoctorNoteBase):
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class PatientDoctorNoteUpdate(PatientDoctorNoteBase):
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class PatientDoctorNote(PatientDoctorNoteBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
