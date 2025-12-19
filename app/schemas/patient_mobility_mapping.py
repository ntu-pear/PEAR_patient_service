from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class PatientMobilityBase(BaseModel):
    PatientID: int
    MobilityListId: int
    MobilityRemarks: Optional[str]
    IsRecovered: Optional[bool] = False

class PatientMobilityCreate(PatientMobilityBase):
    RecoveryDate: Optional[date] = None # Here we allow frontend to pass in a recovery date if IsRecovered is True

class PatientMobilityUpdate(BaseModel):
    MobilityRemarks: Optional[str] = None
    IsRecovered: Optional[bool] = None

class PatientMobilityResponse(BaseModel):
    MobilityID: int
    PatientID: int
    MobilityListId: int
    MobilityRemarks: str
    IsRecovered: bool
    RecoveryDate: Optional[date] = None
    IsDeleted: bool
    CreatedDateTime: datetime
    ModifiedDateTime: datetime
    CreatedById: str
    ModifiedById: str

    model_config = {"from_attributes": True}  # Enables ORM mode for SQLAlchemy models

