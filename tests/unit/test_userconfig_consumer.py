"""
Unit tests for UserConsumer (patient service).
"""

import uuid
from datetime import datetime
from contextlib import contextmanager
from unittest.mock import MagicMock, patch, call

import pytest

from app.models.processed_events_model import MessageProcessingResult


def make_created_message(userconfig_id=1, correlation_id=None):
    return {
        'timestamp': datetime.now().isoformat(),
        'source_service': 'user-service',
        'data': {
            'correlation_id': correlation_id or str(uuid.uuid4()).upper(),
            'event_type': 'USERCONFIG_CREATED',
            'userconfig_id': userconfig_id,
            'userconfig_data': {
                'id': userconfig_id,
                'configBlob': {'SESSION_EXPIRE_MINUTES': 10, 'MAX_PATIENT_PHOTO': 10, 'MAX_ITEMS_TO_RETURN': 40},
                'modifiedDate': '2025-01-01T00:00:00',
                'modifiedById': 'test-user',
            },
            'created_by': 'test-user',
        },
    }


def make_updated_message(userconfig_id=1, correlation_id=None):
    return {
        'timestamp': datetime.now().isoformat(),
        'source_service': 'user-service',
        'data': {
            'correlation_id': correlation_id or str(uuid.uuid4()).upper(),
            'event_type': 'USERCONFIG_UPDATED',
            'userconfig_id': userconfig_id,
            'new_data': {
                'id': userconfig_id,
                'configBlob': {'SESSION_EXPIRE_MINUTES': 20, 'MAX_PATIENT_PHOTO': 20, 'MAX_ITEMS_TO_RETURN': 80},
                'modifiedDate': '2025-06-01T00:00:00',
                'modifiedById': 'test-user',
            },
            'old_data': {},
            'changes': {},
            'modified_by': 'test-user',
        },
    }



@pytest.fixture
def user_consumer():
    """
    UserConsumer with ALL external dependencies mocked.

    We patch:
      - RabbitMQClient → no real connection
      - CRUD imports    → return sensible defaults; individual tests override as needed
      - mapper imports  → return sensible defaults
      - get_db          → yields a MagicMock session
    """
    mock_db = MagicMock()

    @contextmanager
    def fake_get_db():
        yield mock_db

    with patch('app.messaging.user_configuration_consumer.RabbitMQClient'):
        # Patch the module-level imports that __init__ resolves
        with patch('app.crud.ref_user_crud.create_ref_userconfig') as mock_create, \
             patch('app.crud.ref_user_crud.update_ref_userconfig') as mock_update, \
             patch('app.crud.ref_user_crud.is_event_already_processed') as mock_is_processed, \
             patch('app.messaging.mappers.mapper_util.map_userconfig_create') as mock_map_create, \
             patch('app.messaging.mappers.mapper_util.map_userconfig_update') as mock_map_update, \
             patch('app.database.get_db') as mock_get_db_fn:

            from app.messaging.user_configuration_consumer import UserConsumer
            consumer = UserConsumer()

            # Wire sensible defaults onto the instance
            consumer.is_event_already_processed = MagicMock(return_value=False)
            consumer.create_ref_userconfig = MagicMock(return_value=(MagicMock(), False))
            consumer.update_ref_userconfig = MagicMock(return_value=(MagicMock(), False))
            consumer.map_userconfig_create = MagicMock(return_value={
                'UserConfigId': 1,
                'configBlob': {'SESSION_EXPIRE_MINUTES': 10},
                'modifiedDate': datetime(2025, 1, 1),
                'modifiedById': 'test-user',
            })
            consumer.map_userconfig_update = MagicMock(return_value={
                'UserConfigId': 1,
                'configBlob': {'SESSION_EXPIRE_MINUTES': 20},
                'modifiedDate': datetime(2025, 6, 1),
                'modifiedById': 'test-user',
            })
            consumer.get_db = lambda: iter([mock_db])

            # Make get_db_transaction work with the mock db
            @contextmanager
            def fake_transaction():
                yield mock_db

            consumer.get_db_transaction = fake_transaction

            yield consumer



