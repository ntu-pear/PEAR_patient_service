from .base_strategy import HighlightStrategy

class MedicationStrategy(HighlightStrategy):
    """Strategy for generating highlights from high-risk medications (ultra-simplified)"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "MEDICATION"
    
    def should_generate_highlight(self, medication_record) -> bool:
        """
        Check if medication is high-risk and should be highlighted.
        
        CUSTOMIZE THIS based on your hospital's high-alert medication list!
        """
        # Only active medications
        if hasattr(medication_record, 'Status'):
            if medication_record.Status != "Active":
                return False
        
        # Check for high-risk medication classes
        if hasattr(medication_record, 'DrugClass'):
            high_risk_classes = [
                'Anticoagulant',
                'Chemotherapy',
                'Insulin',
                'Narcotic',
                'Sedative',
                'Immunosuppressant'
            ]
            if medication_record.DrugClass in high_risk_classes:
                return True
        
        # Check for specific high-alert medications
        if hasattr(medication_record, 'MedicationName'):
            # CUSTOMIZE THIS LIST for your hospital!
            high_alert_meds = [
                'Warfarin',
                'Heparin',
                'Insulin',
                'Morphine',
                'Fentanyl',
                'Propofol',
                'Potassium Chloride',
                'Sodium Chloride (hypertonic)',
                'Methotrexate',
                'Epinephrine'
            ]
            
            med_name = medication_record.MedicationName.lower()
            for alert_med in high_alert_meds:
                if alert_med.lower() in med_name:
                    return True
        
        # Default: don't highlight
        return False
    
    def generate_highlight_text(self, medication_record) -> str:
        """
        Generate readable medication text.
        Shows medication name and optionally dose/route.
        """
        med_name = getattr(medication_record, 'MedicationName', 'Medication')
        
        # Build highlight text with available details
        parts = [f"High-Risk Med: {med_name}"]
        
        if hasattr(medication_record, 'Dose') and medication_record.Dose:
            parts.append(f"{medication_record.Dose}")
        
        if hasattr(medication_record, 'Route') and medication_record.Route:
            parts.append(f"{medication_record.Route}")
        
        if hasattr(medication_record, 'Frequency') and medication_record.Frequency:
            parts.append(f"{medication_record.Frequency}")
        
        return " - ".join(parts)
    
    def get_source_value(self, db, source_record_id):
        # Implement this after confirming logic
        pass