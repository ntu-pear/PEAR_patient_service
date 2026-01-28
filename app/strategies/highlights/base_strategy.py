from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

'''
This file defines the base strategy class for generating patient highlights. It acts as a interface for all specific highlight strategies
This follows the Strategy Design Pattern, where we will have a factory (Strategy factory) to create and manage different strategy instances.
'''

class HighlightStrategy(ABC):
    """
    Base strategy for generating highlights from different sources.
    
    5 methods to implement:
    1. get_type_code() - Links to database
    2. should_generate_highlight() - Core logic (is this worth highlighting?)
    3. generate_highlight_text() - Display text
    4. get_source_value() - Raw data retrieval for details view
    5. get_additional_fields() - Get type-specific additional fields
    Each strategy corresponds to a specific type of highlight, e.g. Vital, Allergy, Medication, etc.
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
    def should_generate_highlight(self, source_record: Any, db: Optional[Session] = None) -> bool:
        """
        Determine if a source record should generate a highlight. - Highlight logic goes here
        """
        pass
    
    @abstractmethod
    def generate_highlight_text(self, source_record: Any) -> str:
        """
        Generate human-readable highlight text from source record.
        Here we store important information used for display.
        
        E.g. If patient's temperature is > threshold, then return "Fever: XX Degrees"
        """
        pass
    
    @abstractmethod
    def get_source_remarks(self, db: Session, source_record_id: int) -> Optional[str]:
        """
        Each strategy knows how to get its own source remarks - for retrieval of raw data
        This is used when displaying details about the highlight 
        E.g. PrescriptionRemarks for Medication.
        E.g. For the Highlight Type Allergy, this function will retrieve the Remarks (e.g. VitalRemarks).
        """
        pass
    
    @abstractmethod
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        """
        Get type-specific additional fields for the API response.
        
        Each strategy can return different fields based on its type - depends on what the front-end team needs for their front-end.
        """
        pass