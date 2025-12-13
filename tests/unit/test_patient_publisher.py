import uuid
from datetime import datetime

import pytest
from unittest.mock import patch, MagicMock


from app.messaging.patient_publisher import PatientPublisher

@pytest.fixture
def mock_producer_manager():
    """Fixture for mocked producer manager"""
    with patch('app.messaging.patient_publisher.get_producer_manager') as mock:
        manager = MagicMock()
        manager.declare_exchange.return_value = None
        manager.publish.return_value = True
        mock.return_value = manager
        yield manager

@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
            'id': 123,
            'name': 'John Doe',
            'nric': 'S1234567A',
            'isActive': '1',
            'startDate': '2024-01-01T00:00:00',
            'preferredName': 'Johnny'
        }

def test_init_success(mock_producer_manager):
    """Should initialise with the exchange declaration"""
    publisher = PatientPublisher(testing=True)

    assert publisher.exchange == 'patient.updates'
    assert publisher.testing is True
    assert publisher.manager is mock_producer_manager
    mock_producer_manager.declare_exchange.assert_called_once_with('patient.updates', 'topic')

def test_init_exchange_declaration_failure(mock_producer_manager):
    """Should handle exchange declaration failure"""
    mock_producer_manager.declare_exchange.side_effect = Exception("Exchange error")

    publisher = PatientPublisher(testing=True)

    assert publisher.exchange == 'patient.updates'
    assert publisher.manager is mock_producer_manager
    mock_producer_manager.declare_exchange.assert_called_once_with('patient.updates', 'topic')

# ==== publish_patient_created tests ====
@patch('app.messaging.patient_publisher.datetime')
@patch('app.messaging.patient_publisher.uuid.uuid4')
def test_publish_patient_created_success(mock_uuid, mock_datetime, mock_producer_manager, sample_patient_data):
    """Should publish patient created message successfully"""
    # setup mocks
    mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
    fixed_datetime = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_datetime

    publisher = PatientPublisher(testing=True)

    result = publisher.publish_patient_created(
        patient_id = 100,
        patient_data = sample_patient_data,
        created_by="user1"
    )

    assert result is True

    expected_message = {
        'correlation_id': '12345678-1234-5678-1234-567812345678',
        'event_type': 'PATIENT_CREATED',
        'patient_id': 100,
        'patient_data': sample_patient_data,
        'created_by': 'user1',
        'timestamp': '2025-01-01T12:00:00'  # ISO format
    }
    mock_producer_manager.publish.assert_called_once_with(
        'patient.updates',
        'patient.created.100',
        expected_message
    )

def test_publish_patient_created_failure(mock_producer_manager, sample_patient_data):
    """Should return False when publish fails"""
    mock_producer_manager.publish.return_value = False

    publisher = PatientPublisher(testing=True)

    result = publisher.publish_patient_created(
        patient_id=100,
        patient_data=sample_patient_data,
        created_by="user1"
    )

    assert result is False
    mock_producer_manager.publish.assert_called_once()

