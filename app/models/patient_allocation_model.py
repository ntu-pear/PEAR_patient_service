from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientAllocation(Base):
    __tablename__ = "PATIENT_ALLOCATION"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(String(1), default='Y', nullable=False)
    isDeleted = Column(String(1), default='0', nullable=False)
    patientId = Column(Integer, ForeignKey('PATIENT.id'))
    guardianId = Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'), nullable=False)
    guardian2Id = Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'), nullable = True)
    # External DB, uses String for IDs
    doctorId = Column(String, nullable=False)
    gameTherapistId = Column(String, nullable=False)
    supervisorId = Column(String, nullable=False)
    caregiverId = Column(String, nullable=False)
    guardianUserId = Column(String, nullable=True)
    tempDoctorId = Column(String)
    tempCaregiverId = Column(String)
    

    createdDate = Column(DateTime, nullable=False, default=datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String

    patient = relationship("Patient", back_populates="allocations")
    guardian = relationship("PatientGuardian", foreign_keys=[guardianId], back_populates="allocations")
    guardian2 = relationship("PatientGuardian", foreign_keys=[guardian2Id], back_populates="guardian2_allocations")
