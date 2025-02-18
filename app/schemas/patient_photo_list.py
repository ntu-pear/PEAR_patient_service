from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class PatientPhotoListBase(BaseModel):
    IsDeleted: Optional[int] = 0  # Default value is 0 (not deleted)
    Value: str  # Album category name (e.g., Family, Friends)

class PatientPhotoListCreate(PatientPhotoListBase):
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientPhotoListUpdate(BaseModel):
    IsDeleted: Optional[int]
    Value: Optional[str]
    ModifiedById: int
    UpdatedDateTime: datetime

class PatientPhotoList(PatientPhotoListBase):
    PatientPhotoListAlbumID: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    class Config:
        model_config = {"from_attributes": True}
