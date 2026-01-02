import uuid
from datetime import datetime

import pytest
from unittest.mock import patch, MagicMock

from app.messaging.patient_medication_publisher import PatientMedicationPublisher, get_patient_medication_publisher

@pytest.fixture
def mock_producer_manager():
    """Fixture for mocked producer manager"""
    with patch('app.messaging.patient_medication_publisher.get_producer_manager') as mock:
        manager = MagicMock()
        manager.declare_exchange.return_value = None
        manager.publish.return_value = True
        mock.return_value = manager
        yield manager

@pytest.fixture
def sample_patient_medication_data():
    """Sample patient medication data for testing"""
    return {
            'id': 123,
            'isDeleted': '1',
            'patient_id': 1,
            'prescription_list_id': '1',
            'administer_time': '1130',
            'dosage': '1',
            'instruction': 'to take after lunch',
            'startDate': '2024-01-01T00:00:00',
            'endDate': '2024-12-31T23:59:59',
            'prescription_remarks': 'test remarks',
            'created_date_time': '2025-01-01T00:00:00',
            'updated_date_time': '2025-12-31T23:59:59',
        }

def test_init_success(mock_producer_manager):
    """Should initialise with the exchange declaration"""
    publisher = PatientMedicationPublisher(testing=True)

    assert publisher.exchange == 'patient.updates'
    assert publisher.testing is True
    assert publisher.manager is mock_producer_manager
    mock_producer_manager.declare_exchange.assert_called_once_with('patient.updates', 'topic')

def test_init_exchange_declaration_failure(mock_producer_manager):
    """Should handle exchange declaration failure"""
    mock_producer_manager.declare_exchange.side_effect = Exception("Exchange error")

    publisher = PatientMedicationPublisher(testing=True)

    assert publisher.exchange == 'patient.updates'
    assert publisher.manager is mock_producer_manager
    mock_producer_manager.declare_exchange.assert_called_once_with('patient.updates', 'topic')

# ==== publish_patient_medication_created tests ====
@patch('app.messaging.patient_medication_publisher.datetime')
@patch('app.messaging.patient_medication_publisher.uuid.uuid4')
def test_publish_patient_medication_created_success(mock_uuid, mock_datetime, mock_producer_manager, sample_patient_medication_data):
    """Should publish patient created message successfully"""
    # setup mocks
    mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
    fixed_datetime = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_datetime

    publisher = PatientMedicationPublisher(testing=True)

    result = publisher.publish_patient_medication_created(
        medication_id = 100,
        patient_id = 1,
        medication_data = sample_patient_medication_data,
        created_by="user1"
    )

    assert result is True

    expected_message = {
        'correlation_id': '12345678-1234-5678-1234-567812345678',
        'event_type': 'PATIENT_MEDICATION_CREATED',
        'medication_id': 100,
        'patient_id': 1,
        'medication_data': sample_patient_medication_data,
        'created_by': 'user1',
        'timestamp': '2025-01-01T12:00:00'  # ISO format
    }
    mock_producer_manager.publish.assert_called_once_with(
        'patient.updates',
        'patient.medication.created.100',
        expected_message
    )

def test_publish_patient_medication_created_failure(mock_producer_manager, sample_patient_medication_data):
    """Should return False when publish fails"""
    mock_producer_manager.publish.return_value = False

    publisher = PatientMedicationPublisher(testing=True)

    result = publisher.publish_patient_medication_created(
        medication_id=100,
        patient_id=1,
        medication_data=sample_patient_medication_data,
        created_by="user1"
    )

    assert result is False
    mock_producer_manager.publish.assert_called_once()

