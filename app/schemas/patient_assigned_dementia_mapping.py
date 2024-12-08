from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base schema containing shared attributes
class PatientAssignedDementiaBase(BaseModel):
    active: Optional[str] = Field('Y', description="Indicates if the record is active ('Y' for yes, 'N' for no).")
    patientId: int = Field(..., description="ID of the patient assigned to the dementia entry.")
    dementiaTypeListId: int = Field(..., description="ID of the dementia type list assigned to the patient.")

# Schema for creating a new record
class PatientAssignedDementiaCreate(PatientAssignedDementiaBase):
    createdDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was created.")
    modifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was last modified.")
    createdById: int = Field(..., description="ID of the user who created the record.")
    modifiedById: int = Field(..., description="ID of the user who last modified the record.")

# Schema for updating an existing record
class PatientAssignedDementiaUpdate(BaseModel):
    active: Optional[str] = Field(None, description="Indicates if the record is active ('Y' for yes, 'N' for no).")
    dementiaTypeListId: Optional[int] = Field(None, description="Updated dementia type list ID.")
    modifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was last modified.")
    modifiedById: int = Field(..., description="ID of the user who last modified the record.")

# Schema for reading a record
class PatientAssignedDementia(PatientAssignedDementiaBase):
    id: int = Field(..., description="Primary key ID of the record.")
    createdDate: datetime = Field(..., description="Timestamp when the record was created.")
    modifiedDate: datetime = Field(..., description="Timestamp when the record was last modified.")
    createdById: int = Field(..., description="ID of the user who created the record.")
    modifiedById: int = Field(..., description="ID of the user who last modified the record.")

class PatientAssignedDementiaCreateResp(BaseModel):
    id: int
    active: str
    patientId: int
    dementiaTypeListId: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
