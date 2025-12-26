from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator

# class PatientHighlightBase(BaseModel):
#     PatientId: int = Field(json_schema_extra={"example": 1})
#     Type: str = Field(json_schema_extra={"example": "Allergy"})
#     HighlightJSON: str = Field(..., json_schema_extra={"example": '{"id":1,"value":"Shellfish"}'})
#     StartDate: datetime = Field(..., json_schema_extra={"example": "2024-03-03T00:00:00"})
#     EndDate: datetime = Field(..., json_schema_extra={"example": "2024-03-06T00:00:00"})
#     IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


# class PatientHighlightCreate(PatientHighlightBase):
#     pass

# class PatientHighlightUpdate(PatientHighlightBase):
#     pass

# class PatientHighlight(PatientHighlightBase):
#     Id: int = Field(..., json_schema_extra={"example": 1})
#     CreatedDate: datetime = Field(..., json_schema_extra={"example": "2025-01-04T23:13:59.107"})
#     ModifiedDate: datetime = Field(..., json_schema_extra={"example": "2025-01-04T23:13:59.107"})
#     CreatedById: str = Field(json_schema_extra={"example": "1"})
#     ModifiedById: str = Field(json_schema_extra={"example": "1"})

#     model_config = {"from_attributes": True}

class PatientHighlightBase(BaseModel):
    """Base schema for Patient Highlight"""
    PatientId: int = Field(json_schema_extra={"example": 1})
    HighlightTypeId: int = Field(json_schema_extra={"example": 1})
    HighlightText: str = Field(
        max_length=500, 
        json_schema_extra={"example": "High BP: 180/110 mmHg"}
    )
    SourceTable: str = Field(max_length=50, json_schema_extra={"example": "PATIENT_VITAL"})
    SourceRecordId: int = Field(json_schema_extra={"example": 123})


class PatientHighlightCreate(PatientHighlightBase):
    """Schema for creating a new highlight (usually system-generated, not from users)"""
    pass


class PatientHighlightUpdate(BaseModel):
    """Schema for updating a highlight (only text can be updated)"""
    HighlightText: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Updated text"})


class PatientHighlight(PatientHighlightBase):
    """
    Full schema for Patient Highlight responses.
    Includes type information and source value.
    """
    Id: int = Field(json_schema_extra={"example": 1})
    CreatedDate: datetime = Field(json_schema_extra={"example": "2025-12-26T18:00:00"})
    ModifiedDate: datetime = Field(json_schema_extra={"example": "2025-12-26T18:00:00"})
    IsDeleted: Union[str, int] = Field(json_schema_extra={"example": "0"})  # ← Accept both!
    CreatedById: str = Field(json_schema_extra={"example": "user-123"})
    ModifiedById: str = Field(json_schema_extra={"example": "user-123"})
    
    # Type information (from @property in model via joinedload)
    highlight_type_name: Optional[str] = Field(
        None, 
        json_schema_extra={"example": "Vital Signs Alert"}
    )
    highlight_type_code: Optional[str] = Field(
        None, 
        json_schema_extra={"example": "VITAL"}
    )
    
    # Source value (from strategy via CRUD enrichment)
    source_value: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Patient feeling dizzy"}
    )
    
    # Convert int to string for IsDeleted - TODO: standardize this across the app - change all to int
    @field_validator('IsDeleted', mode='before')
    @classmethod
    def convert_is_deleted(cls, v):
        """Convert IsDeleted to string if it's an integer"""
        if isinstance(v, int):
            return str(v)
        return v

    model_config = {"from_attributes": True}