import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from .producer_manager import get_producer_manager

logger = logging.getLogger(__name__)

class PatientAllocationPublisher:
    """Publisher for Patient Allocation Service events"""
    
    def __init__(self, testing: bool = False):
        self.manager = get_producer_manager(testing=testing)
        self.exchange = 'patient.updates'
        self.testing = testing
        
        # Declare the exchange
        try:
            self.manager.declare_exchange(self.exchange, 'topic')
            logger.info("Patient allocation publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize patient allocation publisher: {str(e)}")
    
    def publish_patient_allocation_created(self, allocation_id: int, patient_id: int, 
                                         allocation_data: Dict[str, Any], created_by: str) -> bool:
        """Publish patient allocation creation event"""
        message = {
            'correlation_id': str(uuid.uuid4()),
            'event_type': 'PATIENT_ALLOCATION_CREATED',
            'allocation_id': allocation_id,
            'patient_id': patient_id,
            'allocation_data': allocation_data,
            'created_by': created_by,
            'timestamp': datetime.now().isoformat()
        }
        
        routing_key = f"patient.allocation.created.{allocation_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_ALLOCATION_CREATED event for allocation {allocation_id} (Patient: {patient_id})")
        else:
            logger.error(f"Failed to publish PATIENT_ALLOCATION_CREATED event for allocation {allocation_id}")
            
        return success
    
    def publish_patient_allocation_updated(self, allocation_id: int, patient_id: int,
                                         old_data: Dict[str, Any], new_data: Dict[str, Any], 
                                         changes: Dict[str, Any], modified_by: str) -> bool:
        """Publish patient allocation update event"""
        message = {
            'correlation_id': str(uuid.uuid4()),
            'event_type': 'PATIENT_ALLOCATION_UPDATED',
            'allocation_id': allocation_id,
            'patient_id': patient_id,
            'old_data': old_data,
            'new_data': new_data,
            'changes': changes,
            'modified_by': modified_by,
            'timestamp': datetime.now().isoformat()
        }
        
        routing_key = f"patient.allocation.updated.{allocation_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_ALLOCATION_UPDATED event for allocation {allocation_id} (Patient: {patient_id})")
        else:
            logger.error(f"Failed to publish PATIENT_ALLOCATION_UPDATED event for allocation {allocation_id}")
            
        return success
    
    def publish_patient_allocation_deleted(self, allocation_id: int, patient_id: int,
                                         allocation_data: Dict[str, Any], deleted_by: str) -> bool:
        """Publish patient allocation deletion event"""
        message = {
            'correlation_id': str(uuid.uuid4()),
            'event_type': 'PATIENT_ALLOCATION_DELETED',
            'allocation_id': allocation_id,
            'patient_id': patient_id,
            'allocation_data': allocation_data,
            'deleted_by': deleted_by,
            'timestamp': datetime.now().isoformat()
        }
        
        routing_key = f"patient.allocation.deleted.{allocation_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_ALLOCATION_DELETED event for allocation {allocation_id} (Patient: {patient_id})")
        else:
            logger.error(f"Failed to publish PATIENT_ALLOCATION_DELETED event for allocation {allocation_id}")
            
        return success
    
    def close(self):
        """Close is handled by the producer manager"""
        # No need to close individual publishers
        # The producer manager handles the connection
        pass


# Singleton instance
_patient_allocation_publisher = None

def get_patient_allocation_publisher(testing: bool = False) -> PatientAllocationPublisher:
    """Get or create the singleton patient allocation publisher instance"""
    global _patient_allocation_publisher
    if _patient_allocation_publisher is None:
        _patient_allocation_publisher = PatientAllocationPublisher(testing=testing)
    return _patient_allocation_publisher
