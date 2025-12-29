from sqlalchemy.orm import Session, joinedload

from app.models.patient_allergy_mapping_model import PatientAllergyMapping

from .base_strategy import HighlightStrategy


class AllergyStrategy(HighlightStrategy):
    """Strategy for generating highlights from active allergies"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "ALLERGY"
    
    def should_generate_highlight(self, allergy_record) -> bool:
        """
        Check if allergy should be highlighted.
        
        CUSTOMIZE THIS based on your needs:
        - Option 1: Highlight ALL active allergies (default)
        - Option 2: Only highlight severe allergies
        - Option 3: Highlight specific allergens
        """
        
        # ** Need to discuss with prof about this logic
        
        # Option 1: Highlight all active allergies
        # if hasattr(allergy_record, 'AllergyTypeID'):
        #     return allergy_record.AllergyTypeID == "3" # Testing only
        
        # Option 2: Only severe allergies
        # if hasattr(allergy_record, 'Severity'):
        #     return allergy_record.Severity in ["Severe", "Critical"]
        
        # Option 3: Specific allergens
        # high_risk_allergens = ["Penicillin", "Latex", "Iodine"]
        # if hasattr(allergy_record, 'AllergyName'):
        #     return allergy_record.AllergyName in high_risk_allergens
        
        # Default: highlight all
        return True
    
    def generate_highlight_text(self, allergy_record) -> str:
        """
        Generate readable allergy text.
        Shows the allergy name and optionally severity.
        """
        # Get allergy name
        allergy_name = getattr(allergy_record, 'AllergyName', 
                              getattr(allergy_record, 'Allergen', 'Unknown allergy'))
        
        # Include severity if available
        if hasattr(allergy_record, 'Severity') and allergy_record.Severity:
            return f"Allergy: {allergy_name} ({allergy_record.Severity})"
        else:
            return f"Allergy: {allergy_name}"
        
    def get_source_value(self, db, source_record_id):
        """
        Get the allergy name from ALLERGY_TYPE via PATIENT_ALLERGY_MAPPING.
        
        For allergies, the source is PATIENT_ALLERGY_MAPPING, but the "value"
        we want to display is the AllergyType.Value (e.g., "Penicillin").
        
        We need to:
        1. Query PATIENT_ALLERGY_MAPPING by Patient_AllergyID
        2. Join to ALLERGY_TYPE to get the Value
        """
        try:
            allergy_mapping = db.query(PatientAllergyMapping).options(
                joinedload(PatientAllergyMapping.allergy_type)
            ).filter(
                PatientAllergyMapping.Patient_AllergyID == source_record_id  # 12
            ).first()
            
            if allergy_mapping and allergy_mapping.allergy_type:
                return allergy_mapping.allergy_type.Value
            return None
            
        except Exception as e:
            # Log error but don't fail the entire request
            print(f"Error getting allergy source value: {e}")
            return None