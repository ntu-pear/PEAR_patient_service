from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Patient(Base):
    __tablename__ = "PATIENT"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    nric = Column(String(9), unique=True, nullable=False)
    address = Column(String(255))
    tempAddress = Column(String(255))
    officeNo = Column(String(32))
    handphoneNo = Column(String(32))
    gender = Column(String(1), nullable=False)
    dateOfBirth = Column(DateTime, nullable=False)
    guardianId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    isApproved = Column(String(1))
    preferredName = Column(String(255))
    preferredLanguageId = Column(Integer)  # Changed to Integer
    updateBit = Column(Integer)
    autoGame = Column(Integer)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    patientStatus = Column(String(255), nullable=False)
    terminationReason = Column(String(255))
    patientStatusinActiveReason = Column(String(255))
    patientStatusInActiveDate = Column(String(255))
    profilePicture = Column(String(255))
    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer
    
    guardian = relationship("Patient", remote_side=[id])

# Ensure other models follow similar changes for consistency
