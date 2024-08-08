from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

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
    relationshipId = Column(Integer, ForeignKey('PATIENT_LIST.id'), nullable=False)  # Changed to Integer
    status = Column(String(255), nullable=False)
    guardianApplicationUserId = Column(Integer)  # Changed to Integer

    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient_list = relationship("PatientList", back_populates="guardians")
    patients = relationship("Patient", back_populates="guardian")
    allocations = relationship("PatientAllocation", back_populates="guardian")