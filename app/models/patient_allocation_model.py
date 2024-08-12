from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientAllocation(Base):
    __tablename__ = "PATIENT_ALLOCATION"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(String(1), default='Y', nullable=False)
    patientId = Column(Integer, ForeignKey('PATIENT.id'))
    doctorId = Column(Integer, nullable=False)
    gameTherapistId = Column(Integer, nullable=False)
    supervisorId = Column(Integer, nullable=False)
    caregiverId = Column(Integer, nullable=False)
    guardianId = Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'), nullable=False)
    tempDoctorId = Column(Integer)
    tempCaregiverId = Column(Integer)
    guardian2Id = Column(Integer, ForeignKey('PATIENT_GUARDIAN.id'))

    createdDate = Column(DateTime, nullable=False, default=datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)

    patient = relationship("Patient", back_populates="allocations")
    guardian = relationship("PatientGuardian", foreign_keys=[guardianId], back_populates="allocations")
    guardian2 = relationship("PatientGuardian", foreign_keys=[guardian2Id], back_populates="guardian2_allocations")
