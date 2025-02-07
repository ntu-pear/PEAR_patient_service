from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientSocialHistoryBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    SexuallyActive: Optional[str] = None
    SecondHandSmoker: Optional[str] = None
    AlcoholUse: Optional[str] = None
    CaffeineUse: Optional[str] = None
    TobaccoUse: Optional[str] = None
    DrugUse: Optional[str] = None
    Exercise: Optional[str] = None

class PatientSocialHistoryCreate(PatientSocialHistoryBase):
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str
    ModifiedById: str

class PatientSocialHistoryUpdate(PatientSocialHistoryBase):
    ModifiedDate: datetime
    ModifiedById: int

class PatientSocialHistory(PatientSocialHistoryBase):
    id: int
    CreatedDate: datetime
    modifiedDate: datetime
    CreatedById: str
    ModifiedById: str

    model_config = {"from_attributes": True}
