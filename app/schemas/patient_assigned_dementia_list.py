from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema (common fields)
class PatientAssignedDementiaListBase(BaseModel):
    value: str
    isDeleted: Optional[str] = "0"  # Defaults to "0" for active

# Schema for creating a new record
class PatientAssignedDementiaListCreate(PatientAssignedDementiaListBase):
    pass

# Schema for updating a record
class PatientAssignedDementiaListUpdate(BaseModel):
    value: Optional[str]
    isDeleted: Optional[str]
    modifiedDate: Optional[datetime] = None

# Schema for reading a record
class PatientAssignedDementiaListRead(PatientAssignedDementiaListBase):
    dementiaTypeListId: int  # Primary key
    createdDate: datetime
    modifiedDate: datetime

    class Config:
        orm_mode = True
