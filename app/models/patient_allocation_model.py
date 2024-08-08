from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientAllocation(Base):
    __tablename__ = "PATIENT_ALLOCATION"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    doctorId = Column(Integer, nullable=False)  # references user microservice, Changed to Integer
    gameTherapistId = Column(Integer, nullable=False)  # references user microservice, Changed to Integer
    supervisorId = Column(Integer, nullable=False)  # references user microservice, Changed to Integer
    caregiverId = Column(Integer, nullable=False)  # references user microservice, Changed to Integer
    guardianId = Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'), nullable=False)  # Changed to Integer
    tempDoctorId = Column(Integer)  # references user microservice, Changed to Integer
    tempCaregiverId = Column(Integer)  # references user microservice, Changed to Integer
    guardian2Id = Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'))  # Changed to Integer
    
    createdDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="allocations")
    guardian = relationship("PatientGuardian", back_populates="allocations")
    guardian2 = relationship("PatientGuardian")  # Assuming the same class is used