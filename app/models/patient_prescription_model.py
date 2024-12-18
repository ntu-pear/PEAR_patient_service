from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.patient_prescription_list_model import PatientPrescriptionList

class PatientPrescription(Base):
    __tablename__ = "PATIENT_PRESCRIPTION"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='1', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    prescriptionListId = Column(Integer, ForeignKey('PATIENT_PRESCRIPTION_LIST.id'))  # Changed to Integer
    dosage = Column(String(255), nullable=False)
    frequencyPerDay = Column(BigInteger, nullable=False)
    instruction = Column(String(255), nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    afterMeal = Column(String(1))
    prescriptionRemarks = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)  # used in place of ischronic

    createdDateTime = Column(DateTime, nullable=False, default=DateTime)
    modifiedDateTime = Column(DateTime, nullable=False, default=DateTime)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="prescriptions")
    prescription_list = relationship("PatientPrescriptionList", back_populates="prescriptions")
