from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientPrescriptionList(Base):
    __tablename__ = "PATIENT_PRESCRIPTION_LIST"

    Id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    IsDeleted = Column(String(1), default='0', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    Value = Column(String(255))

    prescriptions = relationship(
        "PatientPrescription",
        back_populates="prescription_list",
    )