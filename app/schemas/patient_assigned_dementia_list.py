from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema (common fields)
class PatientAssignedDementiaListBase(BaseModel):
    Value: str
    IsDeleted: Optional[str] = "0"  # Defaults to "0" for active

# Schema for creating a new record
class PatientAssignedDementiaListCreate(PatientAssignedDementiaListBase):
    Value: str
    # isDeleted: Optional[str] = "0"  # Defaults to "0" for active

# Schema for updating a record
class PatientAssignedDementiaListUpdate(BaseModel):
    Value: Optional[str]
    IsDeleted: Optional[str]
    ModifiedDate: Optional[datetime] = None

# Schema for reading a record
class PatientAssignedDementiaListRead(PatientAssignedDementiaListBase):
    DementiaTypeListId: int  # Primary key
    CreatedDate: datetime
    ModifiedDate: datetime

    model_config = {"from_attributes": True}