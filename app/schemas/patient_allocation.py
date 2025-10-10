from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import datetime

class PatientAllocationBase(BaseModel):
    active: str = Field("Y", pattern="^[YN]$", description="Active status: Y for active, N for inactive", json_schema_extra={"example": "Y"})
    patientId: int = Field(..., gt=0, description="ID of the patient being allocated")
    guardianId: int = Field(..., gt=0, description="ID of the primary guardian for the patient")
    tempDoctorId: Optional[int] = Field(None, gt=0, description="ID of the temporary doctor (if any)")
    tempCaregiverId: Optional[int] = Field(None, gt=0, description="ID of the temporary caregiver (if any)")
    guardian2Id: Optional[int] = Field(None, gt=0, description="ID of the secondary guardian (if any)")
    guardianUserId: Optional[str] = Field(None, description="Application user ID of the primary guardian")
    doctorId: str = Field(..., description="ID of the primary doctor assigned to the patient")
    gameTherapistId: str = Field(..., description="ID of the game therapist assigned to the patient")
    supervisorId: str = Field(..., description="ID of the supervisor overseeing the patient's care")
    caregiverId: str = Field(..., description="ID of the primary caregiver assigned to the patient")

class PatientAllocationCreate(PatientAllocationBase):
    createdDate: datetime = Field(default_factory=datetime.now)
    modifiedDate: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(..., json_schema_extra={"example": "1"})
    ModifiedById: str = Field(..., json_schema_extra={"example": "1"})

class PatientAllocationUpdate(PatientAllocationBase):
    modifiedDate: datetime = Field(default_factory=datetime.now)
    ModifiedById: str = Field(..., json_schema_extra={"example": "1"})

class PatientAllocation(PatientAllocationBase):
    id: int
    isDeleted: bool
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    model_config = {"from_attributes": True}