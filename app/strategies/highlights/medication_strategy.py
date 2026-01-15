from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.patient_medication_model import PatientMedication

from .base_strategy import HighlightStrategy


class MedicationStrategy(HighlightStrategy):
    """Strategy for generating highlights from high-risk medications"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "MEDICATION"
    
    def should_generate_highlight(self, medication_record, db: Optional[Session] = None) -> bool:
        """
        Check if medication is high-risk and should be highlighted.
        
        This function can be customized based on hospital needs. For the base code, I identified certain high risk medications that should be flagged as a highlight.
        """
        
        # Default: highlight all recently created or updated Medications
        return True
    
    def generate_highlight_text(self, medication_record) -> str:
        """
        Generate readable medication text.
        Shows medication name and optionally dose/route.
        """
        # Get medication name from prescription_list
        med_name = "Unknown Medication"
        if hasattr(medication_record, 'prescription_list') and medication_record.prescription_list:
            med_name = medication_record.prescription_list.Value
        
        # Build highlight text
        parts = [f"Medication: {med_name}"]
        # Add dosage if available
        if hasattr(medication_record, 'Dosage') and medication_record.Dosage:
            parts.append(medication_record.Dosage)
        
        # Add instruction if available
        if hasattr(medication_record, 'Instruction') and medication_record.Instruction:
            parts.append(medication_record.Instruction)
        
        return " ".join(parts)
    
    def get_source_remarks(self, db, source_record_id):
        try:
            # Query PATIENT_MEDICATION by Id
            medication = db.query(PatientMedication).filter(
                PatientMedication.Id == source_record_id
            ).first()
            
            if medication:
                return medication.PrescriptionRemarks
            return None
            
        except Exception as e:
            print(f"Error getting medication source remarks: {e}")
            return None

    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        """
        Get medication-specific additional fields.
        
        Sample return:
        {
            "prescription_name": "Warfarin",              # From PATIENT_PRESCRIPTION_LIST.Value
            "dosage": "5mg",                              # From PATIENT_MEDICATION.Dosage
            "instruction": "PO Daily",                    # From PATIENT_MEDICATION.Instruction
            "administer_time": "08:00",                   # From PATIENT_MEDICATION.AdministerTime
            "start_date": "2025-01-01",                   # From PATIENT_MEDICATION.StartDate
            "end_date": "2025-12-31"                      # From PATIENT_MEDICATION.EndDate
        }
        """
        try:
            # Query with prescription_list relationship loaded
            medication = db.query(PatientMedication).options(
                joinedload(PatientMedication.prescription_list)
            ).filter(
                PatientMedication.Id == source_record_id
            ).first()
            
            if not medication:
                return {}
            
            # Extract the fields you want
            additional_fields = {}
            
            # Get prescription name (from PATIENT_PRESCRIPTION_LIST.Value)
            if medication.prescription_list:
                additional_fields["prescription_name"] = medication.prescription_list.Value
            else:
                additional_fields["prescription_name"] = None
            
            # Get medication details
            additional_fields["dosage"] = medication.Dosage
            additional_fields["instruction"] = medication.Instruction
            additional_fields["administer_time"] = medication.AdministerTime
            
            # Convert dates to ISO format strings
            if medication.StartDate:
                additional_fields["start_date"] = medication.StartDate.isoformat()
            else:
                additional_fields["start_date"] = None
                
            if medication.EndDate:
                additional_fields["end_date"] = medication.EndDate.isoformat()
            else:
                additional_fields["end_date"] = None
            
            return additional_fields
            
        except Exception as e:
            print(f"Error getting medication additional fields: {e}")
            return {}