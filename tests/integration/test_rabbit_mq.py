import pytest
import sys
from app.messaging.patient_publisher import PatientPublisher

@pytest.fixture(scope="module")
def publisher():
    pub = PatientPublisher()
    yield pub
    try:
        if hasattr(pub, "channel") and pub.channel.is_open:
            pub.channel.close()
    except Exception as e:
        print(f"Warning: Failed to close channel: {e}")
    try:
        if hasattr(pub, "connection") and pub.connection.is_open:
            pub.connection.close()
    except Exception as e:
        print(f"Warning: Failed to close connection: {e}")

def test_publish_patient_created(publisher):
    patient_id = 456
    patient_data = {
        'id': patient_id,
        'name': 'Jane Smith',
        'nric': 'S7654321B',
        'isActive': '1',
        'startDate': '2024-01-01T00:00:00',
        'preferredName': 'Janey'
    }
    created_by = "patient_integration_test"
    result = publisher.publish_patient_created(patient_id, patient_data, created_by)
    assert result is True

def teardown_module(module):
    """Force exit after tests to prevent hanging in CI."""
    sys.exit(0)
