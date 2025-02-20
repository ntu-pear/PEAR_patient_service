from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class PatientMobilityListBase(BaseModel):
    MobilityListId: int
    IsDeleted: int
    CreatedDateTime: datetime
    ModifiedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    Value: str

class PatientMobilityListCreate(PatientMobilityListBase):
    pass

class PatientMobilityListUpdate(PatientMobilityListBase):
    pass

class PatientMobilityList(PatientMobilityListBase):
    pass

    model_config = {"from_attributes": True}