class TestParseMessage:
    """_parse_message must return the data dict or None for invalid input."""

    def test_parse_valid_message(self, user_consumer):
        """Valid message returns the inner data dict"""
        msg = make_created_message()
        result = user_consumer._parse_message(msg)

        assert result is not None
        assert result['event_type'] == 'USERCONFIG_CREATED'
        assert result['userconfig_id'] == 1

    def test_parse_missing_correlation_id(self, user_consumer):
        """Missing correlation_id → returns None (FAILED_PERMANENT)"""
        msg = make_created_message()
        del msg['data']['correlation_id']
        assert user_consumer._parse_message(msg) is None

    def test_parse_missing_event_type(self, user_consumer):
        """Missing event_type → returns None"""
        msg = make_created_message()
        del msg['data']['event_type']
        assert user_consumer._parse_message(msg) is None

    def test_parse_missing_userconfig_id(self, user_consumer):
        """Missing userconfig_id → returns None"""
        msg = make_created_message()
        del msg['data']['userconfig_id']
        assert user_consumer._parse_message(msg) is None

    def test_parse_empty_message(self, user_consumer):
        """Completely empty message → returns None without crashing"""
        assert user_consumer._parse_message({}) is None



class TestProcessMessageRouting:
    """_process_userconfig_message must route to the correct handler and
    respect duplicate detection."""

    def test_routes_created_event_to_created_handler(self, user_consumer):
        """USERCONFIG_CREATED must reach _handle_userconfig_created"""
        user_consumer._handle_userconfig_created = MagicMock(return_value=MessageProcessingResult.SUCCESS)

        result = user_consumer._process_userconfig_message(make_created_message())

        user_consumer._handle_userconfig_created.assert_called_once()
        assert result == MessageProcessingResult.SUCCESS

    def test_routes_updated_event_to_updated_handler(self, user_consumer):
        """USERCONFIG_UPDATED must reach _handle_userconfig_updated"""
        user_consumer._handle_userconfig_updated = MagicMock(return_value=MessageProcessingResult.SUCCESS)

        result = user_consumer._process_userconfig_message(make_updated_message())

        user_consumer._handle_userconfig_updated.assert_called_once()
        assert result == MessageProcessingResult.SUCCESS

    def test_unknown_event_type_fails_permanently(self, user_consumer):
        """Unrecognised event_type → FAILED_PERMANENT (no retry)"""
        msg = make_created_message()
        msg['data']['event_type'] = 'USERCONFIG_EXPLODED'

        result = user_consumer._process_userconfig_message(msg)

        assert result == MessageProcessingResult.FAILED_PERMANENT

    def test_missing_required_field_fails_permanently(self, user_consumer):
        """Message missing userconfig_id → parse fails → FAILED_PERMANENT"""
        msg = make_created_message()
        del msg['data']['userconfig_id']

        result = user_consumer._process_userconfig_message(msg)

        assert result == MessageProcessingResult.FAILED_PERMANENT

    def test_duplicate_event_returns_duplicate(self, user_consumer):
        """Already-processed correlation_id → DUPLICATE (no handler called)"""
        user_consumer.is_event_already_processed = MagicMock(return_value=True)
        user_consumer._handle_userconfig_created = MagicMock()

        result = user_consumer._process_userconfig_message(make_created_message())

        assert result == MessageProcessingResult.DUPLICATE
        user_consumer._handle_userconfig_created.assert_not_called()



