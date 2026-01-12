from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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
    doctorId = Column(String, nullable=True)
    gameTherapistId = Column(String, nullable=True)
    supervisorId = Column(String, nullable=True)
    caregiverId = Column(String, nullable=True)
    tempDoctorId = Column(String)
    tempCaregiverId = Column(String)
    

    createdDate = Column(DateTime, nullable=False, default=datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String

    patient = relationship("Patient", back_populates="allocations")
    guardian = relationship("PatientGuardian", foreign_keys=[guardianId], back_populates="allocations")
    guardian2 = relationship("PatientGuardian", foreign_keys=[guardian2Id], back_populates="guardian2_allocations")
