from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientPhotoBase(BaseModel):
    """ Base Schema: Common fields for PatientPhoto models """
    PatientID: int
    PhotoDetails: Optional[str] = None
    AlbumCategoryListID: int

class PatientPhotoCreate(PatientPhotoBase):
    """ Schema for creating a new patient photo """
    pass

class PatientPhotoUpdate(BaseModel):
    """ Schema for updating patient photo (Only allow certain fields) """
    PhotoDetails: Optional[str] = None
    AlbumCategoryListID: Optional[int] = None

class PatientPhotoResponse(PatientPhotoBase):
    """ Schema for response after creation/retrieval of a photo """
    PatientPhotoID: int
    PhotoPath: str
    IsDeleted: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "user-123"})
    ModifiedById: str = Field(json_schema_extra={"example": "user-123"})

    class Config:
        model_config = {"from_attributes": True}