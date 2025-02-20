from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientAllergyBase(BaseModel):
    AllergyRemarks: Optional[str] = Field(
        None, json_schema_extra={"example": "Patient has severe reactions"}
    )
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientAllergyCreate(PatientAllergyBase):
    PatientID: int = Field(json_schema_extra={"example": 1})
    AllergyTypeID: int = Field(json_schema_extra={"example": 3})
    AllergyReactionTypeID: int = Field(json_schema_extra={"example": 1})


class PatientAllergyCreateResp(PatientAllergyBase):
    PatientID: int = Field(json_schema_extra={"example": 1})
    AllergyTypeID: int = Field(json_schema_extra={"example": 3})
    AllergyReactionTypeID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class PatientAllergyUpdateReq(PatientAllergyBase):
    Patient_AllergyID: int = Field(json_schema_extra={"example": 1})
    AllergyTypeID: int = Field(json_schema_extra={"example": 3})
    AllergyReactionTypeID: int = Field(json_schema_extra={"example": 1})


class PatientAllergyUpdateResp(PatientAllergyBase):
    PatientID: int = Field(json_schema_extra={"example": 1})
    Patient_AllergyID: int = Field(json_schema_extra={"example": 1})
    AllergyTypeID: int = Field(json_schema_extra={"example": 3})
    AllergyReactionTypeID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})


class PatientAllergy(PatientAllergyBase):
    Patient_AllergyID: int = Field(json_schema_extra={"example": 1})
    PatientID: int = Field(json_schema_extra={"example": 1})
    AllergyTypeValue: str = Field(json_schema_extra={"example": "Corn"})
    AllergyReactionTypeValue: str = Field(json_schema_extra={"example": "Rashes"})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
