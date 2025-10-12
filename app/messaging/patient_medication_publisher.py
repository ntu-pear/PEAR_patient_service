import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from .producer_manager import get_producer_manager

logger = logging.getLogger(__name__)

class PatientMedicationPublisher:
    """Publisher for Patient Medication Service events"""
    
    def __init__(self, testing: bool = False):
        self.manager = get_producer_manager(testing=testing)
        self.exchange = 'patient.updates'
        self.testing = testing
        
        # Declare the exchange
        try:
            self.manager.declare_exchange(self.exchange, 'topic')
            logger.info("Patient medication publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize patient medication publisher: {str(e)}")
    
    def publish_patient_medication_created(self, medication_id: int, patient_id: int, 
                                         medication_data: Dict[str, Any], created_by: str) -> bool:
        """Publish patient medication creation event"""
        message = {
            'correlation_id': str(uuid.uuid4()),
            'event_type': 'PATIENT_MEDICATION_CREATED',
            'medication_id': medication_id,
            'patient_id': patient_id,
            'medication_data': medication_data,
            'created_by': created_by,
            'timestamp': datetime.now().isoformat()
        }
        
        routing_key = f"patient.medication.created.{medication_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_MEDICATION_CREATED event for medication {medication_id} (Patient: {patient_id})")
        else:
            logger.error(f"Failed to publish PATIENT_MEDICATION_CREATED event for medication {medication_id}")
            
        return success
    
    def publish_patient_medication_updated(self, medication_id: int, patient_id: int,
                                         old_data: Dict[str, Any], new_data: Dict[str, Any], 
                                         changes: Dict[str, Any], modified_by: str) -> bool:
        """Publish patient medication update event"""
        message = {
            'correlation_id': str(uuid.uuid4()),
            'event_type': 'PATIENT_MEDICATION_UPDATED',
            'medication_id': medication_id,
            'patient_id': patient_id,
            'old_data': old_data,
            'new_data': new_data,
            'changes': changes,
            'modified_by': modified_by,
            'timestamp': datetime.now().isoformat()
        }
        
        routing_key = f"patient.medication.updated.{medication_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_MEDICATION_UPDATED event for medication {medication_id} (Patient: {patient_id})")
        else:
            logger.error(f"Failed to publish PATIENT_MEDICATION_UPDATED event for medication {medication_id}")
            
        return success
    
    def publish_patient_medication_deleted(self, medication_id: int, patient_id: int,
                                         medication_data: Dict[str, Any], deleted_by: str) -> bool:
        """Publish patient medication deletion event"""
        message = {
            'correlation_id': str(uuid.uuid4()),
            'event_type': 'PATIENT_MEDICATION_DELETED',
            'medication_id': medication_id,
            'patient_id': patient_id,
            'medication_data': medication_data,
            'deleted_by': deleted_by,
            'timestamp': datetime.now().isoformat()
        }
        
        routing_key = f"patient.medication.deleted.{medication_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_MEDICATION_DELETED event for medication {medication_id} (Patient: {patient_id})")
        else:
            logger.error(f"Failed to publish PATIENT_MEDICATION_DELETED event for medication {medication_id}")
            
        return success
    
    def close(self):
        """Close is handled by the producer manager"""
        # No need to close individual publishers
        # The producer manager handles the connection
        pass


# Singleton instance
_patient_medication_publisher = None

def get_patient_medication_publisher(testing: bool = False) -> PatientMedicationPublisher:
    """Get or create the singleton patient medication publisher instance"""
    global _patient_medication_publisher
    if _patient_medication_publisher is None:
        _patient_medication_publisher = PatientMedicationPublisher(testing=testing)
    return _patient_medication_publisher