# ==== publish_patient_updated tests ====
@patch('app.messaging.patient_publisher.datetime')
@patch('app.messaging.patient_publisher.uuid.uuid4')
def test_publish_patient_updated_success(mock_uuid, mock_datetime, mock_producer_manager, sample_patient_data):
    """Should publish patient updated message successfully"""
    # setup mocks
    mock_uuid.return_value = uuid.UUID('11223344-5566-7788-99aa-bbccddeeff00')
    fixed_datetime = datetime(2025, 5, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_datetime

    publisher = PatientPublisher(testing=True)

    old_data = sample_patient_data
    new_data = {
            'id': 1,
            'name': 'Johnny',
            'nric': 'T1020304L',
            'isActive': '1',
            'startDate': '2025-01-01T00:00:00',
            'preferredName': 'Howard'
        }
    changes = {
        'id': {'old': old_data['id'], 'new': new_data['id']},
        'name': {'old': old_data['name'], 'new': new_data['name']},
        'nric': {'old': old_data['nric'], 'new': new_data['nric']},
        'isActive': {'old': old_data['isActive'], 'new': new_data['isActive']},
        'startDate': {'old': old_data['startDate'], 'new': new_data['startDate']},
        'preferredName': {'old': old_data['preferredName'], 'new': new_data['preferredName']}
    }

    result = publisher.publish_patient_updated(
        patient_id = 100,
        old_data = old_data,
        new_data = new_data,
        changes = changes,
        modified_by="user2"
    )

    assert result is True

    expected_message = {
        'correlation_id': '11223344-5566-7788-99aa-bbccddeeff00',
        'event_type': 'PATIENT_UPDATED',
        'patient_id': 100,
        'old_data': old_data,
        'new_data': new_data,
        'changes': changes,
        'modified_by': 'user2',
        'timestamp': '2025-05-01T12:00:00'  # ISO format
    }
    mock_producer_manager.publish.assert_called_once_with(
        'patient.updates',
        'patient.updated.100',
        expected_message
    )

def test_publish_patient_updated_failure(mock_producer_manager, sample_patient_data):
    """Should return False when publish fails"""
    mock_producer_manager.publish.return_value = False
    publisher = PatientPublisher(testing=True)
    result = publisher.publish_patient_updated(
        patient_id=100,
        old_data={},
        new_data={},
        changes={},
        modified_by="user2"
    )

    assert result is False
    mock_producer_manager.publish.assert_called_once()

# === publish_patient_deleted tests ===
@patch('app.messaging.patient_publisher.datetime')
@patch('app.messaging.patient_publisher.uuid.uuid4')
def test_publish_patient_deleted_success(mock_uuid, mock_datetime, mock_producer_manager, sample_patient_data):
    """Should publish patient deleted message successfully"""
    # mock data
    mock_uuid.return_value = uuid.UUID('11223344-5566-7788-99aa-bbccddeeff00')
    fixed_datetime = datetime(2025, 5, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_datetime

    publisher = PatientPublisher(testing=True)
    result = publisher.publish_patient_deleted(
        patient_id=100,
        patient_data=sample_patient_data,
        deleted_by="user3"
    )
    assert result is True
    expected_message = {
        'correlation_id': '11223344-5566-7788-99aa-bbccddeeff00',
        'event_type': 'PATIENT_DELETED',
        'patient_id': 100,
        'patient_data': sample_patient_data,
        'deleted_by': 'user3',
        'timestamp': '2025-05-01T12:00:00'
    }
    mock_producer_manager.publish.assert_called_once_with(
        'patient.updates',
        'patient.deleted.100',
        expected_message
    )

def test_publish_patient_deleted_failure(mock_producer_manager, sample_patient_data):
    """Should return False when publish fails"""
    mock_producer_manager.publish.return_value = False

    publisher = PatientPublisher(testing=True)
    result = publisher.publish_patient_deleted(
        patient_id=100,
        patient_data=sample_patient_data,
        deleted_by="user3"
    )
    assert result is False
    mock_producer_manager.publish.assert_called_once()

# ==== close method test ====
def test_close(mock_producer_manager):
    """Close should be a no-op"""
    publisher = PatientPublisher(testing=True)
    publisher.close()  # Should do nothing and not raise

#  ==== routing key format tests ====
def test_created_routing_key_format(mock_producer_manager, sample_patient_data):
    """Should use correct routing key format for created event"""
    publisher = PatientPublisher(testing=True)
    publisher.publish_patient_created(
        patient_id=100,
        patient_data=sample_patient_data,
        created_by="user1"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    assert args[1] == 'patient.created.100'

def test_updated_routing_key_format(mock_producer_manager, sample_patient_data):
    """Should use correct routing key format for updated event"""
    publisher = PatientPublisher(testing=True)
    publisher.publish_patient_updated(
        patient_id=100,
        old_data=sample_patient_data,
        new_data=sample_patient_data,
        changes={},
        modified_by="user2"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    assert args[1] == 'patient.updated.100'

def test_deleted_routing_key_format(mock_producer_manager, sample_patient_data):
    """Should use correct routing key format for deleted event"""
    publisher = PatientPublisher(testing=True)
    publisher.publish_patient_deleted(
        patient_id=100,
        patient_data=sample_patient_data,
        deleted_by="user3"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    assert args[1] == 'patient.deleted.100'

# === Message content structure tests === #
def test_created_message_structure(mock_producer_manager, sample_patient_data):
    """Should construct correct message structure for created event"""
    publisher = PatientPublisher(testing=True)
    publisher.publish_patient_created(
        patient_id=100,
        patient_data=sample_patient_data,
        created_by="user1"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    message = args[2]
    required_fields = [
        'correlation_id', 'event_type', 'patient_id', 'patient_data', 'created_by', 'timestamp'
    ]

    for field in required_fields:
        assert field in message
    assert message['event_type'] == 'PATIENT_CREATED'

def test_updated_message_structure(mock_producer_manager, sample_patient_data):
    """Should construct correct message structure for updated event"""
    publisher = PatientPublisher(testing=True)
    publisher.publish_patient_updated(
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
        'correlation_id', 'event_type', 'patient_id', 'old_data', 'new_data', 'changes', 'modified_by', 'timestamp'
    ]

    for field in required_fields:
        assert field in message
    assert message['event_type'] == 'PATIENT_UPDATED'

def test_deleted_message_structure(mock_producer_manager, sample_patient_data):
    """Should construct correct message structure for deleted event"""
    publisher = PatientPublisher(testing=True)
    publisher.publish_patient_deleted(
        patient_id=100,
        patient_data=sample_patient_data,
        deleted_by="user3"
    )
    mock_producer_manager.publish.assert_called_once()
    args, kwargs = mock_producer_manager.publish.call_args
    message = args[2]
    required_fields = [
        'correlation_id', 'event_type', 'patient_id', 'patient_data', 'deleted_by', 'timestamp'
    ]
    for field in required_fields:
        assert field in message
    assert message['event_type'] == 'PATIENT_DELETED'