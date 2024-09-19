from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientMobilityList(Base):
    __tablename__ = "PATIENT_MOBILITY_LIST_MAPPING"

    id = Column(Integer, primary_key=True, index=True)
    mobilityListId = Column(Integer, ForeignKey('PATIENT_MOBILITY_LIST_MAPPING.id'), nullable=False)
    IsDeleted = Column(Boolean, default=False, nullable=False)
    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    value = Column(String(255), nullable=False)

    mobility_records = relationship("PatientMobility", secondary="PATIENT_MOBILITY_PATIENT_MOBILITY_LIST", back_populates="mobility_lists")
