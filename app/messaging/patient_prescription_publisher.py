import logging
from datetime import datetime
from typing import Any, Dict

from .producer_manager import get_producer_manager

logger = logging.getLogger(__name__)


class PatientPrescriptionPublisher:
    """Publisher for Patient Service events"""

    def __init__(self, testing: bool = False):
        self.manager = get_producer_manager(testing=testing)
        self.exchange = "patient_prescription.updates"
        self.testing = testing

        # Declare the exchange
        try:
            self.manager.declare_exchange(self.exchange, "topic")
            logger.info("Patient publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize patient publisher: {str(e)}")

    def publish_patient_prescription_created(
        self,
        patient_prescription_id: int,
        patient_prescription_data: Dict[str, Any],
        created_by: str,
    ) -> bool:
        """Publish patient prescription creation event"""
        message = {
            "event_type": "PATIENT_PRESCRIPTION_CREATED",
            "patient_prescription_id": patient_prescription_id,
            "patient_prescription_data": patient_prescription_data,
            "created_by": created_by,
            "timestamp": datetime.utcnow().isoformat(),
        }

        routing_key = f"patient_prescription.created.{patient_prescription_id}"
        success = self.manager.publish(self.exchange, routing_key, message)

        if success:
            logger.info(
                f"Published PATIENT_PRESCRIPTION_CREATED event for patient {patient_prescription_id}"
            )
        else:
            logger.error(
                f"Failed to publish PATIENT_PRESCRIPTION_CREATED event for patient {patient_prescription_id}"
            )

        return success

    # TODO: Implement update and delete event publishing methods for patient prescriptions
    def publish_patient_updated(
        self,
        patient_id: int,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        changes: Dict[str, Any],
        modified_by: str,
    ) -> bool:
        """Publish patient update event"""
        message = {
            "event_type": "PATIENT_UPDATED",
            "patient_id": patient_id,
            "old_data": old_data,
            "new_data": new_data,
            "changes": changes,
            "modified_by": modified_by,
            "timestamp": datetime.utcnow().isoformat(),
        }

        routing_key = f"patient.updated.{patient_id}"
        success = self.manager.publish(self.exchange, routing_key, message)

        if success:
            logger.info(f"Published PATIENT_UPDATED event for patient {patient_id}")
        else:
            logger.error(
                f"Failed to publish PATIENT_UPDATED event for patient {patient_id}"
            )

        return success

    # TODO: Implement update and delete event publishing methods for patient prescriptions
    def publish_patient_deleted(
        self, patient_id: int, patient_data: Dict[str, Any], deleted_by: str
    ) -> bool:
        """Publish patient deletion event"""
        message = {
            "event_type": "PATIENT_DELETED",
            "patient_id": patient_id,
            "patient_data": patient_data,
            "deleted_by": deleted_by,
            "timestamp": datetime.utcnow().isoformat(),
        }

        routing_key = f"patient.deleted.{patient_id}"
        success = self.manager.publish(self.exchange, routing_key, message)

        if success:
            logger.info(f"Published PATIENT_DELETED event for patient {patient_id}")
        else:
            logger.error(
                f"Failed to publish PATIENT_DELETED event for patient {patient_id}"
            )

        return success

    def close(self):
        """Close is handled by the producer manager"""
        # No need to close individual publishers
        # The producer manager handles the connection
        pass


# Singleton instance
_patient_prescription_publisher = None


def get_patient_prescription_publisher(
    testing: bool = False,
) -> PatientPrescriptionPublisher:
    """Get or create the singleton patient publisher instance"""
    global _patient_prescription_publisher
    if _patient_prescription_publisher is None:
        _patient_prescription_publisher = PatientPrescriptionPublisher(testing=testing)
    return _patient_prescription_publisher


# Usage examples and testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Patient Service Usage: python patient_publisher.py test")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    if sys.argv[1] == "test":
        # Test publisher
        publisher = _patient_prescription_publisher(testing=True)

        # Test data
        # TODO: Change testing data from patient to patient_prescription columns
        test_patient_data = {
            "id": 123,
            "name": "John Doe",
            "nric": "S1234567A",
            "isActive": "1",
            "startDate": "2024-01-01T00:00:00",
            "preferredName": "Johnny",
        }

        # Test publishing events
        publisher.publish_patient_prescription_created(
            123, test_patient_data, "test_user"
        )

        updated_data = test_patient_data.copy()
        updated_data["preferredName"] = "John"

        publisher.publish_patient_updated(
            123,
            test_patient_data,
            updated_data,
            {"preferredName": {"old": "Johnny", "new": "John"}},
            "test_user",
        )

        publisher.publish_patient_deleted(123, test_patient_data, "test_user")

        publisher.close()
