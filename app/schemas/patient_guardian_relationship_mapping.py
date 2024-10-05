from pydantic import BaseModel
from datetime import datetime

class PatientGuardianRelationshipMappingBase(BaseModel):
    isDeleted: str
    relationshipName: str


class PatientGuardianRelationshipMappingCreate(PatientGuardianRelationshipMappingBase):
    def __init__(self, **data):
        super().__init__(**data)
        self.createdDate = datetime.now(tz='Asia/Singapore')


class PatientGuardianRelationshipMappingUpdate(PatientGuardianRelationshipMappingBase):
    def __init__(self, **data):
        super().__init__(**data)
        self.modifiedDate = datetime.now(tz='Asia/Singapore')

class PatientGuardianRelationshipMapping(PatientGuardianRelationshipMappingBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int
    