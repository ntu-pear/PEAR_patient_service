from pydantic import BaseModel,Field,field_validator
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

    @field_validator("AdministerTime")
    @classmethod
    def tidy_administer_time(cls, value: str) -> str:
        # "0930, 1300" -> "0930,1300", the scheduler and its SQL split on the bare comma
        return ",".join(t.strip() for t in value.split(",") if t.strip())

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
