from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.patient_allergy_mapping_model import PatientAllergyMapping

from .base_strategy import HighlightStrategy


class AllergyStrategy(HighlightStrategy):
    """Strategy for generating highlights from allergies"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "ALLERGY"
    
    def should_generate_highlight(self, allergy_record, db: Optional[Session] = None) -> bool:
        """
        Check if allergy should be highlighted. By default, all recent allergies are highlighted.
        Logic:
        - Highlight only active allergies (IsDeleted = '0')
        - When allergy is deleted (IsDeleted = '1'), this returns False
        """
        
        if hasattr(allergy_record, 'IsDeleted'):
            return allergy_record.IsDeleted == '0'
        return True
    
    def generate_highlight_text(self, allergy_record, db: Optional[Session] = None, source_record_id: Optional[int] = None) -> str:
        """
        Generate readable allergy text.
        Shows the allergy type and optionally reaction type.
        """
        # If db and source_record_id are provided, fetch the full record with relationships
        if db is not None and source_record_id is not None:
            allergy_record = db.query(PatientAllergyMapping).options(
                joinedload(PatientAllergyMapping.allergy_type),
                joinedload(PatientAllergyMapping.allergy_reaction_type)
            ).filter(
                PatientAllergyMapping.Patient_AllergyID == source_record_id
            ).first()
            
            if not allergy_record:
                return "Allergy: Unknown"
        
        # Get allergy type from ALLERGY_TYPE.Value through relationship
        allergy_type = "Unknown allergy"
        if hasattr(allergy_record, 'allergy_type') and allergy_record.allergy_type:
            allergy_type = allergy_record.allergy_type.Value
        
        # Get reaction type from ALLERGY_REACTION_TYPE.Value through relationship
        reaction_type = None
        if hasattr(allergy_record, 'allergy_reaction_type') and allergy_record.allergy_reaction_type:
            reaction_type = allergy_record.allergy_reaction_type.Value
        
        # Build the highlight text
        if reaction_type:
            return f"Allergy: {allergy_type} ({reaction_type})"
        else:
            return f"Allergy: {allergy_type}"
        
    def get_source_remarks(self, db, source_record_id):
        """
        Get the allergy remarks.
        
        We need to:
        1. Query PATIENT_ALLERGY_MAPPING by Patient_AllergyID
        2. Join to ALLERGY_TYPE to get the Remarks
        """
        try:
            allergy_mapping = db.query(PatientAllergyMapping).options(
                joinedload(PatientAllergyMapping.allergy_type)
            ).filter(
                PatientAllergyMapping.Patient_AllergyID == source_record_id
            ).first()
            
            if allergy_mapping:
                return allergy_mapping.AllergyRemarks
            return None
            
        except Exception as e:
            # Log error but don't fail the entire request
            print(f"Error getting allergy source value: {e}")
            return None
        
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        """
        Get allergy-specific additional fields.
        
        Sample return:
        {
            "allergy_type": "Penicillin",           # From ALLERGY_TYPE.Value
            "allergy_reaction_type": "Severe"       # From ALLERGY_REACTION_TYPE.Value
        }
        """
        try:
            # Query with relationships loaded
            allergy_mapping = db.query(PatientAllergyMapping).options(
                joinedload(PatientAllergyMapping.allergy_type),
                joinedload(PatientAllergyMapping.allergy_reaction_type)
            ).filter(
                PatientAllergyMapping.Patient_AllergyID == source_record_id
            ).first()
            
            if not allergy_mapping:
                return {}
            
            # Extract the fields you want
            additional_fields = {}
            
            # Get allergy type (from ALLERGY_TYPE.Value)
            if allergy_mapping.allergy_type:
                additional_fields["allergy_type"] = allergy_mapping.allergy_type.Value
            else:
                additional_fields["allergy_type"] = None
            
            # Get reaction type (from ALLERGY_REACTION_TYPE.Value)
            if allergy_mapping.allergy_reaction_type:
                additional_fields["allergy_reaction_type"] = allergy_mapping.allergy_reaction_type.Value
            else:
                additional_fields["allergy_reaction_type"] = None
            
            return additional_fields
            
        except Exception as e:
            print(f"Error getting allergy additional fields: {e}")
            return {}