from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientMobilityList(Base):
    __tablename__ = "PATIENT_MOBILITY_LIST"

    MobilityListId = Column(Integer, primary_key=True, index=True)
    IsDeleted = Column(Integer, default=False, nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedById = Column(Integer, nullable=False)  # Changed to Integer
    ModifiedById = Column(Integer, nullable=False)  # Changed to Integer
    Value = Column(String(255), nullable=False)

    mobility_records = relationship(
        "PatientMobility",
        back_populates="mobility_list",
        primaryjoin="PatientMobility.MobilityListId == PatientMobilityList.MobilityListId"
    )
