"""
Integration tests for Patient Service UserConfig Consumer
Tests the flow: RabbitMQ Message -> UserConsumer -> REF_USERCONFIG table -> PROCESSED_EVENTS tracking

SQL to manually clear test data if needed:
  DELETE FROM [PROCESSED_EVENTS] WHERE aggregate_id = '9999';
  DELETE FROM [REF_USERCONFIG] WHERE UserConfigID = 9999;
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict

import pytest

from app.messaging.user_configuration_consumer import UserConsumer
from app.database import SessionLocal
from app.models.processed_events_model import MessageProcessingResult, ProcessedEvent
from app.models.ref_userconfig_model import RefUserConfig




# Fixed test ID
# All tests use this same ID so cleanup is simple and predictable.
TEST_USERCONFIG_ID = 9999



@pytest.fixture(scope="function")
def integration_db():
    """
    Fresh database session for each test.
    Uses the real patient-service database connection (SessionLocal from app.database).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_consumer():
    """
    A real UserConsumer instance.
    We call _process_userconfig_message() directly — no RabbitMQ connection needed.
    """
    consumer = UserConsumer()
    yield consumer
    if consumer.client:
        consumer.client.close()


@pytest.fixture
def mock_userconfig_data():
    """
    Raw userconfig payload as the user-service outbox publishes it.
    """
    return {
        "id": TEST_USERCONFIG_ID,
        "configBlob": {
            "SESSION_EXPIRE_MINUTES": 10,
            "MAX_PATIENT_PHOTO": 10,
            "MAX_ITEMS_TO_RETURN": 40
            },
        "modifiedDate": datetime.now().isoformat(),
        "modifiedById": "test-user-service",
    }


@pytest.fixture(autouse=True)
def cleanup_test_data(integration_db):
    """
    Cleanup fixture that runs before AND after each test.

    BEFORE (yield): wipes any rows from a previously crashed test run so every
                    test starts with a known-clean state.
    AFTER  (yield): deletes everything the test created.

    We tag test data by:
      - RefUserConfig.UserConfigID == TEST_USERCONFIG_ID  (our fixed test ID)
      - ProcessedEvent.aggregate_id == str(TEST_USERCONFIG_ID)
    """
    # PRE-TEST CLEANUP
    try:
        integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.aggregate_id == str(TEST_USERCONFIG_ID)
        ).delete()
        integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).delete()
        integration_db.commit()
        print(f"\n[SETUP] Pre-test cleanup done (UserConfigID={TEST_USERCONFIG_ID})")
    except Exception as e:
        integration_db.rollback()
        print(f"\n[SETUP] Warning during pre-test cleanup: {str(e)}")

    yield  # ← test runs here

    # POST-TEST CLEANUP
    try:
        integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.aggregate_id == str(TEST_USERCONFIG_ID)
        ).delete()
        integration_db.commit()

        integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).delete()
        integration_db.commit()

        print(f"[CLEANUP] Post-test cleanup done (UserConfigID={TEST_USERCONFIG_ID})")
    except Exception as e:
        integration_db.rollback()
        print(f"[CLEANUP] Warning during post-test cleanup: {str(e)}")




def create_userconfig_created_message(
    userconfig_data: Dict[str, Any],
    correlation_id: str = None,
) -> Dict[str, Any]:
    """
    Build a USERCONFIG_CREATED message in the exact shape the consumer expects.

    Consumer reads:
      message["data"]["userconfig_id"]    → which config this is about
      message["data"]["userconfig_data"]  → the raw source dict passed to the mapper
      message["data"]["created_by"]       → recorded as processed_by in PROCESSED_EVENTS
    """
    if not correlation_id:
        correlation_id = str(uuid.uuid4()).upper()

    return {
        "timestamp": datetime.now().isoformat(),
        "source_service": "user-service",
        "data": {
            "correlation_id": correlation_id,
            "event_type": "USERCONFIG_CREATED",
            "userconfig_id": userconfig_data["id"],
            "userconfig_data": userconfig_data,     # ← key the consumer uses for CREATE
            "created_by": userconfig_data.get("modifiedById", "user_service"),
            "timestamp": datetime.now().isoformat(),
        },
    }


