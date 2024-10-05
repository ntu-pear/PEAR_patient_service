from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class PatientGuardianRelationshipMapping(Base):
    __tablename__ = "PATIENT_GUARDIAN_RELATIONSHIP_MAPPING"

    id = Column(Integer, primary_key=True, index=True)  
    isDeleted = Column(String(1), default='0', nullable=False)  
    relationshipName = Column(String(255), nullable = False)

    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)