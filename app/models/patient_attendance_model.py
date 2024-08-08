from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientAttendance(Base):
    __tablename__ = "PATIENT_ATTENDANCE"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    attendanceDate = Column(DateTime)
    arrivalTime = Column(BigInteger)  # BigInt is ok if storing timestamps
    departureTime = Column(BigInteger)  # BigInt is ok if storing timestamps

    createdDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="attendances")
