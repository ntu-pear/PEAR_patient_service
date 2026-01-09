import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.config import Config
from app.models.patient_vital_model import PatientVital

from .base_strategy import HighlightStrategy

logger = logging.getLogger(__name__)

class VitalStrategy(HighlightStrategy):
    """Strategy for generating highlights from abnormal vitals"""
    
    # Default clinical baselines for patients with no vital history
    DEFAULT_TEMPERATURE = 37.0       # Normal body temperature (°C)
    DEFAULT_SYSTOLIC_BP = 120        # Normal systolic BP (mmHg)
    DEFAULT_DIASTOLIC_BP = 80        # Normal diastolic BP (mmHg)
    DEFAULT_HEART_RATE = 75          # Normal resting heart rate (bpm)
    DEFAULT_BLOOD_SUGAR = 7.0        # Normal blood sugar (mg/dL)
    DEFAULT_SPO2 = 97                # Normal oxygen saturation (%)
    
    # FOR PATIENTS WITH VITAL HISTORY: Define tolerances for personalized thresholds based on patient vital history
    TEMPERATURE_TOLERANCE = 1.0      # +- 1.0°C from patient's average
    SYSTOLIC_BP_TOLERANCE = 20       # +- 20 mmHg from patient's average
    DIASTOLIC_BP_TOLERANCE = 15      # +- 15 mmHg from patient's average
    HEART_RATE_TOLERANCE = 20        # +- 20 bpm from patient's average
    BLOOD_SUGAR_TOLERANCE = 3.0      # +- 3.0 mg/dL from patient's average
    SPO2_TOLERANCE = 3               # -3% from patient's average
    
    # Minimum number of historical records needed to calculate personalized thresholds
    MIN_RECORDS_FOR_AVERAGE = 2
    
    _db_session: Optional[Session] = None
    
    def _get_default_baselines(self) -> Dict[str, float]:
        """
        Get default clinical baselines for new patients.
        These are normal adult values used when patient has no history.
        """
        return {
            'temperature': self.DEFAULT_TEMPERATURE,
            'systolic_bp': self.DEFAULT_SYSTOLIC_BP,
            'diastolic_bp': self.DEFAULT_DIASTOLIC_BP,
            'heart_rate': self.DEFAULT_HEART_RATE,
            'blood_sugar': self.DEFAULT_BLOOD_SUGAR,
            'spo2': self.DEFAULT_SPO2
        }
    
    def _get_patient_vital_averages(self, db: Session, patient_id: int, current_vital_id: int) -> Optional[Dict[str, float]]:
        """
        Calculate average vital signs for a patient based on their historical records.
        
        CRITICAL: Excludes the current record from calculation!
        
        Args:
            db: Database session
            patient_id: Patient ID
            current_vital_id: Current vital ID to EXCLUDE from calculation
            
        Returns:
            Dict with average values for each vital sign, or None if not enough data
        """
        try:
            # Get all past vitals for this patient (EXCLUDING current one and deleted records)
            past_vitals = db.query(PatientVital).filter(
                PatientVital.PatientId == patient_id,
                PatientVital.Id != current_vital_id,  # ← CRITICAL: Exclude current record
                PatientVital.IsDeleted == '0'
            ).all()
            
            logger.info(f"Patient {patient_id}: Found {len(past_vitals)} past vitals (excluding current ID {current_vital_id})")
            
            # Need at least MIN_RECORDS_FOR_AVERAGE records
            if len(past_vitals) < self.MIN_RECORDS_FOR_AVERAGE:
                logger.info(f"Patient {patient_id} has only {len(past_vitals)} past vitals - will use default clinical baselines (need {self.MIN_RECORDS_FOR_AVERAGE})")
                return None
            
            # Calculate averages (only for non-null values)
            averages = {}
            
            # Temperature
            temps = [v.Temperature for v in past_vitals if v.Temperature is not None]
            if temps:
                avg_temp = sum(temps) / len(temps)
                averages['temperature'] = avg_temp
            
            # Systolic BP
            sys_bps = [v.SystolicBP for v in past_vitals if v.SystolicBP is not None]
            if sys_bps:
                avg_sys = sum(sys_bps) / len(sys_bps)
                averages['systolic_bp'] = avg_sys
            
            # Diastolic BP
            dia_bps = [v.DiastolicBP for v in past_vitals if v.DiastolicBP is not None]
            if dia_bps:
                avg_dia = sum(dia_bps) / len(dia_bps)
                averages['diastolic_bp'] = avg_dia
            
            # Heart Rate
            hrs = [v.HeartRate for v in past_vitals if v.HeartRate is not None]
            if hrs:
                avg_hr = sum(hrs) / len(hrs)
                averages['heart_rate'] = avg_hr
            
            # Blood Sugar Level
            bsls = [v.BloodSugarLevel for v in past_vitals if v.BloodSugarLevel is not None]
            if bsls:
                avg_bsl = sum(bsls) / len(bsls)
                averages['blood_sugar'] = avg_bsl
                            
            # SpO2
            spo2s = [v.SpO2 for v in past_vitals if v.SpO2 is not None]
            if spo2s:
                avg_spo2 = sum(spo2s) / len(spo2s)
                averages['spo2'] = avg_spo2
            
            logger.info(f"Calculated personalized averages for patient {patient_id} from {len(past_vitals)} records")
            return averages
            
        except Exception as e:
            logger.error(f"Error calculating vital averages for patient {patient_id}: {e}", exc_info=True)
            return None
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "VITAL"
    
    def should_generate_highlight(self, source_record: Any, db: Optional[Session] = None) -> bool:
        """
        Determine if vital should be highlighted.
        
        Logic:
        1. If patient has >= 2 past vitals: Use personalized thresholds
        2. If patient has < 2 past vitals: Use default clinical baselines
        3. If db not provided: Use default clinical baselines
        
        Also stores db session for use in generate_highlight_text.
        """
        vital_record = source_record
        
        # Store db session for later use in generate_highlight_text
        self._db_session = db
        
        # Check if we have patient ID
        if not hasattr(vital_record, 'PatientId') or not vital_record.PatientId:
            logger.warning("Vital record has no PatientId - using default baselines")
            baselines = self._get_default_baselines()
        elif db is None:
            logger.warning("No database session provided - using default baselines")
            baselines = self._get_default_baselines()
        else:
            # Try to get patient's historical averages
            averages = self._get_patient_vital_averages(db, vital_record.PatientId, vital_record.Id)
            
            if not averages:
                # New patient - use default baselines
                logger.info(f"Patient {vital_record.PatientId} is new - using default clinical baselines")
                baselines = self._get_default_baselines()
            else:
                # Use personalized averages
                logger.info(f"Patient {vital_record.PatientId} has history - using personalized thresholds")
                baselines = averages
        
        # Check each vital against the baselines
        
        # Temperature check
        if hasattr(vital_record, 'Temperature') and vital_record.Temperature is not None and 'temperature' in baselines:
            baseline_temp = baselines['temperature']
            min_threshold = baseline_temp - self.TEMPERATURE_TOLERANCE
            max_threshold = baseline_temp + self.TEMPERATURE_TOLERANCE
            
            if vital_record.Temperature > max_threshold or vital_record.Temperature < min_threshold:
                logger.info(f"Temperature {vital_record.Temperature}°C outside range [{min_threshold:.1f}, {max_threshold:.1f}]°C")
                return True
        
        # Systolic BP check
        if hasattr(vital_record, 'SystolicBP') and vital_record.SystolicBP is not None and 'systolic_bp' in baselines:
            baseline_sys = baselines['systolic_bp']
            min_threshold = baseline_sys - self.SYSTOLIC_BP_TOLERANCE
            max_threshold = baseline_sys + self.SYSTOLIC_BP_TOLERANCE
            
            if vital_record.SystolicBP > max_threshold or vital_record.SystolicBP < min_threshold:
                logger.info(f"Systolic BP {vital_record.SystolicBP} mmHg outside range [{min_threshold:.0f}, {max_threshold:.0f}] mmHg")
                return True
        
        # Diastolic BP check
        if hasattr(vital_record, 'DiastolicBP') and vital_record.DiastolicBP is not None and 'diastolic_bp' in baselines:
            baseline_dia = baselines['diastolic_bp']
            min_threshold = baseline_dia - self.DIASTOLIC_BP_TOLERANCE
            max_threshold = baseline_dia + self.DIASTOLIC_BP_TOLERANCE
            
            if vital_record.DiastolicBP > max_threshold or vital_record.DiastolicBP < min_threshold:
                logger.info(f"Diastolic BP {vital_record.DiastolicBP} mmHg outside range [{min_threshold:.0f}, {max_threshold:.0f}] mmHg")
                return True
        
        # Heart Rate check
        if hasattr(vital_record, 'HeartRate') and vital_record.HeartRate is not None and 'heart_rate' in baselines:
            baseline_hr = baselines['heart_rate']
            min_threshold = baseline_hr - self.HEART_RATE_TOLERANCE
            max_threshold = baseline_hr + self.HEART_RATE_TOLERANCE
            
            if vital_record.HeartRate > max_threshold or vital_record.HeartRate < min_threshold:
                logger.info(f"Heart Rate {vital_record.HeartRate} bpm outside range [{min_threshold:.0f}, {max_threshold:.0f}] bpm")
                return True
        
        # Blood Sugar Level check
        if hasattr(vital_record, 'BloodSugarLevel') and vital_record.BloodSugarLevel is not None and 'blood_sugar' in baselines:
            baseline_bsl = baselines['blood_sugar']
            min_threshold = baseline_bsl - self.BLOOD_SUGAR_TOLERANCE
            max_threshold = baseline_bsl + self.BLOOD_SUGAR_TOLERANCE
            
            if vital_record.BloodSugarLevel > max_threshold or vital_record.BloodSugarLevel < min_threshold:
                logger.info(f"Blood Sugar {vital_record.BloodSugarLevel} mg/dL outside range [{min_threshold:.1f}, {max_threshold:.1f}] mg/dL")
                return True
        
        # SpO2 check (only check if too low)
        if hasattr(vital_record, 'SpO2') and vital_record.SpO2 is not None and 'spo2' in baselines:
            baseline_spo2 = baselines['spo2']
            min_threshold = baseline_spo2 - self.SPO2_TOLERANCE
            
            if vital_record.SpO2 < min_threshold:
                logger.info(f"SpO2 {vital_record.SpO2}% below threshold {min_threshold:.0f}%")
                return True
        
        logger.info(f"All vitals within acceptable range")
        return False
    
    def generate_highlight_text(self, vital_record) -> str:
        """
        Generate highlight text with specific messages (Fever, Hypertension, etc.).
        
        Uses the db session stored from should_generate_highlight() to get patient's averages or default baselines.
        """
        parts = []
        
        # Get baselines (personalized or default)
        if not hasattr(vital_record, 'PatientId') or not vital_record.PatientId:
            baselines = self._get_default_baselines()
            baseline_source = "normal"
        elif self._db_session is None:
            baselines = self._get_default_baselines()
            baseline_source = "normal"
        else:
            # Try to get patient's averages
            averages = self._get_patient_vital_averages(
                self._db_session, 
                vital_record.PatientId, 
                vital_record.Id
            )
            
            if averages:
                baselines = averages
                baseline_source = "avg"
            else:
                baselines = self._get_default_baselines()
                baseline_source = "normal"
        
        # Temperature with specific message
        if hasattr(vital_record, 'Temperature') and vital_record.Temperature is not None and 'temperature' in baselines:
            temp = vital_record.Temperature
            baseline_temp = baselines['temperature']
            threshold_high = baseline_temp + self.TEMPERATURE_TOLERANCE
            threshold_low = baseline_temp - self.TEMPERATURE_TOLERANCE
            
            if temp > threshold_high:
                parts.append(f"Fever: {temp}°C ({baseline_source}: {baseline_temp:.1f}°C)")
            elif temp < threshold_low:
                parts.append(f"Hypothermia: {temp}°C ({baseline_source}: {baseline_temp:.1f}°C)")
        
        # Blood Pressure with specific message
        if hasattr(vital_record, 'SystolicBP') and vital_record.SystolicBP is not None and 'systolic_bp' in baselines:
            sys = vital_record.SystolicBP
            dia = vital_record.DiastolicBP if hasattr(vital_record, 'DiastolicBP') else None
            
            baseline_sys = baselines['systolic_bp']
            threshold_high_sys = baseline_sys + self.SYSTOLIC_BP_TOLERANCE
            threshold_low_sys = baseline_sys - self.SYSTOLIC_BP_TOLERANCE
            
            if dia is not None and 'diastolic_bp' in baselines:
                baseline_dia = baselines['diastolic_bp']
                threshold_high_dia = baseline_dia + self.DIASTOLIC_BP_TOLERANCE
                threshold_low_dia = baseline_dia - self.DIASTOLIC_BP_TOLERANCE
                
                if sys > threshold_high_sys or dia > threshold_high_dia:
                    parts.append(f"High BP: {sys}/{dia} mmHg ({baseline_source}: {baseline_sys:.0f}/{baseline_dia:.0f})")
                elif sys < threshold_low_sys or dia < threshold_low_dia:
                    parts.append(f"Low BP: {sys}/{dia} mmHg ({baseline_source}: {baseline_sys:.0f}/{baseline_dia:.0f})")
            else:
                # Only systolic available
                if sys > threshold_high_sys:
                    parts.append(f"High BP: {sys} mmHg ({baseline_source}: {baseline_sys:.0f})")
                elif sys < threshold_low_sys:
                    parts.append(f"Low BP: {sys} mmHg ({baseline_source}: {baseline_sys:.0f})")
        
        # Heart Rate with specific message
        if hasattr(vital_record, 'HeartRate') and vital_record.HeartRate is not None and 'heart_rate' in baselines:
            hr = vital_record.HeartRate
            baseline_hr = baselines['heart_rate']
            threshold_high = baseline_hr + self.HEART_RATE_TOLERANCE
            threshold_low = baseline_hr - self.HEART_RATE_TOLERANCE
            
            if hr > threshold_high:
                parts.append(f"Tachycardia: {hr} bpm ({baseline_source}: {baseline_hr:.0f})")
            elif hr < threshold_low:
                parts.append(f"Bradycardia: {hr} bpm ({baseline_source}: {baseline_hr:.0f})")
        
        # Blood Sugar Level with specific message
        if hasattr(vital_record, 'BloodSugarLevel') and vital_record.BloodSugarLevel is not None and 'blood_sugar' in baselines:
            bsl = vital_record.BloodSugarLevel
            baseline_bsl = baselines['blood_sugar']
            threshold_high = baseline_bsl + self.BLOOD_SUGAR_TOLERANCE
            threshold_low = baseline_bsl - self.BLOOD_SUGAR_TOLERANCE
            
            if bsl > threshold_high:
                parts.append(f"Hyperglycemia: {bsl} mg/dL ({baseline_source}: {baseline_bsl:.1f})")
            elif bsl < threshold_low:
                parts.append(f"Hypoglycemia: {bsl} mg/dL ({baseline_source}: {baseline_bsl:.1f})")
        
        # SpO2 with specific message (only low is abnormal)
        if hasattr(vital_record, 'SpO2') and vital_record.SpO2 is not None and 'spo2' in baselines:
            spo2 = vital_record.SpO2
            baseline_spo2 = baselines['spo2']
            threshold_low = baseline_spo2 - self.SPO2_TOLERANCE
            
            if spo2 < threshold_low:
                parts.append(f"Low oxygen: {spo2}% ({baseline_source}: {baseline_spo2:.0f}%)")
        
        # Join all parts
        if parts:
            return ", ".join(parts)
        else:
            return "Abnormal vital signs"
        
    def get_source_remarks(self, db, source_record_id):
        """
        Get VitalRemarks from PATIENT_VITAL table.
        This is what displays in the 'source_remarks' field.
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
            
            # Get patient averages or default baselines
            averages = self._get_patient_vital_averages(db, vital.PatientId, vital.Id)
            
            # Return all vital measurements
            result = {
                "systolic_bp": vital.SystolicBP,
                "diastolic_bp": vital.DiastolicBP,
                "temperature": vital.Temperature,
                "heart_rate": vital.HeartRate,
                "spo2": vital.SpO2,
                "blood_sugar_level": vital.BloodSugarLevel
            }
            
            # Add patient averages or default baselines
            if averages:
                result["patient_averages"] = averages
                result["baseline_source"] = "patient_history"
            else:
                result["default_baselines"] = self._get_default_baselines()
                result["baseline_source"] = "clinical_defaults"
            
            return result
            
        except Exception as e:
            print(f"Error getting vital additional fields: {e}")
            return {}