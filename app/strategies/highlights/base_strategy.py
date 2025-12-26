from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy.orm import Session

'''
This file defines the base strategy class for generating patient highlights. It acts as a interface for all specific highlight strategies
This follows the Strategy Design Pattern, where we will have a factory (Strategy factory) to create and manage different strategy instances.
'''

class HighlightStrategy(ABC):
    """
    Base strategy for generating highlights from different sources.
    
    ULTRA-SIMPLIFIED - Only 3 methods:
    1. get_type_code() - Links to database
    2. should_generate_highlight() - Core logic (is this worth highlighting?)
    3. generate_highlight_text() - Display text
    
    NO get_candidate_records() - not needed for event-driven approach!
    You already have the record when you call the strategy.
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
        Each strategy knows how to get its own source value - for retrieval of raw data.
        This is used when displaying details about the highlight.
        E.g. For the Highlight Type Allergy, this function will retrieve the Value (e.g. Panadol) from the PATIENT_ALLERGY table.
        """
        pass