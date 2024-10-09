from sqlalchemy import Column, Integer, DateTime,String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class PatientPatientGuardian(Base):
    __tablename__ = "PATIENT_PATIENT_GUARDIAN"

    id = Column(Integer, primary_key=True, index=True) 
    patientId = Column(Integer, ForeignKey('PATIENT.id'), nullable=False)
    guardianId =  Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'), nullable=False)
    relationshipId = Column(Integer, ForeignKey('PATIENT_GUARDIAN_RELATIONSHIP_MAPPING.id'), nullable=False)
    isDeleted = Column(String(1), default="0", nullable=False)

    createdDate = Column(DateTime, nullable=False, default=datetime.now())
    modifiedDate = Column(DateTime, nullable=False, default=datetime.now())
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)

    patient = relationship("Patient", back_populates="patient_guardian")
    patient_guardian = relationship("PatientGuardian", back_populates="patient_patient_guardian")
    relationship = relationship("PatientGuardianRelationshipMapping", backref=None)