def create_userconfig_updated_message(
    userconfig_id: int,
    old_data: Dict[str, Any],
    new_data: Dict[str, Any],
    correlation_id: str = None,
) -> Dict[str, Any]:
    """
    Build a USERCONFIG_UPDATED message in the exact shape the consumer expects.

    Consumer reads:
      message["data"]["userconfig_id"]  → which config to update
      message["data"]["new_data"]       → the raw source dict passed to the mapper
      message["data"]["modified_by"]    → recorded as processed_by in PROCESSED_EVENTS
    """
    if not correlation_id:
        correlation_id = str(uuid.uuid4()).upper()

    # Compute which keys actually changed (for the changes dict in the payload)
    changes = {}
    for key in new_data:
        if key in old_data and old_data[key] != new_data[key]:
            changes[key] = {"old": old_data[key], "new": new_data[key]}

    return {
        "timestamp": datetime.now().isoformat(),
        "source_service": "user-service",
        "data": {
            "correlation_id": correlation_id,
            "event_type": "USERCONFIG_UPDATED",
            "userconfig_id": userconfig_id,
            "old_data": old_data,
            "new_data": new_data,               # ← key the consumer uses for UPDATE
            "changes": changes,
            "modified_by": new_data.get("modifiedById", "user_service"),
            "timestamp": datetime.now().isoformat(),
        },
    }



