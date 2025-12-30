from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

from app.config import Config
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
        
        If any vital sign is outside normal ranges, return True.
        """
        # Blood Pressure
        if hasattr(vital_record, 'SystolicBP') and vital_record.SystolicBP:
            if (vital_record.SystolicBP > Config.Vital.SystolicBP.MAX_VALUE or 
                vital_record.SystolicBP < Config.Vital.SystolicBP.MIN_VALUE):
                return True
            if vital_record.SystolicBP == 100:   # Testing
                return True
        
        if hasattr(vital_record, 'DiastolicBP') and vital_record.DiastolicBP:
            if (vital_record.DiastolicBP > Config.Vital.DiastolicBP.MAX_VALUE or 
                vital_record.DiastolicBP < Config.Vital.DiastolicBP.MIN_VALUE):
                return True
        
        # Temperature
        if hasattr(vital_record, 'Temperature') and vital_record.Temperature:
            if (vital_record.Temperature > Config.Vital.Temperature.MAX_VALUE or 
                vital_record.Temperature < Config.Vital.Temperature.MIN_VALUE):
                return True
            if vital_record.Temperature == 37:  # Testing
                return True
        
        # Heart Rate
        if hasattr(vital_record, 'HeartRate') and vital_record.HeartRate:
            if (vital_record.HeartRate > Config.Vital.HeartRate.MAX_VALUE or 
                vital_record.HeartRate < Config.Vital.HeartRate.MIN_VALUE):
                return True
        
        # Blood Sugar Level
        if hasattr(vital_record, 'BloodSugarLevel') and vital_record.BloodSugarLevel:
            if (vital_record.BloodSugarLevel > Config.Vital.BloodSugarLevel.MAX_VALUE or 
                vital_record.BloodSugarLevel < Config.Vital.BloodSugarLevel.MIN_VALUE):
                return True
        
        # Oxygen Saturation
        if hasattr(vital_record, 'SpO2') and vital_record.SpO2:
            if vital_record.SpO2 < Config.Vital.SpO2.MIN_VALUE:
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
                sys_high = sys > Config.Vital.SystolicBP.MAX_VALUE
                sys_low = sys < Config.Vital.SystolicBP.MIN_VALUE
                dia_high = dia > Config.Vital.DiastolicBP.MAX_VALUE
                dia_low = dia < Config.Vital.DiastolicBP.MIN_VALUE
                
                if sys_high or dia_high:
                    parts.append(f"High BP: {sys}/{dia} mmHg")
                elif sys_low or dia_low:
                    parts.append(f"Low BP: {sys}/{dia} mmHg")
        
        # Temperature
        if hasattr(vital_record, 'Temperature') and vital_record.Temperature:
            temp = vital_record.Temperature
            if temp > Config.Vital.Temperature.MAX_VALUE:
                parts.append(f"Fever: {temp}°C")
            elif temp < Config.Vital.Temperature.MIN_VALUE:
                parts.append(f"Low temp: {temp}°C")
        
        # Heart Rate
        if hasattr(vital_record, 'HeartRate') and vital_record.HeartRate:
            hr = vital_record.HeartRate
            if hr > Config.Vital.HeartRate.MAX_VALUE:
                parts.append(f"High HR: {hr} bpm")
            elif hr < Config.Vital.HeartRate.MIN_VALUE:
                parts.append(f"Low HR: {hr} bpm")
        
        # Blood Sugar level
        if hasattr(vital_record, 'BloodSugarLevel') and vital_record.BloodSugarLevel:
            bsl = vital_record.BloodSugarLevel
            if bsl > Config.Vital.BloodSugarLevel.MAX_VALUE:
                parts.append(f"High BSL: {bsl} mg/dL")
            elif bsl < Config.Vital.BloodSugarLevel.MIN_VALUE:
                parts.append(f"Low BSL: {bsl} mg/dL")
        
        # Oxygen Saturation
        if hasattr(vital_record, 'SpO2') and vital_record.SpO2:
            spo2 = vital_record.SpO2
            if spo2 < Config.Vital.SpO2.MIN_VALUE:
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
        
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        """
        Get vital-specific additional fields.
        
        Returns:
        {
            "systolic_bp": 180,
            "diastolic_bp": 110,
            "temperature": 39.5,
            "heart_rate": 120,
            "spo2": 92,
            "blood_sugar_level": 15.5
        }
        """
        try:
            vital = db.query(PatientVital).filter(
                PatientVital.Id == source_record_id
            ).first()
            
            if not vital:
                return {}
            
            # Return all vital measurements
            return {
                "systolic_bp": vital.SystolicBP,
                "diastolic_bp": vital.DiastolicBP,
                "temperature": vital.Temperature,
                "heart_rate": vital.HeartRate,
                "spo2": vital.SpO2,
                "blood_sugar_level": vital.BloodSugarLevel
            }
            
        except Exception as e:
            print(f"Error getting vital additional fields: {e}")
            return {}