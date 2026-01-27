from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientDementiaStageListBase(BaseModel):
    DementiaStage: str = Field(..., description="Name of the dementia stage (e.g., Mild, Moderate, Severe)")

class PatientDementiaStageListCreate(PatientDementiaStageListBase):
    pass

class PatientDementiaStageListUpdate(BaseModel):
    DementiaStage: Optional[str] = Field(None, description="Updated dementia stage name")

class PatientDementiaStageList(PatientDementiaStageListBase):
    id: int = Field(..., description="Primary key ID of the record")
    IsDeleted: str = Field(..., description="Indicates if the record is deleted ('1' for yes, '0' for no)")
    CreatedDate: datetime = Field(..., description="Timestamp when the record was created")
    ModifiedDate: datetime = Field(..., description="Timestamp when the record was last modified")
    CreatedById: str = Field(..., json_schema_extra={"example": "1"})
    ModifiedById: str = Field(..., json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}