class TestConsumerUserconfigCreate:
    """
    Tests for USERCONFIG_CREATED event processing.
    The consumer must:
      1. Map the raw payload through map_userconfig_create
      2. Insert a row into REF_USERCONFIG (via IDENTITY_INSERT raw SQL)
      3. Write a PROCESSED_EVENTS row for idempotency tracking
    """

    def test_create_userconfig_processes_message_successfully(
        self, integration_db, user_consumer, mock_userconfig_data
    ):
        """
        GIVEN: A valid USERCONFIG_CREATED message
        WHEN:  The consumer processes it
        THEN:  A REF_USERCONFIG row is created AND a PROCESSED_EVENTS row exists

        Goal: verify the full happy-path — message arrives, REF_USERCONFIG row
              is inserted with correct data, idempotency record is written.
        """
        correlation_id = str(uuid.uuid4()).upper()
        message = create_userconfig_created_message(mock_userconfig_data, correlation_id)

        print(f"\nProcessing USERCONFIG_CREATED — correlation_id: {correlation_id}")

        result = user_consumer._process_userconfig_message(message)

        print(f"Processing result: {result}")

        assert result == MessageProcessingResult.SUCCESS

        ref_config = integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).first()

        assert ref_config is not None
        assert ref_config.UserConfigID == TEST_USERCONFIG_ID
        assert ref_config.modifiedById == "test-user-service"

        # configBlob is stored as a JSON string — parse and compare
        stored_blob = json.loads(ref_config.configBlob)
        assert stored_blob["SESSION_EXPIRE_MINUTES"] == 10
        assert stored_blob["MAX_PATIENT_PHOTO"] == 10
        assert stored_blob["MAX_ITEMS_TO_RETURN"] == 40

        print(f"DONE: Created REF_USERCONFIG ID: {ref_config.UserConfigID}")
        print(f"  configBlob: {ref_config.configBlob}")
        print(f"  modifiedById: {ref_config.modifiedById}")

        processed_event = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).first()

        assert processed_event is not None
        assert processed_event.event_type == "USERCONFIG_CREATED"
        assert processed_event.aggregate_id == str(TEST_USERCONFIG_ID)

        print(f"DONE: Created PROCESSED_EVENT correlation_id: {processed_event.correlation_id}")
        print(f"  event_type: {processed_event.event_type}")
        print(f"  aggregate_id: {processed_event.aggregate_id}")


    def test_duplicate_create_message_is_idempotent(
        self, integration_db, user_consumer, mock_userconfig_data
    ):
        """
        GIVEN: A USERCONFIG_CREATED message processed twice with the same correlation_id
        WHEN:  The consumer receives the duplicate
        THEN:  Returns DUPLICATE and no additional rows are created in either table

        Goal: verify idempotency — the same event arriving twice (e.g. network retry)
              must not create duplicate REF_USERCONFIG rows or corrupt the DB.
        """
        correlation_id = str(uuid.uuid4()).upper()
        message = create_userconfig_created_message(mock_userconfig_data, correlation_id)

        print(f"\nProcessing initial USERCONFIG_CREATED — correlation_id: {correlation_id}")

        # First delivery — must succeed
        result1 = user_consumer._process_userconfig_message(message)
        assert result1 == MessageProcessingResult.SUCCESS

        # Capture counts after first delivery
        initial_config_count = integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).count()
        initial_event_count = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).count()

        print(f"Initial counts — REF_USERCONFIG: {initial_config_count}, PROCESSED_EVENTS: {initial_event_count}")

        # Second delivery — same message, same correlation_id
        print(f"Processing duplicate USERCONFIG_CREATED — correlation_id: {correlation_id}")
        result2 = user_consumer._process_userconfig_message(message)

        assert result2 == MessageProcessingResult.DUPLICATE

        # Neither table should have grown
        final_config_count = integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).count()
        final_event_count = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).count()

        assert final_config_count == initial_config_count
        assert final_event_count == initial_event_count

        print(f"DONE: Duplicate correctly rejected — no extra rows created")
        print(f"  REF_USERCONFIG count: {initial_config_count} -> {final_config_count}")
        print(f"  PROCESSED_EVENTS count: {initial_event_count} -> {final_event_count}")


    def test_create_with_invalid_data_fails_permanently(
        self, integration_db, user_consumer
    ):
        """
        GIVEN: A USERCONFIG_CREATED message missing the required "userconfig_id" field
        WHEN:  The consumer processes it
        THEN:  Returns FAILED_PERMANENT and no rows are created

        Goal: malformed messages that will never be valid (missing required fields)
              must be rejected permanently and NOT retried — they would fail forever.
        """
        correlation_id = str(uuid.uuid4()).upper()

        # "userconfig_id" is intentionally absent — _parse_message will return None
        invalid_message = {
            "timestamp": datetime.now().isoformat(),
            "source_service": "user-service",
            "data": {
                "correlation_id": correlation_id,
                "event_type": "USERCONFIG_CREATED",
                # "userconfig_id" missing on purpose
            },
        }

        print(f"\nProcessing invalid USERCONFIG_CREATED — correlation_id: {correlation_id}")

        result = user_consumer._process_userconfig_message(invalid_message)

        assert result == MessageProcessingResult.FAILED_PERMANENT

        # No PROCESSED_EVENTS row for permanently-failed messages
        processed_event = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).first()
        assert processed_event is None

        print(f"DONE: Invalid message rejected permanently — no DB rows created")


    def test_create_with_mapping_failure_fails_permanently(
        self, integration_db, user_consumer, mock_userconfig_data, monkeypatch
    ):
        """
        GIVEN: A USERCONFIG_CREATED message where the mapper returns None
               (simulates missing required source fields like "id" or "configBlob")
        WHEN:  The consumer processes it
        THEN:  Returns FAILED_PERMANENT

        Goal: mapper failures mean the source data is structurally wrong and will
              never map correctly — treat as permanent failure, not retryable.
        """
        correlation_id = str(uuid.uuid4()).upper()
        message = create_userconfig_created_message(mock_userconfig_data, correlation_id)

        print(f"\nProcessing USERCONFIG_CREATED with mapping failure — correlation_id: {correlation_id}")

        # Force mapper to return None (simulates missing required source fields)
        monkeypatch.setattr(user_consumer, "map_userconfig_create", lambda x: None)

        result = user_consumer._process_userconfig_message(message)

        assert result == MessageProcessingResult.FAILED_PERMANENT
        print(f"DONE: Mapping failure correctly returned FAILED_PERMANENT")


    def test_create_with_database_error_returns_retryable(
        self, integration_db, user_consumer, mock_userconfig_data, monkeypatch
    ):
        """
        GIVEN: A valid USERCONFIG_CREATED message and a transient database failure
        WHEN:  The consumer processes it and the CRUD operation throws OperationalError
        THEN:  Returns FAILED_RETRYABLE so the message stays on the queue for retry

        Goal: transient failures (DB connection drop, deadlock, timeout) must NOT
              be swallowed — the message must remain in the queue and be retried.
        """
        correlation_id = str(uuid.uuid4()).upper()
        message = create_userconfig_created_message(mock_userconfig_data, correlation_id)

        print(f"\nSimulating DB error for USERCONFIG_CREATED — correlation_id: {correlation_id}")

        from sqlalchemy.exc import OperationalError

        def mock_create_failure(*args, **kwargs):
            raise OperationalError("Database connection lost", None, None)

        monkeypatch.setattr(user_consumer, "create_ref_userconfig", mock_create_failure)

        result = user_consumer._process_userconfig_message(message)

        assert result == MessageProcessingResult.FAILED_RETRYABLE

        # No PROCESSED_EVENTS row — the event was NOT marked as processed
        # so RabbitMQ will requeue it and the consumer will try again
        processed_event = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).first()
        assert processed_event is None

        print(f"DONE: DB error correctly returned FAILED_RETRYABLE")
        print(f"  No PROCESSED_EVENTS row — message will be requeued for retry")




