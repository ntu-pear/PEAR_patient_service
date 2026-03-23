from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PatientHighlightType(Base):
    __tablename__ = "PATIENT_HIGHLIGHT_TYPE"

    # Primary Key
    Id = Column(Integer, primary_key=True, index=True)
    
    # Type Information
    TypeName = Column(String(100), nullable=False)
    TypeCode = Column(String(50), nullable=False, unique=True, index=True)  # For strategies (e.g., "VITAL")
    Description = Column(String(500), nullable=True) # Optional description
    
    # Configuration
    IsEnabled = Column(String(0), default="1", nullable=False, index=True)  # Admin can enable/disable
    
    # Audit Fields
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    IsDeleted = Column(String(0), nullable=False, default="0", index=True)
    CreatedById = Column(String(450), nullable=False)
    ModifiedById = Column(String(450), nullable=False)