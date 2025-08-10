import pytest
from app.messaging.patient_publisher import PatientPublisher

@pytest.fixture(scope="module")
def publisher():
    # Setup
    pub = PatientPublisher()
    yield pub
    # Teardown: close RabbitMQ connection if available
    try:
        if hasattr(pub, "connection") and pub.connection:
            pub.connection.close()
    except Exception as e:
        print(f"Warning: Failed to close publisher connection: {e}")

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

#def test_publish_patient_updated(publisher):
#    patient_id = 456
#    old_data = {
#        'id': patient_id,
#        'name': 'Jane Smith',
#        'nric': 'S7654321B',
#        'isActive': '1',
#        'startDate': '2024-01-01T00:00:00',
#        'preferredName': 'Janey'
#    }
#    new_data = old_data.copy()
#    new_data['preferredName'] = 'Jane'
#    changes = {'preferredName': {'old': 'Janey', 'new': 'Jane'}}
#    modified_by = "patient_integration_test"
#    result = publisher.publish_patient_updated(patient_id, old_data, new_data, changes, modified_by)
#    assert result is True
#
#def test_publish_patient_deleted(publisher):
#    patient_id = 456
#    patient_data = {
#        'id': patient_id,
#        'name': 'Jane Smith',
#        'nric': 'S7654321B',
#        'isActive': '1',
#        'startDate': '2024-01-01T00:00:00',
#        'preferredName': 'Jane'
#    }
#    deleted_by = "patient_integration_test"
#    result = publisher.publish_patient_deleted(patient_id, patient_data, deleted_by)
#    assert result is True