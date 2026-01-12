from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientMedicalDiagnosisListBase(BaseModel):
    DiagnosisName: str = Field(json_schema_extra={"example": "Cardiovascular"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})

class PatientMedicalDiagnosisListCreate(PatientMedicalDiagnosisListBase):
    CreatedByID: str = Field(json_schema_extra={"example": "1"})
    ModifiedByID: str = Field(json_schema_extra={"example": "1"})

class PatientMedicalDiagnosisListUpdate(PatientMedicalDiagnosisListBase):
    ModifiedByID: str = Field(json_schema_extra={"example": "1"})

class PatientMedicalDiagnosisList(PatientMedicalDiagnosisListBase):
    Id: int = Field(json_schema_extra={"example": 1})
    CreatedDate: datetime = Field(default_factory=datetime.now)
    ModifiedDate: datetime = Field(default_factory=datetime.now)
    CreatedByID: str = Field(json_schema_extra={"example": "1"})
    ModifiedByID: str = Field(json_schema_extra={"example": "1"})
    
    model_config = {"from_attributes": True}