from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

from sqlalchemy.orm import Session, joinedload

'''
This file defines the base strategy class for generating patient highlights. It acts as a interface for all specific highlight strategies
This follows the Strategy Design Pattern, where we will have a factory (Strategy factory) to create and manage different strategy instances.
'''

class HighlightStrategy(ABC):
    """
    Base strategy for generating highlights from different sources.
    
    4 methods to implement:
    1. get_type_code() - Links to database
    2. should_generate_highlight() - Core logic (is this worth highlighting?)
    3. generate_highlight_text() - Display text
    4. get_source_value() - Raw data retrieval for details view
    5. get_additional_fields() - Get type-specific additional fields
    Each strategy corresponds to a specific type of highlight, e.g., Vital, Allergy, Medication, etc.
    """
    
    @abstractmethod
    def get_type_code(self) -> str:
        """
        Return the type code for this strategy.
        Must match TypeCode in PATIENT_HIGHLIGHT_TYPE table.
        
        Returns:
            str: Type code (e.g., 'VITAL', 'ALLERGY')
        
        Example:
            return "VITAL"
        """
        pass
    
    @abstractmethod
    def should_generate_highlight(self, source_record: Any) -> bool:
        """
        Determine if a source record should generate a highlight.
        
        *** This function determines whether a record should be highlighted or not
        
        Args:
            source_record: The source record to evaluate (e.g., Vital, Allergy)
        
        Returns:
            bool: True if highlight should be generated
        
        Examples:
            # For vitals - check if BP is abnormal
            if source_record.Systolic > 140:
                return True
            
            # For allergies - check if active
            if source_record.Status == "Active":
                return True
        """
        pass
    
    @abstractmethod
    def generate_highlight_text(self, source_record: Any) -> str:
        """
        Generate human-readable highlight text from source record.
        This is what the user will see in the UI.
        
        Args:
            source_record: The source record
        
        Returns:
            str: Highlight text for display (max 500 chars)
        
        Examples:
            return f"High BP: {source_record.Systolic}/{source_record.Diastolic} mmHg"
            return f"Allergy: {source_record.AllergyName}"
        """
        pass
    
    @abstractmethod
    def get_source_value(self, db: Session, source_record_id: int) -> Optional[str]:
        """
        Each strategy knows how to get its own source value - for retrieval of raw data
        This is used when displaying details about the highlight 
        E.g. PrescriptionRemarks for Medication.
        E.g. For the Highlight Type Allergy, this function will retrieve the Value (e.g. Panadol) from the PATIENT_ALLERGY table.
        """
        pass
    
    @abstractmethod
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        """
        Get type-specific additional fields for the API response.
        
        Each strategy can return different fields based on its type.
        
        Examples:
        - AllergyStrategy returns: {"allergy_type": "Penicillin", "reaction_type": "Severe"}
        - MedicationStrategy returns: {"prescription_name": "Warfarin", "prescription_remarks": "Monitor INR"}
        - VitalStrategy returns: {"systolic_bp": 180, "diastolic_bp": 110, "temperature": 39.5}
        
        Args:
            db: Database session
            source_record_id: ID of the source record
            
        Returns:
            Dict[str, Any]: Dictionary of additional fields specific to this type
        """
        pass