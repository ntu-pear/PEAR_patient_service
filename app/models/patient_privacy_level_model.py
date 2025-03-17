from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, BigInteger, Enum as SqlEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from app.database import Base
import pytz
import enum

class PrivacyStatus(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
class PatientPrivacyLevel(Base):
    __tablename__ = 'PRIVACY_LEVEL_SETTING'

    patientId = Column(Integer, ForeignKey('PATIENT.id'), primary_key=True)
    active = Column(Boolean, default=True, nullable=False)
    privacyLevelSensitive = Column(SqlEnum(PrivacyStatus), nullable=False)
    createdDate = Column(DateTime, server_default=func.now(), nullable=False)
    modifiedDate = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    createdById = Column(String(255), nullable=True)
    modifiedById = Column(String(255), nullable=True)

    # Relationship with Patient
    patient = relationship("Patient", back_populates="privacy")
    
    def get_created_date_sgt(self):
        """Convert createdDate to Singapore Time (SGT)"""
        return self.createdDate.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Singapore"))

    def get_modified_date_sgt(self):
        """Convert modifiedDate to Singapore Time (SGT)"""
        return self.modifiedDate.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Singapore"))