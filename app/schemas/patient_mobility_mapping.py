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

class PatientMobilityResponse(PatientMobilityBase):
    MobilityID: int
    IsDeleted: int
    CreatedDateTime: datetime
    ModifiedDateTime: datetime
    CreatedById: int
    ModifiedById: int

    class ConfigDict:
        # Don't use orm_mode = True anymore. Deprecated.
        # orm_mode = True 
        model_config = {"from_attributes": True}
