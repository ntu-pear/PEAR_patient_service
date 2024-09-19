from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientMobility_MobilityList(Base):
    __tablename__ = "PATIENT_MOBILITY_PATIENT_MOBILITY_LIST"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('PATIENT_MOBILITY.id'), nullable=False)
    mobilityListId = Column(Integer, ForeignKey('PATIENT_MOBILITY_LIST_MAPPING.id'), nullable=False)

    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)
