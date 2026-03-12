from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PatientHighlight(Base):
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
    IsDeleted = Column(String(0), default="0", nullable=False)
    CreatedById = Column(String(450), nullable=False)
    ModifiedById = Column(String(450), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="highlights")
    # highlight_type = relationship("PatientHighlightType", back_populates="highlights")

    # _highlight_type = relationship("PatientHighlightType", back_populates="highlights")
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
