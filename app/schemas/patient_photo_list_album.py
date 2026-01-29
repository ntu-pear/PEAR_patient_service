from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientPhotoListAlbumBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Family Photos"})
    IsDeleted: Optional[int] = Field(default=0, json_schema_extra={"example": 0})


class PatientPhotoListAlbumCreate(PatientPhotoListAlbumBase):
    pass


class PatientPhotoListAlbumUpdate(BaseModel):
    Value: Optional[str] = None
    IsDeleted: Optional[int] = None


class PatientPhotoListAlbum(PatientPhotoListAlbumBase):
    AlbumCategoryListID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}