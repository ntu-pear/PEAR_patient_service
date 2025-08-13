import logging
from typing import Dict, Any
from datetime import datetime

from .producer_manager import get_producer_manager

logger = logging.getLogger(__name__)

class PatientPublisher:
    """Publisher for Patient Service events"""
    
    def __init__(self, testing: bool = False):
        self.manager = get_producer_manager(testing=testing)
        self.exchange = 'patient.updates'
        self.testing = testing
        
        # Declare the exchange
        try:
            self.manager.declare_exchange(self.exchange, 'topic')
            logger.info("Patient publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize patient publisher: {str(e)}")
    
    def publish_patient_created(self, patient_id: int, patient_data: Dict[str, Any], 
                              created_by: str) -> bool:
        """Publish patient creation event"""
        message = {
            'event_type': 'PATIENT_CREATED',
            'patient_id': patient_id,
            'patient_data': patient_data,
            'created_by': created_by,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        routing_key = f"patient.created.{patient_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_CREATED event for patient {patient_id}")
        else:
            logger.error(f"Failed to publish PATIENT_CREATED event for patient {patient_id}")
            
        return success
    
    def publish_patient_updated(self, patient_id: int, old_data: Dict[str, Any], 
                              new_data: Dict[str, Any], changes: Dict[str, Any],
                              modified_by: str) -> bool:
        """Publish patient update event"""
        message = {
            'event_type': 'PATIENT_UPDATED',
            'patient_id': patient_id,
            'old_data': old_data,
            'new_data': new_data,
            'changes': changes,
            'modified_by': modified_by,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        routing_key = f"patient.updated.{patient_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_UPDATED event for patient {patient_id}")
        else:
            logger.error(f"Failed to publish PATIENT_UPDATED event for patient {patient_id}")
            
        return success
    
    def publish_patient_deleted(self, patient_id: int, patient_data: Dict[str, Any],
                              deleted_by: str) -> bool:
        """Publish patient deletion event"""
        message = {
            'event_type': 'PATIENT_DELETED',
            'patient_id': patient_id,
            'patient_data': patient_data,
            'deleted_by': deleted_by,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        routing_key = f"patient.deleted.{patient_id}"
        success = self.manager.publish(self.exchange, routing_key, message)
        
        if success:
            logger.info(f"Published PATIENT_DELETED event for patient {patient_id}")
        else:
            logger.error(f"Failed to publish PATIENT_DELETED event for patient {patient_id}")
            
        return success
    
    def close(self):
        """Close is handled by the producer manager"""
        # No need to close individual publishers
        # The producer manager handles the connection
        pass


# Singleton instance
_patient_publisher = None

def get_patient_publisher(testing: bool =False) -> PatientPublisher:
    """Get or create the singleton patient publisher instance"""
    global _patient_publisher
    if _patient_publisher is None:
        _patient_publisher = PatientPublisher(testing=testing)
    return _patient_publisher


# Usage examples and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Patient Service Usage: python patient_publisher.py test")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1] == "test":
        # Test publisher
        publisher = PatientPublisher(testing=True)
        
        # Test data
        test_patient_data = {
            'id': 123,
            'name': 'John Doe',
            'nric': 'S1234567A',
            'isActive': '1',
            'startDate': '2024-01-01T00:00:00',
            'preferredName': 'Johnny'
        }
        
        # Test publishing events
        publisher.publish_patient_created(123, test_patient_data, "test_user")
        
        updated_data = test_patient_data.copy()
        updated_data['preferredName'] = 'John'
        
        publisher.publish_patient_updated(
            123, 
            test_patient_data, 
            updated_data, 
            {'preferredName': {'old': 'Johnny', 'new': 'John'}}, 
            "test_user"
        )
        
        publisher.publish_patient_deleted(123, test_patient_data, "test_user")
        
        publisher.close()
