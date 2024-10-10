from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientAllergyBase(BaseModel):
    active: Optional[str] = Field('1', example='1')
    patientId: int = Field(example=1)
    allergyRemarks: Optional[str] = Field(None, example='Not well')

class PatientAllergyCreate(PatientAllergyBase):
    createdDate: datetime = Field(example='2021-01-01T00:00:00')
    modifiedDate: datetime = Field(example='2021-01-01T00:00:00')
    createdById: int = Field(example=1)
    modifiedById: int = Field(example=1)

class PatientAllergyUpdate(PatientAllergyBase):
    modifiedDate: datetime = Field(example='2021-01-01T00:00:00')
    modifiedById: int = Field(example=1)

class PatientAllergy(PatientAllergyBase):
    id: int = Field(example=1)
    createdDate: datetime = Field(example='2021-01-01T00:00:00')
    modifiedDate: datetime = Field(example='2021-01-01T00:00:00')
    createdById: int = Field(example=1)
    modifiedById: int = Field(example=1)

    class Config:
        orm_mode = True
