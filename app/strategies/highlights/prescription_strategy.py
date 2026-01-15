from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.patient_prescription_model import PatientPrescription

from .base_strategy import HighlightStrategy


class PrescriptionStrategy(HighlightStrategy):
    """Strategy for generating highlights from chronic or high-risk prescriptions"""
    
    def get_type_code(self) -> str:
        return "PRESCRIPTION"
    
    def should_generate_highlight(self, prescription_record, db: Optional[Session] = None) -> bool:
        """
        Check if prescription should be highlighted.

        """
        # Default: highlight all recently created or updated Prescriptions
        return True
    
    def generate_highlight_text(self, prescription_record) -> str:
        """
        Generate readable prescription highlight text.
        
        Format: "[Chronic/High-Risk] Prescription: [Name] [Dosage] [Frequency]"
        Example: "Chronic Prescription: Metformin 500mg 2x daily"
        """
        # Get prescription name
        prescription_name = "Unknown Prescription"
        if hasattr(prescription_record, 'prescription_list') and prescription_record.prescription_list:
            prescription_name = prescription_record.prescription_list.Value
    
        prefix = ["Prescription"]
        
        # # Build text
        parts = [f"{prefix}: {prescription_name}"]
        
        # Add dosage
        if hasattr(prescription_record, 'Dosage') and prescription_record.Dosage:
            parts.append(prescription_record.Dosage)
        
        # Add frequency
        if hasattr(prescription_record, 'FrequencyPerDay') and prescription_record.FrequencyPerDay:
            freq = prescription_record.FrequencyPerDay
            parts.append(f"{freq}x daily")
        
        return " ".join(parts)
        

    def get_source_remarks(self, db: Session, source_record_id: int) -> Optional[str]:
        """
        Get PrescriptionRemarks from PATIENT_PRESCRIPTION table.
        This contains special instructions or notes about the prescription.
        """
        try:
            prescription = db.query(PatientPrescription).filter(
                PatientPrescription.Id == source_record_id
            ).first()
            
            if prescription:
                return prescription.PrescriptionRemarks
            return None
            
        except Exception as e:
            print(f"Error getting prescription source remarks: {e}")
            return None
    
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        """
        Get prescription-specific additional fields.
        
        Sample return:
        {
            "prescription_name": "Metformin",           # From PATIENT_PRESCRIPTION_LIST.Value
            "dosage": "500mg",                          # From PATIENT_PRESCRIPTION.Dosage
            "frequency_per_day": 2,                     # From PATIENT_PRESCRIPTION.FrequencyPerDay
            "instruction": "Take with food",            # From PATIENT_PRESCRIPTION.Instruction
            "is_after_meal": "1",                       # From PATIENT_PRESCRIPTION.IsAfterMeal
            "status": "Chronic",                        # From PATIENT_PRESCRIPTION.Status
            "start_date": "2025-01-01T00:00:00",       # From PATIENT_PRESCRIPTION.StartDate
            "end_date": null                            # From PATIENT_PRESCRIPTION.EndDate
        }
        """
        try:
            # Query with prescription_list relationship loaded
            prescription = db.query(PatientPrescription).options(
                joinedload(PatientPrescription.prescription_list)
            ).filter(
                PatientPrescription.Id == source_record_id
            ).first()
            
            if not prescription:
                return {}
            
            # Extract fields
            additional_fields = {}
            
            # Get prescription name from PATIENT_PRESCRIPTION_LIST
            if prescription.prescription_list:
                additional_fields["prescription_name"] = prescription.prescription_list.Value
            else:
                additional_fields["prescription_name"] = None
            
            # Get prescription details
            additional_fields["dosage"] = prescription.Dosage
            additional_fields["frequency_per_day"] = prescription.FrequencyPerDay
            additional_fields["instruction"] = prescription.Instruction
            additional_fields["is_after_meal"] = prescription.IsAfterMeal
            additional_fields["status"] = prescription.Status
            
            # Convert dates to ISO format
            if prescription.StartDate:
                additional_fields["start_date"] = prescription.StartDate.isoformat()
            else:
                additional_fields["start_date"] = None
            
            if prescription.EndDate:
                additional_fields["end_date"] = prescription.EndDate.isoformat()
            else:
                additional_fields["end_date"] = None
            
            return additional_fields
            
        except Exception as e:
            print(f"Error getting prescription additional fields: {e}")
            return {}