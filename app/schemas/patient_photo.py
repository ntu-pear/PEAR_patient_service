from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPhotoBase(BaseModel):
    """ Base Schema: Common fields for PatientPhoto models """
    IsDeleted: Optional[int] = 0  # Default to 0 (active)
    PatientID: int
    PhotoPath: Optional[str] = None
    PhotoDetails: Optional[str] = None
    AlbumCategoryListID: int

class PatientPhotoCreate(PatientPhotoBase):
    """ Schema for creating a new patient photo (System fills other fields) """
    CreatedDateTime: datetime = datetime.utcnow()
    UpdatedDateTime: datetime = datetime.utcnow()
    CreatedById: int
    ModifiedById: int

class PatientPhotoUpdate(BaseModel):
    """ Schema for updating patient photo (Only allow certain fields) """
    PhotoDetails: Optional[str] = None
    IsDeleted: Optional[int] = None
    UpdatedDateTime: datetime = datetime.utcnow()
    ModifiedById: int

class PatientPhotoResponse(PatientPhotoBase):
    """ Schema for response after creation/retrieval of a photo """
    PatientPhotoID: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: int
    ModifiedById: int

    class Config:
        orm_mode = True  # Ensures compatibility with SQLAlchemy ORM
