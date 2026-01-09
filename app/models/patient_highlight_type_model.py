from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PatientHighlightType(Base):
    __tablename__ = "PATIENT_HIGHLIGHT_TYPE"

    # HighlightTypeID = Column(Integer, primary_key=True, index=True)
    # Value = Column(String(255), nullable=False)  
    # IsDeleted = Column(String(0), default="0", nullable=False)
    # CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    # UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    # CreatedById = Column(String, nullable=False)  # Changed to String
    # ModifiedById = Column(String, nullable=False)  # Changed to String

    """
    Patient Highlight Type Model - V3 Ultra-Simplified (NO PRIORITY)
    
    Configuration table for different types of highlights.
    Each type defines:
    - What kind of highlight (VITAL, ALLERGY, PROBLEM, MEDICATION)
    - Whether it's enabled (admin can toggle)
    - How long to keep highlights (retention in business days)
    
    Examples:
    - VITAL: Abnormal vital signs, 3 business days retention
    - ALLERGY: Active allergies, 7 business days retention
    
    NOTE: No Priority field - frontend sorts by PatientId + CreatedDate
    """
    __tablename__ = "PATIENT_HIGHLIGHT_TYPE"

    # Primary Key
    Id = Column(Integer, primary_key=True, index=True)
    
    # Type Information
    TypeName = Column(String(100), nullable=False)           # Human-readable (e.g., "Vital Signs Alert")
    TypeCode = Column(String(50), nullable=False, unique=True, index=True)  # For strategies (e.g., "VITAL")
    Description = Column(String(500), nullable=True)         # Optional description
    
    # Configuration
    IsEnabled = Column(Boolean, nullable=False, default=True, index=True)  # Admin can enable/disable
    
    # Audit Fields
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    IsDeleted = Column(Boolean, nullable=False, default=False, index=True)
    CreatedById = Column(String(450), nullable=False)
    ModifiedById = Column(String(450), nullable=False)