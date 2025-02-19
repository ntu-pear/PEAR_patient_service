from pydantic import BaseModel,Field
from datetime import datetime

class PatientMobility_MobilityListBase(BaseModel):
    patient_id: int
    mobilityListId: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientMobility_MobilityListCreate(PatientMobility_MobilityListBase):
    pass

class PatientMobility_MobilityListUpdate(PatientMobility_MobilityListBase):
    pass

class PatientMobility_MobilityList(PatientMobility_MobilityListBase):
    id: int

    model_config = {"from_attributes": True}
