from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class PatientAllergyMapping(Base):
    __tablename__ = "PATIENT_ALLERGY_MAPPING"

    Patient_AllergyID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("PATIENT.id"), nullable=False)
    AllergyListID = Column(Integer, ForeignKey("ALLERGY_TYPE.AllergyTypeID"), nullable=False)
    AllergyReactionListID = Column(Integer, ForeignKey("ALLERGY_REACTION_TYPE.AllergyReactionTypeID"), nullable=False)
    AllergyRemarks = Column(String(255))
    Active = Column(String(1), default="1", nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)

    # Relationships
    allergy_type = relationship("AllergyType")
    allergy_reaction_type = relationship("AllergyReactionType")

    # Relationship to Patient
    patient = relationship("Patient", back_populates="allergies")