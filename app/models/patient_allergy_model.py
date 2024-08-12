from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientAllergy(Base):
    __tablename__ = "PATIENT_ALLERGY"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    allergyListId = Column(Integer, ForeignKey('PATIENT_LIST.id'))  # Changed to Integer
    allergyReactionListId = Column(Integer, ForeignKey('PATIENT_LIST.id'))  # Changed to Integer
    allergyRemarks = Column(String(255))

    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="allergies")
    allergy_list = relationship("PatientList", back_populates="allergies")
    allergy_reaction_list = relationship("PatientList", back_populates="allergy_reactions")