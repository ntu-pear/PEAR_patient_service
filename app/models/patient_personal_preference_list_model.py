from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base

VALID_PREFERENCE_TYPES = {"LikesDislikes", "Habit", "Hobby"}


class PatientPersonalPreferenceList(Base):
    __tablename__ = "PATIENT_PERSONAL_PREFERENCE_LIST"

    Id = Column(Integer, primary_key=True, index=True)
    PreferenceType = Column(String(50), nullable=False)  # LikesDislikes, Habit or Hobby
    PreferenceName = Column(String(255), nullable=False)
    IsDeleted = Column(String(1), default='0', nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID = Column(String(450), nullable=False)
    ModifiedByID = Column(String(450), nullable=False)

    __table_args__ = (
        UniqueConstraint("PreferenceType", "PreferenceName", name="UQ_PersonalPreferenceList_TypeName"),
    )

    # Relationship back to patient preference mappings
    patient_preferences = relationship(
        "PatientPersonalPreference",
        back_populates="_preference_list"
    )