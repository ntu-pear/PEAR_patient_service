from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional


class PatientMobilityBase(BaseModel):
    active: int
    patient_id: int
    mobilityListId: int
    status: Optional[str] = None


class PatientMobilityCreate(PatientMobilityBase):
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class PatientMobilityUpdate(PatientMobilityBase):
    modifiedDate: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class PatientMobility(PatientMobilityBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
