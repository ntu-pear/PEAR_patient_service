from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List
from .patient import Patient
from .patient_guardian import PatientGuardian
from .patient_guardian_relationship_mapping import PatientGuardianRelationshipMapping
import pytz

class PatientPatientGuardianBase(BaseModel):
    isDeleted: str
    patientId: int
    guardianId: int
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientPatientGuardianCreate(PatientPatientGuardianBase):
    relationshipId: int
    createdDate: datetime = Field(default_factory=datetime.now)
    modifiedDate: datetime = Field(default_factory=datetime.now)
class PatientPatientGuardianUpdate(PatientPatientGuardianBase):
    relationshipId: int
    modifiedDate: datetime =Field(default_factory=datetime.now)

class PatientPatientGuardian(PatientPatientGuardianBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    patient_guardian: PatientGuardian
    relationship: PatientGuardianRelationshipMapping

class PatientWithRelationship(BaseModel):
    patient: Patient
    relationshipName: str
    model_config = ConfigDict(from_attributes=True)

class GuardianWithRelationship(BaseModel):
    patient_guardian: PatientGuardian
    relationshipName: str
    model_config = ConfigDict(from_attributes=True)

class PatientPatientGuardianByGuardian(BaseModel):
    patient_guardian: PatientGuardian
    patients: List[PatientWithRelationship]
    model_config = ConfigDict(from_attributes=True)

class PatientPatientGuardianByPatient(BaseModel):
    patient: Patient
    patient_guardians: List[GuardianWithRelationship]
    model_config = ConfigDict(from_attributes=True)
