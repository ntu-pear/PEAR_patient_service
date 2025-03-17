from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientSocialHistoryBase(BaseModel):
    isDeleted: Optional[str] = '0'
    patientId: int
    sexuallyActive: int = Field(json_schema_extra={"example": 1})
    secondHandSmoker: int = Field(json_schema_extra={"example": 1})
    alcoholUse: int = Field(json_schema_extra={"example": 1})
    caffeineUse: int = Field(json_schema_extra={"example": 1})
    tobaccoUse: int = Field(json_schema_extra={"example": 1})
    drugUse: int = Field(json_schema_extra={"example": 1})
    exercise: int = Field(json_schema_extra={"example": 1})
    dietListId: int = Field(json_schema_extra={"example": 1})
    educationListId: int = Field(json_schema_extra={"example": 1})
    liveWithListId: int = Field(json_schema_extra={"example": 1})
    occupationListId: int = Field(json_schema_extra={"example": 1})
    petListId: int = Field(json_schema_extra={"example": 1})
    religionListId: int = Field(json_schema_extra={"example": 1})

class PatientSocialHistoryCreate(PatientSocialHistoryBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: str
    modifiedById: str

class PatientSocialHistoryUpdate(PatientSocialHistoryBase):
    id: int

class PatientSocialHistory(PatientSocialHistoryBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: str
    modifiedById: str

    model_config = {"from_attributes": True}

class PatientSocialHistoryDecode(PatientSocialHistoryBase):
    id: int
    dietValue: str
    educationValue: str
    liveWithValue: str
    occupationValue: str
    petValue: str
    religionValue: str
    createdDate: datetime
    modifiedDate: datetime
    createdById: str
    modifiedById: str