from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
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
    CreatedById = Column(Integer, nullable=False)
    ModifiedById = Column(Integer, nullable=False)

    mobility_list = relationship(
        "PatientMobilityList",
        back_populates="mobility_records",
        primaryjoin="PatientMobility.MobilityListId == PatientMobilityList.MobilityListId"
    )

    # Relationship with Patient
    patient = relationship("Patient", back_populates="mobility_records")
