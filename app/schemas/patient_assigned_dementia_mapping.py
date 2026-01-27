from pydantic import BaseModel, Field, ConfigDict

from datetime import datetime
from typing import Optional

class PatientAssignedDementiaBase(BaseModel):
    IsDeleted: Optional[str] = Field('0', description="Indicates if the record isDeleted ('1' for yes, '0' for no).")
    PatientId: int = Field(..., description="ID of the patient assigned to the dementia entry.")
    DementiaTypeListId: int = Field(..., description="ID of the dementia type list assigned to the patient.")
    DementiaStageId: int = Field(..., description="ID of the dementia stage (Mild, Moderate, Severe)")

class PatientAssignedDementiaCreate(PatientAssignedDementiaBase):
    CreatedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was created.")
    ModifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was last modified.")
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientAssignedDementiaUpdate(BaseModel):
    IsDeleted: Optional[str] = Field("0", description="Indicates if the record is isDeleted ('1' for yes, '0' for no).")
    DementiaTypeListId: Optional[int] = Field(None, description="Updated dementia type list ID.")
    DementiaStageId: int = Field(..., description="Updated dementia stage ID")
    ModifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was last modified.")
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientAssignedDementia(PatientAssignedDementiaBase):
    id: int = Field(..., description="Primary key ID of the record.")
    CreatedDate: datetime = Field(..., description="Timestamp when the record was created.")
    ModifiedDate: datetime = Field(..., description="Timestamp when the record was last modified.")
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    DementiaTypeValue: Optional[str]
    dementia_stage_value: str
    
class PatientAssignedDementiaCreateResp(BaseModel):
    id: int
    IsDeleted: str
    PatientId: int
    DementiaTypeListId: int
    DementiaStageId: int
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    

    model_config = {"from_attributes": True}  
