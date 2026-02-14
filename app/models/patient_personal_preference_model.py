from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class PatientPersonalPreference(Base):
    __tablename__ = "PATIENT_PERSONAL_PREFERENCE"

    Id = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("PATIENT.id"), nullable=False, index=True)
    PersonalPreferenceListID = Column(Integer, ForeignKey("PATIENT_PERSONAL_PREFERENCE_LIST.Id"), nullable=False, index=True)
    IsLike = Column(String(1), nullable=True) # 'Y' = Like, 'N' = Dislike, NULL = not applicable (Habit / Hobby)
    PreferenceRemarks = Column(String(500), nullable=True)
    IsDeleted = Column(String(1), default='0', nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID  = Column(String(450), nullable=False)
    ModifiedByID = Column(String(450), nullable=False)

    __table_args__ = (
        UniqueConstraint("PatientID", "PersonalPreferenceListID", name="UQ_PatientPersonalPreference_PatientPref"), # This constraint ensures that the combination of patient ID and preference is unique.
    )

    # Relationships
    patient = relationship("Patient", back_populates="personal_preferences")
    preference_list = relationship("PatientPersonalPreferenceList", back_populates="patient_preferences")