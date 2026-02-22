from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# class HighlightTypeBase(BaseModel):
#     Value: str = Field(json_schema_extra={"example": "newPrescription"})
#     IsDeleted: str = Field(default="0", json_schema_extra={"example": "0"})

# class HighlightTypeCreate(HighlightTypeBase):
#     pass

# class HighlightTypeUpdate(HighlightTypeBase):
#     pass

# class HighlightType(HighlightTypeBase):
#     HighlightTypeID: int = Field(json_schema_extra={"example": 1})
#     CreatedDateTime: datetime = Field(default_factory=datetime.now)
#     UpdatedDateTime: datetime = Field(default_factory=datetime.now)
#     CreatedById: str = Field(json_schema_extra={"example": "1"})
#     ModifiedById: str = Field(json_schema_extra={"example": "1"})
#     model_config = {"from_attributes": True}

class HighlightTypeBase(BaseModel):
    """Base schema for Patient Highlight Type (NO PRIORITY)"""
    TypeName: str = Field(max_length=100, json_schema_extra={"example": "Vital Signs Alert"})
    TypeCode: str = Field(max_length=50, json_schema_extra={"example": "VITAL"})
    Description: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Alerts for abnormal vital signs"})
    IsEnabled: bool = Field(default=True, json_schema_extra={"example": True})

class HighlightTypeCreate(HighlightTypeBase):
    """Schema for creating a new highlight type"""
    pass


class HighlightTypeUpdate(BaseModel):
    """Schema for updating a highlight type (all fields optional, NO PRIORITY)"""
    TypeName: Optional[str] = Field(None, max_length=100, json_schema_extra={"example": "Updated Name"})
    TypeCode: Optional[str] = Field(None, max_length=50, json_schema_extra={"example": "VITAL"})
    Description: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Updated description"})
    IsEnabled: Optional[bool] = Field(None, json_schema_extra={"example": False})

class HighlightType(HighlightTypeBase):
    """Full schema for Patient Highlight Type responses (NO PRIORITY)"""
    Id: int = Field(json_schema_extra={"example": 1})
    CreatedDate: datetime = Field(json_schema_extra={"example": "2025-01-04T23:13:59.107"})
    ModifiedDate: datetime = Field(json_schema_extra={"example": "2025-01-04T23:13:59.107"})
    IsDeleted: bool = Field(json_schema_extra={"example": False})
    CreatedById: str = Field(json_schema_extra={"example": "user-123"})
    ModifiedById: str = Field(json_schema_extra={"example": "user-123"})

    model_config = {"from_attributes": True}


class HighlightTypeToggle(BaseModel):
    """Schema for toggling type enabled status"""
    IsEnabled: bool = Field(json_schema_extra={"example": True})
