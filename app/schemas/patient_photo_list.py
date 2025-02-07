from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPhotoListBase(BaseModel):
    IsDeleted: Optional[int] = 0  # Default value is 0 (not deleted)
    Value: str  # Album category name (e.g., Family, Friends)

class PatientPhotoListCreate(PatientPhotoListBase):
    CreatedById: int
    ModifiedById: int

class PatientPhotoListUpdate(BaseModel):
    IsDeleted: Optional[int]
    Value: Optional[str]
    ModifiedById: int
    UpdatedDateTime: datetime

class PatientPhotoList(PatientPhotoListBase):
    PatientPhotoListAlbumID: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: int
    ModifiedById: int

    class Config:
        orm_mode = True
