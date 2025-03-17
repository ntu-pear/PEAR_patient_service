from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientMobilityBase(BaseModel):
    PatientID: int
    MobilityListId: int
    MobilityRemarks: Optional[str]
    IsRecovered: Optional[bool] = False

class PatientMobilityCreate(PatientMobilityBase):
    pass

class PatientMobilityUpdate(BaseModel):
    MobilityRemarks: Optional[str]
    IsRecovered: Optional[bool]

class PatientMobilityResponse(BaseModel):
    MobilityID: int
    PatientID: int
    MobilityListId: int
    IsRecovered: bool
    IsDeleted: bool
    CreatedDateTime: datetime
    ModifiedDateTime: datetime
    CreatedById: str
    ModifiedById: str

    model_config = {"from_attributes": True}  # ✅ Enables ORM mode for SQLAlchemy models

