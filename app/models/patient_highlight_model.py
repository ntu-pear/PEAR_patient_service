from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PatientHighlight(Base):
    __tablename__ = "PATIENT_HIGHLIGHT"

    # Id = Column(Integer, primary_key=True, index=True)
    # IsDeleted = Column(String(1), default="0", nullable=False)
    # PatientId = Column(Integer, ForeignKey("PATIENT.id"), nullable=False)
    # Type = Column(String(255), nullable=False)
    # HighlightJSON = Column(String(255), nullable=False)
    # StartDate = Column(DateTime, nullable=False)
    # EndDate = Column(DateTime, nullable=False)
    # CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    # ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    # CreatedById = Column(String, nullable=False)  # Changed to String
    # ModifiedById = Column(String, nullable=False)  # Changed to String
    
    # patient = relationship("Patient", back_populates="highlights")
    
    """
    Patient Highlight Model - V3 Ultra-Simplified
    
    Stores highlight records for patients with links to source data.
    Each highlight links to:
    - A patient (PatientId)
    - A highlight type (HighlightTypeId)
    - The source record that triggered it (SourceTable + SourceRecordId)
    
    Examples:
    - Vital highlight: Links to PATIENT_VITAL record with abnormal BP
    - Allergy highlight: Links to PATIENT_ALLERGY_MAPPING with active allergy
    """
    __tablename__ = "PATIENT_HIGHLIGHT"

    # Primary Key
    Id = Column(Integer, primary_key=True, index=True)
    
    # Core Fields
    PatientId = Column(Integer, ForeignKey("PATIENT.id"), nullable=False, index=True)
    HighlightTypeId = Column(Integer, ForeignKey("PATIENT_HIGHLIGHT_TYPE.Id"), nullable=False, index=True)
    HighlightText = Column(String(500), nullable=False)  # Display text (e.g., "High BP: 180/110 mmHg")
    
    # Source Tracking - Links back to original record
    SourceTable = Column(String(50), nullable=False)      # Table name (e.g., "PATIENT_VITAL")
    SourceRecordId = Column(Integer, nullable=False)      # ID in source table
    
    # Audit Fields
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    IsDeleted = Column(Integer, default=0, nullable=False)
    CreatedById = Column(String(450), nullable=False)
    ModifiedById = Column(String(450), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="highlights")
    # highlight_type = relationship("PatientHighlightType", back_populates="highlights")

    # _highlight_type = relationship("PatientHighlightType", back_populates="highlights")# NEW (Like preferred_language pattern)
    _highlight_type = relationship(
        "PatientHighlightType",
        foreign_keys=[HighlightTypeId],
        lazy="joined"  # Auto-loads type info
    )

    @property
    def highlight_type_name(self) -> Optional[str]:
        """Return type name (e.g., 'Vital Signs Alert')"""
        if self._highlight_type:
            return self._highlight_type.TypeName
        return None

    @property
    def highlight_type_code(self) -> Optional[str]:
        """Return type code (e.g., 'VITAL')"""
        if self._highlight_type:
            return self._highlight_type.TypeCode
        return None    