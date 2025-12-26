from typing import Optional

from sqlalchemy.orm import Session

from app.models.patient_vital_model import PatientVital

from .base_strategy import HighlightStrategy


class VitalStrategy(HighlightStrategy):
    """Strategy for generating highlights from abnormal vitals (ultra-simplified)"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "VITAL"
    
    def should_generate_highlight(self, vital_record) -> bool:
        """
        Check if vital is abnormal and should generate a highlight.
        
        CUSTOMIZE THIS based on your vital signs structure!
        
        Returns True if ANY of these conditions are met:
        - High or low blood pressure
        - High or low temperature
        - High or low heart rate
        """
        # Blood Pressure - CUSTOMIZE THRESHOLDS
        if hasattr(vital_record, 'SystolicBP') and vital_record.SystolicBP:
            if vital_record.SystolicBP > 140:  # High
                return True
            if vital_record.SystolicBP < 90:   # Low
                return True
            if vital_record.SystolicBP == 100:   # Testing
                return True
        
        if hasattr(vital_record, 'DiastolicBP') and vital_record.DiastolicBP:
            if vital_record.DiastolicBP > 90:  # High
                return True
            if vital_record.DiastolicBP < 60:  # Low
                return True
        
        # Temperature - CUSTOMIZE THRESHOLDS
        if hasattr(vital_record, 'Temperature') and vital_record.Temperature:
            if vital_record.Temperature > 38.0:  # Fever (Celsius)
                return True
            if vital_record.Temperature < 36.0:  # Hypothermia
                return True
            if vital_record.Temperature == 37:  # Testing
                return True
        
        # Heart Rate - CUSTOMIZE THRESHOLDS
        if hasattr(vital_record, 'HeartRate') and vital_record.HeartRate:
            if vital_record.HeartRate > 100:  # Tachycardia
                return True
            if vital_record.HeartRate < 60:   # Bradycardia
                return True
        
        # Blood Sugar Level - CUSTOMIZE THRESHOLDS (optional)
        if hasattr(vital_record, 'BloodSugarLevel') and vital_record.BloodSugarLevel:
            if vital_record.RespiratoryRate > 13:
                return True
            if vital_record.RespiratoryRate < 6:
                return True
        
        # Oxygen Saturation - CUSTOMIZE THRESHOLDS (optional)
        if hasattr(vital_record, 'SpO2') and vital_record.OxygenSaturation:
            if vital_record.OxygenSaturation < 95:  # Low SpO2
                return True
        
        return False
    
    def generate_highlight_text(self, vital_record) -> str:
        """
        Generate readable text for the highlight.
        This is what users will see in the UI.
        """
        parts = []
        
        # Blood Pressure
        if hasattr(vital_record, 'SystolicBP') and hasattr(vital_record, 'DiastolicBP'):
            sys = vital_record.SystolicBP
            dia = vital_record.DiastolicBP
            if sys and dia:
                if sys > 140 or dia > 90:
                    parts.append(f"High BP: {sys}/{dia} mmHg")
                elif sys < 90 or dia < 60:
                    parts.append(f"Low BP: {sys}/{dia} mmHg")
                elif sys == 100 or dia == 80:
                    parts.append(f"Testing for Systolic BP: {sys}/{dia} mmHg")
        
        # Temperature
        if hasattr(vital_record, 'Temperature') and vital_record.Temperature:
            temp = vital_record.Temperature
            if temp > 38.0:
                parts.append(f"Fever: {temp}°C")
            elif temp < 36.0:
                parts.append(f"Low temp: {temp}°C")
            elif temp == 37.0:
                parts.append(f"TESTING TEMPERATURE: {temp}°C")
        
        # Heart Rate
        if hasattr(vital_record, 'HeartRate') and vital_record.HeartRate:
            hr = vital_record.HeartRate
            if hr > 100:
                parts.append(f"High HR: {hr} bpm")
            elif hr < 60:
                parts.append(f"Low HR: {hr} bpm")
        
        # Blood Sugar level
        if hasattr(vital_record, 'BloodSugarLevel') and vital_record.BloodSugarLevel:
            bsl = vital_record.BloodSugarLevel
            if bsl > 13:
                parts.append(f"High BSL: {bsl} mg/dL")
            elif bsl < 6:
                parts.append(f"Low BSL: {bsl} mg/dL")
        
        # Oxygen Saturation
        if hasattr(vital_record, 'SpO2') and vital_record.SpO2:
            spo2 = vital_record.SpO2
            if spo2 < 95:
                parts.append(f"Low SpO2: {spo2}%")
        
        # Join all parts or return generic message
        if parts:
            return ", ".join(parts)
        else:
            return "Abnormal vital signs"
        
    def get_source_value(self, db, source_record_id):
        """
        Get VitalRemarks from PATIENT_VITAL table.
        This is what displays in the 'source_value' field.
        """
        try:
            vital = db.query(PatientVital).filter(
                PatientVital.Id == source_record_id
            ).first()
            
            if vital:
                return vital.VitalRemarks
            return None
            
        except Exception as e:
            print(f"Error getting vital source value: {e}")
            return None