from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class PatientMedicationBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    PrescriptionListId: int
    AdministerTime: str
    Dosage: str
    Instruction: str
    StartDate: datetime
    EndDate: Optional[datetime] = None
    PrescriptionRemarks: str

class PatientMedicationCreate(PatientMedicationBase):
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientMedicationUpdate(PatientMedicationBase):
    UpdatedDateTime: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientMedication(PatientMedicationBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
