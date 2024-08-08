from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPhotoBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    photoPath: Optional[str] = None
    albumCategoryListId: int

class PatientPhotoCreate(PatientPhotoBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientPhotoUpdate(PatientPhotoBase):
    modifiedDate: datetime
    modifiedById: int

class PatientPhoto(PatientPhotoBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        orm_mode: True
