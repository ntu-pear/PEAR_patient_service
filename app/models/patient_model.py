import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.patient_list_language_model import PatientListLanguage


class Patient(Base):
    __tablename__ = "PATIENT"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    name = Column(String(255), nullable=False)
    nric = Column(
        String(9), nullable=False
    )  # Remove Unique constraint due to presence soft deletes
    address = Column(String(255))
    tempAddress = Column(String(255))
    homeNo = Column(String(32))
    handphoneNo = Column(String(32))
    gender = Column(String(1), nullable=False)
    dateOfBirth = Column(DateTime, nullable=False)
    isApproved = Column(String(1))
    preferredName = Column(String(255))
    preferredLanguageId = Column(
        Integer, ForeignKey("PATIENT_LIST_LANGUAGE.id")
    )  # Changed to Integer
    updateBit = Column(String(1), default="1", nullable=False)
    autoGame = Column(String(1), default="0", nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    isActive = Column(String(1), default="1", nullable=False)
    isRespiteCare = Column(String(1), nullable=False)
    privacyLevel = Column(Integer, default="0", nullable=False)
    terminationReason = Column(String(255))
    inActiveReason = Column(String(255))
    inActiveDate = Column(DateTime)
    profilePicture = Column(String(255))
    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String
    isDeleted = Column(Integer, default="0", nullable=False)

    allocations = relationship("PatientAllocation", back_populates="patient")
    # guardian = relationship("PatientGuardian", back_populates="patient")
    patient_patient_guardian = relationship(
        "PatientPatientGuardian", back_populates="patient"
    )

    # allergies = relationship("PatientAllergy", back_populates="allergy_list", foreign_keys="[PatientAllergy.allergyListId]")
    allergies = relationship("PatientAllergyMapping", back_populates="patient")
    doctor_notes = relationship("PatientDoctorNote", back_populates="patient")
    photos = relationship("PatientPhoto", back_populates="patient")
    assigned_dementias = relationship(
        "PatientAssignedDementiaMapping", back_populates="patient"
    )
    mobility_records = relationship("PatientMobility", back_populates="patient")
    prescriptions = relationship("PatientPrescription", back_populates="patient")
    medications = relationship("PatientMedication", back_populates="patient")
    social_histories = relationship("PatientSocialHistory", back_populates="patient")
    vitals = relationship("PatientVital", back_populates="patient")
    attendances = relationship("PatientAttendance", back_populates="patient")
    highlights = relationship("PatientHighlight", back_populates="patient")
    privacy = relationship("PatientPrivacyLevel", back_populates="patient")
    problems = relationship("PatientProblem", back_populates="patient")

    _preferred_language = relationship(
        PatientListLanguage,
        foreign_keys=[preferredLanguageId],
        lazy="joined"
    )
    
    @property
    def preferred_language(self) -> Optional[str]:
        """Return the language value (based on the language ID) as a string"""
        if self._preferred_language:
            return self._preferred_language.value
        return None

    # Ensure other models follow similar changes for consistency
    @property
    def mask_nric(self):
        return ("*" * 5) + self.nric[-4:]
