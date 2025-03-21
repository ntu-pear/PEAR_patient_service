from pydantic import BaseModel, Field, ConfigDict

from datetime import datetime
from typing import Optional

# Base schema containing shared attributes
class PatientAssignedDementiaBase(BaseModel):
    IsDeleted: Optional[str] = Field('0', description="Indicates if the record isDeleted ('1' for yes, '0' for no).")
    PatientId: int = Field(..., description="ID of the patient assigned to the dementia entry.")
    DementiaTypeListId: int = Field(..., description="ID of the dementia type list assigned to the patient.")

# Schema for creating a new record
class PatientAssignedDementiaCreate(PatientAssignedDementiaBase):
    CreatedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was created.")
    ModifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was last modified.")
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

# Schema for updating an existing record
class PatientAssignedDementiaUpdate(BaseModel):
    IsDeleted: Optional[str] = Field("0", description="Indicates if the record is isDeleted ('1' for yes, '0' for no).")
    DementiaTypeListId: Optional[int] = Field(None, description="Updated dementia type list ID.")
    ModifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was last modified.")
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

# Schema for reading a record
class PatientAssignedDementia(PatientAssignedDementiaBase):
    id: int = Field(..., description="Primary key ID of the record.")
    CreatedDate: datetime = Field(..., description="Timestamp when the record was created.")
    ModifiedDate: datetime = Field(..., description="Timestamp when the record was last modified.")
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    DementiaTypeValue: Optional[str]
    
class PatientAssignedDementiaCreateResp(BaseModel):
    id: int
    IsDeleted: str
    PatientId: int
    DementiaTypeListId: int
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    

    model_config = {"from_attributes": True}  