class TestConsumerUserconfigUpdate:
    """
    Tests for USERCONFIG_UPDATED event processing.
    The consumer must:
      1. Map the raw "new_data" payload through map_userconfig_update
      2. Update the existing REF_USERCONFIG row
      3. Write a PROCESSED_EVENTS row for idempotency tracking

    Every update test that needs an existing row calls _seed_initial_userconfig()
    first — this is the equivalent of first creating the patient in the scheduler tests.
    """

    def _seed_initial_userconfig(self, user_consumer, mock_userconfig_data) -> str:
        """
        Helper: send a USERCONFIG_CREATED message so a real REF_USERCONFIG row
        exists before the update test runs.

        Returns the correlation_id used for the create (so tests can clear it
        from PROCESSED_EVENTS if they want a clean count for the update assertion).
        """
        create_correlation_id = str(uuid.uuid4()).upper()
        create_message = create_userconfig_created_message(
            mock_userconfig_data, create_correlation_id
        )
        result = user_consumer._process_userconfig_message(create_message)
        assert result == MessageProcessingResult.SUCCESS, \
            "Seed step failed — cannot run update test without an existing REF_USERCONFIG row"

        print(f"\n[SEED] Created initial REF_USERCONFIG row (ID={TEST_USERCONFIG_ID})")
        return create_correlation_id

    def test_update_userconfig_processes_message_successfully(
        self, integration_db, user_consumer, mock_userconfig_data
    ):
        """
        GIVEN: An existing REF_USERCONFIG row and a USERCONFIG_UPDATED message
               with changed configBlob values
        WHEN:  The consumer processes it
        THEN:  The REF_USERCONFIG row is updated AND a PROCESSED_EVENTS row is created

        Goal: verify the full happy-path for the update flow — correct values land
              in the DB and the idempotency record is written.
        """
        create_correlation_id = self._seed_initial_userconfig(user_consumer, mock_userconfig_data)

        # Clear the CREATED processed event so counts are clean for update assertions
        integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == create_correlation_id
        ).delete()
        integration_db.commit()

        # Build the update message with different configBlob values
        updated_data = dict(mock_userconfig_data)
        updated_data["configBlob"] = {"SESSION_EXPIRE_MINUTES": 20, "MAX_PATIENT_PHOTO": 20, "MAX_ITEMS_TO_RETURN": 80}
        updated_data["modifiedDate"] = datetime.now().isoformat()

        update_correlation_id = str(uuid.uuid4()).upper()
        update_message = create_userconfig_updated_message(
            TEST_USERCONFIG_ID,
            mock_userconfig_data,
            updated_data,
            update_correlation_id,
        )

        print(f"Processing USERCONFIG_UPDATED — correlation_id: {update_correlation_id}")

        result = user_consumer._process_userconfig_message(update_message)

        assert result == MessageProcessingResult.SUCCESS

        ref_config = integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).first()

        assert ref_config is not None
        stored_blob = json.loads(ref_config.configBlob)
        assert stored_blob["SESSION_EXPIRE_MINUTES"] == 20
        assert stored_blob["MAX_PATIENT_PHOTO"] == 20
        assert stored_blob["MAX_ITEMS_TO_RETURN"] == 80

        print(f"DONE: Updated REF_USERCONFIG ID: {ref_config.UserConfigID}")
        print(f"New configBlob: {ref_config.configBlob}")

        processed_event = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == update_correlation_id
        ).first()

        assert processed_event is not None
        assert processed_event.event_type == "USERCONFIG_UPDATED"
        assert processed_event.aggregate_id == str(TEST_USERCONFIG_ID)

        print(f"DONE: Created PROCESSED_EVENT for update — event_type: {processed_event.event_type}")


    def test_update_nonexistent_userconfig_succeeds_gracefully(
        self, integration_db, user_consumer, mock_userconfig_data
    ):
        """
        GIVEN: A USERCONFIG_UPDATED message for a userconfig ID that does not
               exist in REF_USERCONFIG (out-of-order delivery)
        WHEN:  The consumer processes it
        THEN:  Returns SUCCESS (graceful handling) and a PROCESSED_EVENTS row is
               created so the message is NOT endlessly retried

        Goal: out-of-order messages must not crash the consumer or block the queue.
              Returning SUCCESS tells RabbitMQ to acknowledge and discard the message.
        """
        correlation_id = str(uuid.uuid4()).upper()

        # Build update for an ID that definitely does not exist
        non_existent_id = 88888
        non_existent_data = dict(mock_userconfig_data)
        non_existent_data["id"] = non_existent_id

        update_message = create_userconfig_updated_message(
            non_existent_id,
            non_existent_data,
            non_existent_data,
            correlation_id,
        )

        print(f"\nProcessing UPDATE for non-existent userconfig ID={non_existent_id}")

        result = user_consumer._process_userconfig_message(update_message)

        assert result == MessageProcessingResult.SUCCESS

        processed_event = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).first()
        assert processed_event is not None

        print(f"DONE: Non-existent userconfig update handled gracefully")
        print(f"  PROCESSED_EVENTS created: aggregate_id={processed_event.aggregate_id}")

        # Clean up this extra processed event (it has aggregate_id='88888',
        # outside the autouse cleanup scope which only targets '9999')
        integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == correlation_id
        ).delete()
        integration_db.commit()


    def test_duplicate_update_message_is_idempotent(
        self, integration_db, user_consumer, mock_userconfig_data
    ):
        """
        GIVEN: A USERCONFIG_UPDATED message processed twice with the same correlation_id
        WHEN:  The consumer receives the duplicate
        THEN:  Returns DUPLICATE and the REF_USERCONFIG row is not modified again

        Goal: verify idempotency for update events — the same update arriving twice
              must produce the same end state without double-writing.
        """

        self._seed_initial_userconfig(user_consumer, mock_userconfig_data)

        updated_data = dict(mock_userconfig_data)
        updated_data["configBlob"] = {"SESSION_EXPIRE_MINUTES": 20, "MAX_PATIENT_PHOTO": 20, "MAX_ITEMS_TO_RETURN": 80}
        updated_data["modifiedDate"] = datetime.now().isoformat()

        update_correlation_id = str(uuid.uuid4()).upper()
        update_message = create_userconfig_updated_message(
            TEST_USERCONFIG_ID,
            mock_userconfig_data,
            updated_data,
            update_correlation_id,
        )

        # First delivery
        print(f"\nProcessing initial USERCONFIG_UPDATED — correlation_id: {update_correlation_id}")
        result1 = user_consumer._process_userconfig_message(update_message)
        assert result1 == MessageProcessingResult.SUCCESS

        # Capture state after first delivery
        after_first = integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).first()
        blob_after_first = after_first.configBlob
        modified_date_after_first = after_first.modifiedDate

        print(f"State after first update — configBlob: {blob_after_first}")

        # Second delivery — same message
        print(f"Processing duplicate USERCONFIG_UPDATED — correlation_id: {update_correlation_id}")
        result2 = user_consumer._process_userconfig_message(update_message)

        assert result2 == MessageProcessingResult.DUPLICATE

        # Row must be unchanged from after first delivery
        after_second = integration_db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == TEST_USERCONFIG_ID
        ).first()
        integration_db.refresh(after_second)

        assert after_second.configBlob == blob_after_first
        assert after_second.modifiedDate == modified_date_after_first

        print(f"DONE: Duplicate update rejected correctly")
        print(f"configBlob unchanged: {after_second.configBlob}")
        print(f"modifiedDate unchanged: {after_second.modifiedDate}")


    def test_update_with_mapping_failure_fails_permanently(
        self, integration_db, user_consumer, mock_userconfig_data, monkeypatch
    ):
        """
        GIVEN: A USERCONFIG_UPDATED message where the mapper returns None
        WHEN:  The consumer processes it
        THEN:  Returns FAILED_PERMANENT

        Goal: mapper failures on the update path are treated identically to the
              create path — bad source data should go to DLQ, not be retried.
        """
        self._seed_initial_userconfig(user_consumer, mock_userconfig_data)

        updated_data = dict(mock_userconfig_data)
        updated_data["configBlob"] = {"SESSION_EXPIRE_MINUTES": 20}

        update_correlation_id = str(uuid.uuid4()).upper()
        update_message = create_userconfig_updated_message(
            TEST_USERCONFIG_ID,
            mock_userconfig_data,
            updated_data,
            update_correlation_id,
        )

        print(f"\nProcessing USERCONFIG_UPDATED with mapping failure — correlation_id: {update_correlation_id}")

        # Force the mapper to return None
        monkeypatch.setattr(user_consumer, "map_userconfig_update", lambda x: None)

        result = user_consumer._process_userconfig_message(update_message)

        assert result == MessageProcessingResult.FAILED_PERMANENT
        print(f"DONE: Mapping failure correctly returned FAILED_PERMANENT")


    def test_update_with_database_error_returns_retryable(
        self, integration_db, user_consumer, mock_userconfig_data, monkeypatch
    ):
        """
        GIVEN: A valid USERCONFIG_UPDATED message and a transient database failure
        WHEN:  The consumer processes it and the CRUD operation throws OperationalError
        THEN:  Returns FAILED_RETRYABLE and no PROCESSED_EVENTS row is created

        Goal: transient failures on the update path must be retried, not swallowed.
        """
        self._seed_initial_userconfig(user_consumer, mock_userconfig_data)

        updated_data = dict(mock_userconfig_data)
        updated_data["configBlob"] = {"SESSION_EXPIRE_MINUTES": 20}
        updated_data["modifiedDate"] = datetime.now().isoformat()

        update_correlation_id = str(uuid.uuid4()).upper()
        update_message = create_userconfig_updated_message(
            TEST_USERCONFIG_ID,
            mock_userconfig_data,
            updated_data,
            update_correlation_id,
        )

        print(f"\nSimulating DB error for USERCONFIG_UPDATED — correlation_id: {update_correlation_id}")

        from sqlalchemy.exc import OperationalError

        def mock_update_failure(*args, **kwargs):
            raise OperationalError("Database connection lost", None, None)

        monkeypatch.setattr(user_consumer, "update_ref_userconfig", mock_update_failure)

        result = user_consumer._process_userconfig_message(update_message)

        assert result == MessageProcessingResult.FAILED_RETRYABLE

        # No PROCESSED_EVENTS row — the event was NOT marked as processed
        processed_event = integration_db.query(ProcessedEvent).filter(
            ProcessedEvent.correlation_id == update_correlation_id
        ).first()
        assert processed_event is None

        print(f"DONE: DB error correctly returned FAILED_RETRYABLE")
        print(f"  No PROCESSED_EVENTS row — message will be requeued for retry")
