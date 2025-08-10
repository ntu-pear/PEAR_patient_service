import pytest
import threading
import sys
import time

from app.messaging.patient_publisher import PatientPublisher

@pytest.fixture(scope="module")
def publisher():
    return PatientPublisher()

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
    # Give any async cleanup a moment
    time.sleep(0.5)

    print("\n=== DEBUG: Active non-daemon threads ===")
    for t in threading.enumerate():
        if t.is_alive() and not t.daemon:
            print(f"Thread: {t.name} | {t}")
    print("========================================\n")
    sys.stdout.flush()
