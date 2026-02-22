from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.patient_personal_preference_list_model import PatientPersonalPreferenceList


class PatientPersonalPreference(Base):
    __tablename__ = "PATIENT_PERSONAL_PREFERENCE"

    Id = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("PATIENT.id"), nullable=False, index=True)
    PersonalPreferenceListID = Column(Integer, ForeignKey("PATIENT_PERSONAL_PREFERENCE_LIST.Id"), nullable=False, index=True)
    IsLike = Column(String(1), nullable=True)  # 'Y' = Like, 'N' = Dislike, NULL = not applicable (Habit / Hobby)
    PreferenceRemarks = Column(String(500), nullable=True)
    IsDeleted = Column(String(1), default='0', nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID = Column(String(450), nullable=False)
    ModifiedByID = Column(String(450), nullable=False)

    __table_args__ = (
        UniqueConstraint("PatientID", "PersonalPreferenceListID", name="UQ_PatientPersonalPreference_PatientPref"),
    )

    # Relationships
    patient = relationship("Patient", back_populates="personal_preferences")
    _preference_list = relationship(
        PatientPersonalPreferenceList,
        foreign_keys=[PersonalPreferenceListID],
        back_populates="patient_preferences",
        lazy="joined"
    )

    @property
    def preference_name(self) -> Optional[str]:
        """Return PreferenceName from the linked preference list item."""
        if self._preference_list:
            return self._preference_list.PreferenceName
        return None

    @property
    def preference_type(self) -> Optional[str]:
        """Return PreferenceType from the linked preference list item."""
        if self._preference_list:
            return self._preference_list.PreferenceType
        return None