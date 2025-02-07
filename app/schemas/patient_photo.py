from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPhotoBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    PhotoPath: Optional[str] = None
    AlbumCategoryListId: int

class PatientPhotoCreate(PatientPhotoBase):
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str
    ModifiedById: str

class PatientPhotoUpdate(PatientPhotoBase):
    ModifiedDate: datetime
    ModifiedById: int

class PatientPhoto(PatientPhotoBase):
    id: int
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: int
    ModifiedById: int

    model_config = {"from_attributes": True}
