from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientMedicalHistoryBase(BaseModel):
    PatientID: int = Field(json_schema_extra={"example": 1})
    MedicalDiagnosisID: int = Field(json_schema_extra={"example": 1})
    DateOfDiagnosis: Optional[date] = Field(default=None, json_schema_extra={"example": "2024-01-15"})
    Remarks: Optional[str] = Field(default=None, json_schema_extra={"example": "Patient reported severe headaches due to dehydration"})
    SourceOfInformation: Optional[str] = Field(default=None, json_schema_extra={"example": "Patient"})
    IsDeleted: str = Field(default="0", json_schema_extra={"example": "0"})

class PatientMedicalHistoryCreate(PatientMedicalHistoryBase):
    CreatedByID: str = Field(json_schema_extra={"example": "1"})
    ModifiedByID: str = Field(json_schema_extra={"example": "1"})

class PatientMedicalHistoryUpdate(BaseModel):
    MedicalDiagnosisID: Optional[int] = Field(default=None, json_schema_extra={"example": 1})
    DateOfDiagnosis: Optional[date] = Field(default=None, json_schema_extra={"example": "2024-01-15"})
    Remarks: Optional[str] = Field(default=None, json_schema_extra={"example": "Updated remarks"})
    SourceOfInformation: Optional[str] = Field(default=None, json_schema_extra={"example": "Patient"})
    IsDeleted: Optional[str] = Field(default=None, json_schema_extra={"example": "0"})
    ModifiedByID: str = Field(json_schema_extra={"example": "1"})

class PatientMedicalHistory(PatientMedicalHistoryBase):
    Id: int = Field(json_schema_extra={"example": 1})
    CreatedDate: datetime = Field(default_factory=datetime.now)
    LastUpdatedDate: datetime = Field(default_factory=datetime.now)
    CreatedByID: str = Field(json_schema_extra={"example": "1"})
    ModifiedByID: str = Field(json_schema_extra={"example": "1"})
    
    model_config = {"from_attributes": True}