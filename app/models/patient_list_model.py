from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
import datetime

class PatientList(Base):
    __tablename__ = "PATIENT_LIST"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(String(1), default='Y', nullable=False)
    type = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    listOrder = Column(Integer)

    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)
