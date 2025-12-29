from app.models.patient_medication_model import PatientMedication

from .base_strategy import HighlightStrategy


class MedicationStrategy(HighlightStrategy):
    """Strategy for generating highlights from high-risk medications (ultra-simplified)"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "MEDICATION"
    
    def should_generate_highlight(self, medication_record) -> bool:
        """
        Check if medication is high-risk and should be highlighted.
        
        This function can be customized based on hospital needs. For the base code, I identified certain high risk medications that should be flagged as a highlight.
        """
        medication_name = None
        # Here we only want to deal with active medications
        if hasattr(medication_record, 'IsDeleted'):
            if medication_record.IsDeleted != "0":
                return False
        
        # Get medication name from prescription_list relationship
        medication_name = None
        if hasattr(medication_record, 'prescription_list') and medication_record.prescription_list:
            medication_name = medication_record.prescription_list.Value
        
        if not medication_name:
            return False  # No medication name, can't determine if high-risk - don't highlight
        
        # List of high-alert medications
        high_alert_medications = [
            'Acetaminophen',
            'Diphenhydramine',
            'Donepezil',
            'Galantamine',
            'Guaifenesin',
            'Ibuprofen',
        ]
        
        # Check if medication name contains any high-alert medication
        med_name_lower = medication_name.lower()
        for alert_med in high_alert_medications:
            if alert_med.lower() in med_name_lower:
                return True
        
        # Default: don't highlight
        return False
    
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
        parts = [f"High-Risk Medication: {med_name}"]
        
        # Add dosage if available
        if hasattr(medication_record, 'Dosage') and medication_record.Dosage:
            parts.append(medication_record.Dosage)
        
        # Add instruction if available
        if hasattr(medication_record, 'Instruction') and medication_record.Instruction:
            parts.append(medication_record.Instruction)
        
        return " ".join(parts)
    
    def get_source_value(self, db, source_record_id):
        # Implement this after confirming logic with prof
        try:
            # Query PATIENT_MEDICATION by Id
            medication = db.query(PatientMedication).filter(
                PatientMedication.Id == source_record_id
            ).first()
            
            if medication:
                return medication.PrescriptionRemarks
            return None
            
        except Exception as e:
            print(f"Error getting medication source value: {e}")
            return None