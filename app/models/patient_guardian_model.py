from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientGuardian(Base):
    __tablename__ = "PATIENT_GUARDIAN"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(String(1), default='Y', nullable=False)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    preferredName = Column(String(255))
    gender = Column(String(1), nullable=False)
    contactNo = Column(String(32), nullable=False)
    nric = Column(String(9), nullable=False)
    email = Column(String(255))
    dateOfBirth = Column(DateTime, nullable=False)
    address = Column(String(255), nullable=False)
    tempAddress = Column(String(255))
    relationshipId = Column(Integer, ForeignKey('PATIENT_LIST.id'), nullable=False)
    status = Column(String(255), nullable=False)
    isDeleted = Column(String(1), nullable=False, default="0")
    guardianApplicationUserId = Column(Integer)

    patientId = Column(Integer, ForeignKey('PATIENT.id'))

    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)

    patient_list = relationship("PatientList", back_populates="guardians")
    patient = relationship("Patient", back_populates="guardian")

    allocations = relationship("PatientAllocation", foreign_keys="[PatientAllocation.guardianId]", back_populates="guardian")
    guardian2_allocations = relationship("PatientAllocation", foreign_keys="[PatientAllocation.guardian2Id]", back_populates="guardian2")
