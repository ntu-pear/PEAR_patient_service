from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Patient(Base):
    __tablename__ = "PATIENT"

    id = Column(Integer, primary_key=True, index=True)  # Changed to PascalCase
    Active = Column(String(1), default='Y', nullable=False)
    Name = Column(String(255), nullable=False)
    Nric = Column(String(9), unique=True, nullable=False)
    Address = Column(String(255))
    TempAddress = Column(String(255))
    HomeNo = Column(String(32))
    HandphoneNo = Column(String(32))
    Gender = Column(String(1), nullable=False)
    DateOfBirth = Column(DateTime, nullable=False)
    IsApproved = Column(String(1))
    PreferredName = Column(String(255))
    PreferredLanguageId = Column(Integer, ForeignKey('PATIENT_LIST_LANGUAGE.id'))  # Changed ForeignKey to PascalCase
    UpdateBit = Column(String(1), default='1', nullable=False)
    AutoGame = Column(String(1), default='0', nullable=False)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime)
    IsActive = Column(String(1), default='1', nullable=False)
    IsRespiteCare = Column(String(1), nullable=False)
    PrivacyLevel = Column(Integer, default='0', nullable=False)
    TerminationReason = Column(String(255))
    InActiveReason = Column(String(255))
    InActiveDate = Column(DateTime)
    ProfilePicture = Column(String(255))
    CreatedDate = Column(DateTime, nullable=False)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String
    IsDeleted = Column(Integer, default='0', nullable=False)

    allocations = relationship("PatientAllocation", back_populates="patient")
    #guardian = relationship("PatientGuardian", back_populates="patient")
    patient_patient_guardian = relationship("PatientPatientGuardian", back_populates="patient")

    #allergies = relationship("PatientAllergy", back_populates="allergy_list", foreign_keys="[PatientAllergy.allergyListId]")
    allergies = relationship("PatientAllergyMapping", back_populates="patient")
    doctor_notes = relationship("PatientDoctorNote", back_populates="patient")
    photos = relationship("PatientPhoto", back_populates="patient")
    assigned_dementias = relationship("PatientAssignedDementiaMapping", back_populates="patient")
    mobility_records = relationship("PatientMobility", back_populates="patient")
    prescriptions = relationship("PatientPrescription", back_populates="patient")
    social_histories = relationship("PatientSocialHistory", back_populates="patient")
    vitals = relationship("PatientVital", back_populates="patient")
    attendances = relationship("PatientAttendance", back_populates="patient")
    highlights = relationship("PatientHighlight", back_populates="patient")
# Ensure other models follow similar changes for consistency
