from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientPrescriptionBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    PrescriptionListId: int
    Dosage: str
    FrequencyPerDay: int
    Instruction: str
    StartDate: datetime
    EndDate: Optional[datetime] = None
    IsAfterMeal: Optional[str] = Field(json_schema_extra={"example": "1"})
    PrescriptionRemarks: str
    Status: Optional[str] = None

class PatientPrescriptionCreate(PatientPrescriptionBase):
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientPrescriptionUpdate(PatientPrescriptionBase):
    UpdatedDateTime: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientPrescription(PatientPrescriptionBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