# ==== publish_patient_medication_updated tests ====
@patch('app.messaging.patient_medication_publisher.datetime')
@patch('app.messaging.patient_medication_publisher.uuid.uuid4')
def test_publish_patient_medication_updated_success(mock_uuid, mock_datetime, mock_producer_manager, sample_patient_medication_data):
    """Should publish patient updated message successfully"""
    # setup mocks
    mock_uuid.return_value = uuid.UUID('11223344-5566-7788-99aa-bbccddeeff00')
    fixed_datetime = datetime(2025, 5, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_datetime

    publisher = PatientMedicationPublisher(testing=True)

    old_data = sample_patient_medication_data
    new_data = {
            'id': 123,
            'isDeleted': '1',
            'patient_id': 100,
            'prescription_list_id': '11',
            'administer_time': '1230',
            'dosage': '2',
            'instruction': 'to take after dinner',
            'startDate': '2024-01-01T00:00:00',
            'endDate': '2024-12-31T23:59:59',
            'prescription_remarks': 'test remarks 1',
            'created_date_time': '2025-01-01T00:00:00',
            'updated_date_time': '2025-12-31T23:59:59',
        }
    changes = {
        'id': {'old': old_data['id'], 'new': new_data['id']},
        'isDeleted': {'old': old_data['isDeleted'], 'new': new_data['isDeleted']},
        'patient_id': {'old': old_data['patient_id'], 'new': new_data['patient_id']},
        'prescription_list_id': {'old': old_data['prescription_list_id'], 'new': new_data['prescription_list_id']},
        'administer_time': {'old': old_data['administer_time'], 'new': new_data['administer_time']},
        'dosage': {'old': old_data['dosage'], 'new': new_data['dosage']},
        'instruction': {'old': old_data['instruction'], 'new': new_data['instruction']},
        'startDate': {'old': old_data['startDate'], 'new': new_data['startDate']},
        'endDate': {'old': old_data['endDate'], 'new': new_data['endDate']},
        'prescription_remarks': {'old': old_data['prescription_remarks']},
        'created_date_time': {'old': old_data['created_date_time'], 'new': new_data['created_date_time']},
        'updated_date_time': {'old': old_data['updated_date_time'], 'new': new_data['updated_date_time']},
    }

    result = publisher.publish_patient_medication_updated(
        medication_id=100,
        patient_id = 100,
        old_data = old_data,
        new_data = new_data,
        changes = changes,
        modified_by="user2"
    )

    assert result is True

    expected_message = {
        'correlation_id': '11223344-5566-7788-99aa-bbccddeeff00',
        'event_type': 'PATIENT_MEDICATION_UPDATED',
        'medication_id': 100,
        'patient_id': 100,
        'old_data': old_data,
        'new_data': new_data,
        'changes': changes,
        'modified_by': 'user2',
        'timestamp': '2025-05-01T12:00:00'  # ISO format
    }
    mock_producer_manager.publish.assert_called_once_with(
        'patient.updates',
        'patient.medication.updated.100',
        expected_message
    )

def test_publish_patient_medication_updated_failure(mock_producer_manager, sample_patient_medication_data):
    """Should return False when publish fails"""
    mock_producer_manager.publish.return_value = False
    publisher = PatientMedicationPublisher(testing=True)
    result = publisher.publish_patient_medication_updated(
        medication_id=100,
        patient_id=100,
        old_data={},
        new_data={},
        changes={},
        modified_by="user2"
    )

    assert result is False
    mock_producer_manager.publish.assert_called_once()

# === publish_patient_medication_deleted tests ===
@patch('app.messaging.patient_medication_publisher.datetime')
@patch('app.messaging.patient_medication_publisher.uuid.uuid4')
def test_publish_patient_medication_deleted_success(mock_uuid, mock_datetime, mock_producer_manager, sample_patient_medication_data):
    """Should publish patient medication deleted message successfully"""
    # mock data
    mock_uuid.return_value = uuid.UUID('11223344-5566-7788-99aa-bbccddeeff00')
    fixed_datetime = datetime(2025, 5, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_datetime

    publisher = PatientMedicationPublisher(testing=True)
    result = publisher.publish_patient_medication_deleted(
        medication_id=100,
        patient_id=1,
        medication_data=sample_patient_medication_data,
        deleted_by="user3"
    )
    assert result is True
    expected_message = {
        'correlation_id': '11223344-5566-7788-99aa-bbccddeeff00',
        'event_type': 'PATIENT_MEDICATION_DELETED',
        'medication_id': 100,
        'patient_id': 1,
        'medication_data': sample_patient_medication_data,
        'deleted_by': 'user3',
        'timestamp': '2025-05-01T12:00:00'
    }
    mock_producer_manager.publish.assert_called_once_with(
        'patient.updates',
        'patient.medication.deleted.100',
        expected_message
    )

def test_publish_patient_medication_deleted_failure(mock_producer_manager, sample_patient_medication_data):
    """Should return False when publish fails"""
    mock_producer_manager.publish.return_value = False

    publisher = PatientMedicationPublisher(testing=True)
    result = publisher.publish_patient_medication_deleted(
        medication_id=100,
        patient_id=100,
        medication_data=sample_patient_medication_data,
        deleted_by="user3"
    )
    assert result is False
    mock_producer_manager.publish.assert_called_once()

# ==== close method test ====
def test_close(mock_producer_manager):
    """Close should be a no-op"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.close()  # Should do nothing and not raise

# ==== Singleton instance tests ====
def test_get_patient_medication_publisher_singleton(mock_producer_manager):
    """Should return singleton instance on multiple calls"""

    instance1 = get_patient_medication_publisher(testing=True)
    instance2 = get_patient_medication_publisher(testing=True)

    assert instance1 is instance2
    assert isinstance(instance1, PatientMedicationPublisher)
    mock_producer_manager.declare_exchange.assert_called_once_with('patient.updates', 'topic')


#  ==== routing key format tests ====
def test_created_routing_key_format(mock_producer_manager, sample_patient_medication_data):
    """Should use correct routing key format for created event"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.publish_patient_medication_created(
        medication_id=100,
        patient_id=100,
        medication_data=sample_patient_medication_data,
        created_by="user1"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    assert args[1] == 'patient.medication.created.100'

def test_updated_routing_key_format(mock_producer_manager, sample_patient_medication_data):
    """Should use correct routing key format for updated event"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.publish_patient_medication_updated(
        medication_id=100,
        patient_id=100,
        old_data=sample_patient_medication_data,
        new_data=sample_patient_medication_data,
        changes={},
        modified_by="user2"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    assert args[1] == 'patient.medication.updated.100'

def test_deleted_routing_key_format(mock_producer_manager, sample_patient_medication_data):
    """Should use correct routing key format for deleted event"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.publish_patient_medication_deleted(
        medication_id=100,
        patient_id=100,
        medication_data=sample_patient_medication_data,
        deleted_by="user3"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    assert args[1] == 'patient.medication.deleted.100'

# === Message content structure tests === #
def test_created_message_structure(mock_producer_manager, sample_patient_medication_data):
    """Should construct correct message structure for created event"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.publish_patient_medication_created(
        medication_id=100,
        patient_id=100,
        medication_data=sample_patient_medication_data,
        created_by="user1"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    message = args[2]
    required_fields = [
        'correlation_id', 'event_type', 'medication_id', 'patient_id', 'medication_data', 'created_by', 'timestamp'
    ]

    for field in required_fields:
        assert field in message
    assert message['event_type'] == 'PATIENT_MEDICATION_CREATED'

def test_updated_message_structure(mock_producer_manager, sample_patient_medication_data):
    """Should construct correct message structure for updated event"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.publish_patient_medication_updated(
        medication_id=100,
        patient_id=100,
        old_data={},
        new_data={},
        changes={},
        modified_by="user2"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    message = args[2]
    required_fields = [
        'correlation_id', 'event_type', 'medication_id', 'patient_id', 'old_data', 'new_data', 'changes', 'modified_by', 'timestamp'
    ]

    for field in required_fields:
        assert field in message
    assert message['event_type'] == 'PATIENT_MEDICATION_UPDATED'

def test_deleted_message_structure(mock_producer_manager, sample_patient_medication_data):
    """Should construct correct message structure for deleted event"""
    publisher = PatientMedicationPublisher(testing=True)
    publisher.publish_patient_medication_deleted(
        medication_id=100,
        patient_id=100,
        medication_data=sample_patient_medication_data,
        deleted_by="user3"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    message = args[2]
    required_fields = [
        'correlation_id', 'event_type', 'medication_id','patient_id', 'medication_data', 'deleted_by', 'timestamp'
    ]
    for field in required_fields:
        assert field in message
    assert message['event_type'] == 'PATIENT_MEDICATION_DELETED'