class TestHandleUserconfigCreated:
    """Unit tests for the USERCONFIG_CREATED handler."""

    def test_create_success(self, user_consumer):
        """Happy path: mapper succeeds, CRUD succeeds → SUCCESS"""
        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_created(mock_db, make_created_message()['data'])

        assert result == MessageProcessingResult.SUCCESS
        user_consumer.map_userconfig_create.assert_called_once()
        user_consumer.create_ref_userconfig.assert_called_once()

    def test_create_mapper_returns_none_fails_permanently(self, user_consumer):
        """Mapper failure (bad source data) → FAILED_PERMANENT"""
        user_consumer.map_userconfig_create = MagicMock(return_value=None)

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_created(mock_db, make_created_message()['data'])

        assert result == MessageProcessingResult.FAILED_PERMANENT
        user_consumer.create_ref_userconfig.assert_not_called()

    def test_create_crud_returns_false_fails_retryable(self, user_consumer):
        """CRUD returning (None/False, False) → FAILED_RETRYABLE"""
        user_consumer.create_ref_userconfig = MagicMock(return_value=(False, False))

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_created(mock_db, make_created_message()['data'])

        assert result == MessageProcessingResult.FAILED_RETRYABLE

    def test_create_crud_reports_duplicate_returns_duplicate(self, user_consumer):
        """CRUD returning (result, True) → DUPLICATE (already created)"""
        user_consumer.create_ref_userconfig = MagicMock(return_value=(MagicMock(), True))

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_created(mock_db, make_created_message()['data'])

        assert result == MessageProcessingResult.DUPLICATE

    def test_create_db_error_fails_retryable(self, user_consumer):
        """Unexpected DB exception → FAILED_RETRYABLE (transient error, retry)"""
        from sqlalchemy.exc import OperationalError
        user_consumer.create_ref_userconfig = MagicMock(
            side_effect=OperationalError("DB connection lost", None, None)
        )

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_created(mock_db, make_created_message()['data'])

        assert result == MessageProcessingResult.FAILED_RETRYABLE

    def test_create_schema_validation_fails_permanently(self, user_consumer):
        """Mapper returns data that fails Pydantic schema → FAILED_PERMANENT"""
        # Return a dict missing required fields so refUserConfigCreate(**data) raises
        user_consumer.map_userconfig_create = MagicMock(
            return_value={'bad_field': 'bad_value'}   # missing UserConfigId etc.
        )

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_created(mock_db, make_created_message()['data'])

        assert result == MessageProcessingResult.FAILED_PERMANENT



class TestHandleUserconfigUpdated:
    """Unit tests for the USERCONFIG_UPDATED handler."""

    def test_update_success(self, user_consumer):
        """Happy path: mapper succeeds, CRUD succeeds → SUCCESS"""
        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_updated(mock_db, make_updated_message()['data'])

        assert result == MessageProcessingResult.SUCCESS
        user_consumer.map_userconfig_update.assert_called_once()
        user_consumer.update_ref_userconfig.assert_called_once()

    def test_update_mapper_returns_none_fails_permanently(self, user_consumer):
        """Mapper failure → FAILED_PERMANENT"""
        user_consumer.map_userconfig_update = MagicMock(return_value=None)

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_updated(mock_db, make_updated_message()['data'])

        assert result == MessageProcessingResult.FAILED_PERMANENT
        user_consumer.update_ref_userconfig.assert_not_called()

    def test_update_crud_returns_duplicate_returns_duplicate(self, user_consumer):
        """CRUD reports duplicate (was_duplicate=True) for non-sync → DUPLICATE"""
        user_consumer.update_ref_userconfig = MagicMock(return_value=(MagicMock(), True))

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_updated(mock_db, make_updated_message()['data'])

        assert result == MessageProcessingResult.DUPLICATE

    def test_update_nonexistent_row_returns_success(self, user_consumer):
        """Row not found (CRUD returns None, not_duplicate) → SUCCESS (graceful)"""
        user_consumer.update_ref_userconfig = MagicMock(return_value=(None, False))

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_updated(mock_db, make_updated_message()['data'])

        assert result == MessageProcessingResult.SUCCESS

    def test_update_db_error_fails_retryable(self, user_consumer):
        """DB exception → FAILED_RETRYABLE"""
        from sqlalchemy.exc import OperationalError
        user_consumer.update_ref_userconfig = MagicMock(
            side_effect=OperationalError("connection lost", None, None)
        )

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_updated(mock_db, make_updated_message()['data'])

        assert result == MessageProcessingResult.FAILED_RETRYABLE

    def test_update_schema_validation_fails_permanently(self, user_consumer):
        """Mapper returns bad dict → Pydantic validation → FAILED_PERMANENT"""
        user_consumer.map_userconfig_update = MagicMock(
            return_value={'bad_field': 'bad_value'}
        )

        mock_db = MagicMock()
        result = user_consumer._handle_userconfig_updated(mock_db, make_updated_message()['data'])

        assert result == MessageProcessingResult.FAILED_PERMANENT
