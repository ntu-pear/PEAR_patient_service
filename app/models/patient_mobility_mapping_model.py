from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from app.database import Base


class PatientMobility(Base):
    __tablename__ = "PATIENT_MOBILITY_MAPPING"

    MobilityID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey('PATIENT.id'), nullable=False)
    MobilityListId = Column(Integer, ForeignKey('PATIENT_MOBILITY_LIST.MobilityListId'), nullable=False)  # Foreign Key
    MobilityRemarks = Column(String(255))
    IsRecovered = Column(Boolean, default=False, nullable=False)
    IsDeleted = Column(Boolean, default=False, nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String
    RecoveryDate = Column(Date, nullable=True, default=None) # Default is null for recovery date

    mobility_list = relationship(
        "PatientMobilityList",
        back_populates="mobility_records",
        primaryjoin="PatientMobility.MobilityListId == PatientMobilityList.MobilityListId"
    )

    # Relationship with Patient
    patient = relationship("Patient", back_populates="mobility_records")
