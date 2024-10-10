from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Patient(Base):
    __tablename__ = "PATIENT"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    nric = Column(String(9), unique=True, nullable=False)
    address = Column(String(255))
    tempAddress = Column(String(255))
    homeNo = Column(String(32))
    handphoneNo = Column(String(32))
    gender = Column(String(1), nullable=False)
    dateOfBirth = Column(DateTime, nullable=False)
    guardianId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    isApproved = Column(String(1))
    preferredName = Column(String(255))
    preferredLanguageId = Column(Integer, nullable=False)  # Changed to Integer
    updateBit = Column(String(1), default='1', nullable=False)
    autoGame = Column(String(1), default='0', nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    isActive = Column(String(1), default='1', nullable=False)
    isRespiteCare = Column(String(1), nullable=False)
    privacyLevel = Column(Integer, default='0', nullable=False)
    terminationReason = Column(String(255))
    inActiveReason = Column(String(255))
    inActiveDate = Column(DateTime)
    profilePicture = Column(String(255))
    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer
    
    allocations = relationship("PatientAllocation", back_populates="patient")
    #guardian = relationship("PatientGuardian", back_populates="patient")
    patient_guardian = relationship("PatientPatientGuardian", back_populates="patient")
    #allergies = relationship("PatientAllergy", back_populates="allergy_list", foreign_keys="[PatientAllergy.allergyListId]")
    allergies = relationship("PatientAllergyMapping", back_populates="patient")
    doctor_notes = relationship("PatientDoctorNote", back_populates="patient")
    photos = relationship("PatientPhoto", back_populates="patient")
    assigned_dementias = relationship("PatientAssignedDementia", back_populates="patient")
    mobility_records = relationship("PatientMobility", back_populates="patient")
    prescriptions = relationship("PatientPrescription", back_populates="patient")
    social_histories = relationship("PatientSocialHistory", back_populates="patient")
    vitals = relationship("PatientVital", back_populates="patient")
    attendances = relationship("PatientAttendance", back_populates="patient")
    highlights = relationship("PatientHighlight", back_populates="patient")
# Ensure other models follow similar changes for consistency
