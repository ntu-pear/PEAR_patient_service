"""
Integration tests for Patient Service (Publisher) Outbox Pattern
Tests for flow: Patient CRUD -> OUTBOX_EVENTS table creation
"""
import uuid
from datetime import datetime

import pytest
from app.crud.patient_crud import (
    get_patient, get_patients, create_patient, update_patient, delete_patient, get_patient_include_deleted
)
from app.database import SessionLocal
from app.models.patient_model import Patient
from app.models.outbox_model import OutboxEvent
from app.schemas.patient import PatientCreate, PatientUpdate
from app.models.patient_list_language_model import PatientListLanguage

@pytest.fixture
def unique_nric():
    """Generate a unique NRIC for each test."""
    # Use last 7 chars of UUID to create unique NRIC
    unique_id = str(uuid.uuid4()).replace('-', '')[:7].upper()
    return f"S{unique_id}A"

@pytest.fixture(scope="session")
def session_db():
    """
    Session-level database connection for setup/teardown of reference data.
    This is separate from the per-test integration_db fixture.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# for foreign key constraint
@pytest.fixture(autouse=True, scope="session")
def setup_reference_tables(session_db):
    """
    Setup required reference tables before tests run.
    Only inserts if data doesn't exist - doesn't delete existing data.
    """
    try:
        # Check if languages already exist
        existing_lang_1 = session_db.query(PatientListLanguage).filter_by(id=1).first()
        existing_lang_2 = session_db.query(PatientListLanguage).filter_by(id=2).first()

        # Only insert if they don't exist
        if not existing_lang_1:
            lang1 = PatientListLanguage(
                id=1,
                value="English",
                isDeleted='0',
                createdDate=datetime.now(),
                modifiedDate=datetime.now()
            )
            session_db.add(lang1)

        if not existing_lang_2:
            lang2 = PatientListLanguage(
                id=2,
                value="Mandarin",
                isDeleted='0',
                createdDate=datetime.now(),
                modifiedDate=datetime.now()
            )
            session_db.add(lang2)

        session_db.commit()
        print("\n[SETUP] Reference tables verified/initialized")

    except Exception as e:
        session_db.rollback()
        print(f"\n[SETUP] Warning: {str(e)}")

    yield

@pytest.fixture(scope="function")
def integration_db():
    """
    Each test gets a fresh DB session with automatic rollback.
    """
    db = SessionLocal()
    # Start a transaction
    db.begin()

    try:
        yield db
    finally:
        # Rollback everything
        db.rollback()
        db.close()

@pytest.fixture
def mock_user():
    """
    Mock user info for CRUD operations
    """
    return {
        "id": "test-user-1",
        "fullname": "Integration Test User"
    }
@pytest.fixture
def sample_updated_patient_data(unique_nric):
    return PatientUpdate(
            name="Updated Patient",
            nric=unique_nric,
            address="Updated Address",
            tempAddress="Test Temp Address",
            homeNo="Test Home No",
            handphoneNo="Test Hand Phone No",
            gender="M",
            dateOfBirth=datetime(2020, 1, 1),
            isApproved="1",
            preferredName="Test Name",
            #preferredLanguageId=2,
            updateBit="1",
            autoGame="1",
            startDate=datetime(2020, 1, 1),
            endDate=datetime(2020, 1, 1),
            isActive="1",
            isRespiteCare="1",
            privacyLevel=1,
            terminationReason="Test Reason",
            inActiveReason="Test Reason",
            inActiveDate=datetime(2020, 1, 1),
            profilePicture="Test Profile Picture",
            isDeleted=0,
            modifiedDate=datetime.now(),
            ModifiedById="test-user-1",
        )

@pytest.fixture
def sample_created_patient_data(unique_nric):
    return PatientCreate(
            name="Test Patient",
            nric=unique_nric,
            address="Test Address",
            tempAddress="Test Temp Address",
            homeNo="Test Home No",
            handphoneNo="Test Hand Phone No",
            gender="M",
            dateOfBirth=datetime(2020, 1, 1),
            isApproved="1",
            preferredName="Test Name",
            #preferredLanguageId=2,
            updateBit="1",
            autoGame="1",
            startDate=datetime(2020, 1, 1),
            endDate=datetime(2020, 1, 1),
            isActive="1",
            isRespiteCare="1",
            privacyLevel=1,
            terminationReason="Test Reason",
            inActiveReason="Test Reason",
            inActiveDate=datetime(2020, 1, 1),
            profilePicture="Test Profile Picture",
            isDeleted=0,
            createdDate=datetime.now(),
            modifiedDate=datetime.now(),
            CreatedById="test-user-1",
            ModifiedById="test-user-1",
        )

# Uncomment this when you are testing to ensure clean state.
# NOTE (IMPORTANT): This will delete ALL records in the tables after each test function, so make sure you point to the testing DB, and not PROD!

@pytest.fixture(autouse=True)
def cleanup_test_data(integration_db):
    """
    Cleanup fixture that runs after each test.
    Deletes all test data created during the test.
    """
    # This runs BEFORE the test
    yield

    # This runs AFTER the test - cleanup
    try:
        # Delete all outbox events first
        integration_db.query(OutboxEvent).delete()
        integration_db.commit()

        # Delete all patients
        integration_db.query(Patient).delete()
        integration_db.commit()

        print("\n[CLEANUP] Test data cleared successfully")
    except Exception as e:
        integration_db.rollback()
        print(f"\n[CLEANUP] Warning: Failed to cleanup test data: {str(e)}")

class TestPatientCreateOutbox:
    def test_create_patient_creates_outbox(self, integration_db, mock_user, sample_created_patient_data):
        """
        GIVEN: Patient data
        WHEN: create_patient is called
        THEN: Patient and OutboxEvent are created atomically.

        Goal: Check if the creation of Patient also creates an OutboxEvent. This function checks if the created records are the same
        """
        patient_data = sample_created_patient_data

        # create patient
        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\n[DONE]: Created Patient ID: {patient.id}")
        print(f"Patient Name: {patient.name}")
        print(f"Patient Gender: {patient.gender}")
        print(f"Patient Created By: {patient.CreatedById}")

        # Assert if patient is created
        assert patient.id is not None
        assert patient.name == "Test Patient"
        assert patient.gender == "M"
        assert patient.CreatedById == 'test-user-1'
        assert patient.isDeleted == 0
        assert patient.mask_nric == "*****" + patient.nric[-4:]

        # Assert that outbox event is created
        outbox_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(patient.id)
        ).first()

        assert outbox_event is not None
        assert outbox_event.event_type == "PATIENT_CREATED"
        assert outbox_event.aggregate_id == str(patient.id)
        assert outbox_event.routing_key == f"patient.created.{patient.id}"

        print(f"\n[DONE]: Created OutboxEvent ID: {outbox_event.id}")
        print(f" Event Type: {outbox_event.event_type}")
        print(f" Correlation ID: {outbox_event.correlation_id}")

        # Verify payload
        payload = outbox_event.get_payload()
        assert payload["event_type"] == "PATIENT_CREATED"
        assert payload["patient_id"] == patient.id
        assert payload["created_by"] == "test-user-1"
        assert "correlation_id" in payload
        assert "timestamp" in payload

    def test_duplicate_patient_fails_atomically(self, integration_db, mock_user, sample_created_patient_data):
        """
        GIVEN: An existing Patient with NRIC "S0123456A"
        WHEN: create_patient is called with the same NRIC
        THEN: HTTPException raised and no additional outbox event created

        Goal: This function checks if the creation of duplicate patient is rejected properly and no outbox event is created.
        """
        patient_data = sample_created_patient_data
        # create first patient
        patient1 = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\n[DONE]: Created Patient ID: {patient1.id}")

        initial_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_CREATED"
        ).count()

        # Attempt to create duplicate
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            create_patient(
                db=integration_db,
                patient=patient_data,
                user=mock_user['id'],
                user_full_name=mock_user['fullname'],
                correlation_id=str(uuid.uuid4())
            )
        assert exc_info.value.status_code == 400
        print(f"DONE: Duplicate creation properly rejected")
        # Verify no additional outbox events created
        final_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_CREATED"
        ).count()
        assert final_outbox_count == initial_outbox_count

class TestPatientUpdateOutbox:
    def test_update_patient_creates_outbox_event(self, integration_db, mock_user, sample_created_patient_data, sample_updated_patient_data):
        """
        GIVEN: An existing Patient
        WHEN: update_patient is called with changes
        THEN: OutboxEvent records changes atomically

        Goal: This function checks if updating a patient creates an outbox event with the changes.
        """
        # create initial patient
        patient_data = sample_created_patient_data

        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        original_id = patient.id

        print(f"\n[DONE]: Created Patient ID: {patient.id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Update patient
        update_data = sample_updated_patient_data

        updated_patient = update_patient(
            patient_id= original_id,
            db=integration_db,
            patient=update_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        print(f"\n[DONE]: Updated Patient ID: {original_id}")

        # Assert that Patient is updated
        assert updated_patient.name == "Updated Patient"
        assert updated_patient.address == "Updated Address"

        # Assert that outbox event is created
        outbox_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_UPDATED",
            OutboxEvent.aggregate_id == str(original_id)
        ).first()

        assert outbox_event is not None
        assert outbox_event.routing_key == f"patient.updated.{original_id}"

        print(f"DONE: Created UPDATE Outbox Event ID: {outbox_event.id}")

        # Verify payload contains changes
        payload = outbox_event.get_payload()
        assert "changes" in payload
        assert "name" in payload["changes"]
        assert payload["changes"]["name"]["old"] == "Test Patient"
        assert payload["changes"]["name"]["new"] == "Updated Patient"

    def test_update_with_no_changes_does_not_create_outbox(self, integration_db, mock_user, sample_created_patient_data, sample_updated_patient_data):
        """
        GIVEN: An existing Patient
        WHEN: update_patient is called with no actual changes
        THEN: No new OutboxEvent is created for PATIENT_UPDATED
        NOTE: This function will create one extra record in the Patient table, and no record in Outbox table.

        Goal: This function checks if updating a patient with no actual changes does NOT create an outbox event.
        """
        # Create patient
        patient_data = sample_created_patient_data
        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\nDONE: Created Patient ID: {patient.id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(patient.id)
        ).delete()
        integration_db.commit()

        # "Update" with same values (no actual changes)
        update_data = sample_created_patient_data
        update_patient(
            patient_id=patient.id,
            db=integration_db,
            patient=update_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: No-change update processed")

        # No new PATIENT_UPDATED event should be created
        updated_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_UPDATED",
            OutboxEvent.aggregate_id == str(patient.id)
        ).first()

        assert updated_event is None
        print(f"DONE: Verified no UPDATE event created")

    def test_update_nonexistent_patient_fails(self, integration_db, mock_user, sample_updated_patient_data):
        """
        GIVEN: Non-existent patient ID
        WHEN: update_patient is called
        THEN: HTTPException raised and no outbox event created

        Goal: This function checks if updating a non-existent patient is rejected properly and no outbox event is created.
        """
        initial_outbox_count = integration_db.query(OutboxEvent).count()

        update_data = sample_updated_patient_data

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            update_patient(
                patient_id=1,
                db=integration_db,
                patient=update_data,
                user=mock_user['id'],
                user_full_name=mock_user['fullname'],
                correlation_id=str(uuid.uuid4())
            )

        assert exc_info.value.status_code == 404

        print(f"\nDONE: Update of non-existent patient properly rejected")

        # No outbox event created
        final_outbox_count = integration_db.query(OutboxEvent).count()
        assert final_outbox_count == initial_outbox_count

class TestPatientDeleteOutbox:
    def test_delete_patient_creates_outbox_event(self, integration_db, mock_user, sample_created_patient_data):
        """
        GIVEN: An existing patient
        WHEN: delete_patient is called
        THEN: OutboxEvent records deletion atomically

        Goal: This function checks if soft-deleting a patient creates an outbox event with the deletion info.
        """
        # Create patient
        patient_data = sample_created_patient_data
        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        original_id = patient.id

        print(f"\nDONE: Created Patient ID: {original_id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Delete patient
        deleted_patient = delete_patient(
            patient_id= original_id,
            db=integration_db,
            user_id=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: Deleted Patient ID: {original_id}")

        # Assertions: Patient soft-deleted
        assert deleted_patient.isDeleted == 1

        # There is no get_patient_by_id in the patient_crud thus unable to assert refreshed = get_patient
        refreshed = get_patient_include_deleted(
            db=integration_db,
            patient_id=original_id,
            include_deleted="1"
        )
        assert refreshed.isDeleted == 1

        # Assertions: Outbox event created
        outbox_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_DELETED",
            OutboxEvent.aggregate_id == str(original_id)
        ).first()

        assert outbox_event is not None
        assert outbox_event.routing_key == f"patient.deleted.{original_id}"

        print(f"DONE: Created DELETE Outbox Event ID: {outbox_event.id}")

        # Verify payload
        payload = outbox_event.get_payload()
        assert payload["deleted_by"] == "test-user-1"
        assert "patient_data" in payload

    def test_delete_nonexistent_patient_fails(self, integration_db, mock_user):
        """
        GIVEN: Non-existent patient ID
        WHEN: delete_patient is called
        THEN: HTTPException raised and no outbox event created

        Goal: This function checks if deleting a non-existent patient is rejected properly and no outbox event is created.
        """
        initial_outbox_count = integration_db.query(OutboxEvent).count()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            delete_patient(
                db=integration_db,
                patient_id=999999,
                user_id=mock_user['id'],
                user_full_name=mock_user['fullname'],
                correlation_id=str(uuid.uuid4())
            )

        assert exc_info.value.status_code == 404

        print(f"\nDONE: Delete of non-existent patient properly rejected")

        # No outbox event created
        final_outbox_count = integration_db.query(OutboxEvent).count()
        assert final_outbox_count == initial_outbox_count


class TestOutboxTransactionAtomicity:
    """Test that patient and outbox events are created atomically"""

    def test_patient_and_outbox_created_together_or_not_at_all(self, integration_db, mock_user, sample_created_patient_data):
        """
        GIVEN: Create operation succeeds
        WHEN: Transaction is committed
        THEN: Both patient and outbox event exist

        Goal: This function checks if the creation of patient and outbox event are atomic - both created or neither.
        """
        initial_patient_count = integration_db.query(Patient).count()
        initial_outbox_count = integration_db.query(OutboxEvent).count()

        patient_data = sample_created_patient_data

        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\nDONE: Created patient ID: {patient.id}")

        final_patient_count = integration_db.query(Patient).count()
        final_outbox_count = integration_db.query(OutboxEvent).count()

        # Both should be created together
        assert final_patient_count == initial_patient_count + 1
        assert final_outbox_count == initial_outbox_count + 1

        print(f"DONE: patient count: {initial_patient_count} → {final_patient_count}")
        print(f"DONE: Outbox count: {initial_outbox_count} → {final_outbox_count}")

        # Verify they reference the same aggregate
        outbox = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(patient.id)
        ).first()
        assert outbox is not None

        print(f"DONE: Verified atomic creation")

    def test_patient_update_and_outbox_created_atomically(self, integration_db, mock_user, sample_created_patient_data,sample_updated_patient_data):
        """
        GIVEN: An existing patient that will be updated
        WHEN: Update operation succeeds
        THEN: patient modification and outbox event creation occur atomically

        Goal: This function checks if updating a patient creates an outbox event with the same data.
        """
        # Create initial patient
        patient_data = sample_created_patient_data

        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        original_id = patient.id
        original_modified_date = patient.modifiedDate

        print(f"\nDONE: Created patient ID: {original_id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Get initial state
        initial_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_UPDATED"
        ).count()

        # Update patient
        update_data = sample_updated_patient_data

        updated_patient = update_patient(
            patient_id= original_id,
            db=integration_db,
            patient=update_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: Updated patient ID: {original_id}")

        # Verify patient was actually modified in the database
        refreshed_patient = get_patient(
            db=integration_db,
            patient_id=original_id,
        )
        assert refreshed_patient.name == "Updated Patient"
        assert refreshed_patient.modifiedDate > original_modified_date  # Timestamp changed
        assert refreshed_patient.ModifiedById == "test-user-1"

        # Verify outbox event was created in the same transaction
        final_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_UPDATED"
        ).count()
        assert final_outbox_count == initial_outbox_count + 1

        print(f"DONE: patient modified and Outbox UPDATED count: {initial_outbox_count} -> {final_outbox_count}")

        # Verify the outbox event references the updated patient
        outbox = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id),
            OutboxEvent.event_type == "PATIENT_UPDATED"
        ).first()
        assert outbox is not None
        assert outbox.routing_key == f"patient.updated.{original_id}"
        assert outbox.created_by == "test-user-1"

        # Verify payload reflects the actual changes
        payload = outbox.get_payload()
        assert payload["patient_id"] == original_id
        assert "changes" in payload
        assert "name" in payload["changes"]
        assert payload["changes"]["name"]["old"] == "Test Patient"
        assert payload["changes"]["name"]["new"] == "Updated Patient"

        print(f"DONE: Verified atomic update - patient modified and outbox event created together")

    def test_patient_delete_and_outbox_created_atomically(self, integration_db, mock_user, sample_created_patient_data):
        """
        GIVEN: An existing patient that will be deleted
        WHEN: Delete operation succeeds
        THEN: patient soft-deletion and outbox event creation occur atomically

        Goal: This function checks if soft-deleting a patient creates an outbox event with the same deletion info.
        """
        # Create initial patient
        patient_data = sample_created_patient_data
        patient = create_patient(
            db=integration_db,
            patient=patient_data,
            user=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        original_id = patient.id
        original_modified_date = patient.modifiedDate

        print(f"\nDONE: Created patient ID: {original_id}")

        # Verify patient is not deleted initially
        assert patient.isDeleted == 0

        # Clear outbox from creation - since we only want to look at the deletion event
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Get initial state
        initial_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_DELETED"
        ).count()

        # Delete patient (soft delete)
        deleted_patient = delete_patient(
            patient_id= original_id,
            db=integration_db,
            user_id=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: Deleted patient ID: {original_id}")

        # verify that patient was soft deleted in database
        refreshed_patient = get_patient_include_deleted(
            db=integration_db,
            patient_id=original_id,
            include_deleted="1",
        )
        assert refreshed_patient is not None
        assert refreshed_patient.isDeleted == 1
        assert refreshed_patient.modifiedDate > original_modified_date
        assert refreshed_patient.ModifiedById == "test-user-1"

        # Verify the patient is NOT retrievable with get_patient
        non_deleted_patient = get_patient(
            patient_id= original_id,
            db=integration_db,
        )
        assert non_deleted_patient is None  # Should not be found

        # Verify outbox event was created in the same transaction
        final_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_DELETED"
        ).count()
        assert final_outbox_count == initial_outbox_count + 1

        print(f"DONE: patient soft-deleted and Outbox DELETED count: {initial_outbox_count} → {final_outbox_count}")

        # Verify the outbox event references the deleted patient
        outbox = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id),
            OutboxEvent.event_type == "PATIENT_DELETED"
        ).first()
        assert outbox is not None
        assert outbox.routing_key == f"patient.deleted.{original_id}"
        assert outbox.created_by == "test-user-1"

        # Verify payload contains deletion information
        payload = outbox.get_payload()
        assert payload["patient_id"] == original_id
        assert payload["deleted_by"] == "test-user-1"
        assert "patient_data" in payload
        assert payload["patient_data"]["name"] == "Test Patient"

        # Verify actual patient in DB has isDeleted == 1 - confirms soft delete actually happened
        final_patient_state = get_patient_include_deleted(
            db=integration_db,
            patient_id=original_id,
            include_deleted="1"
        )
        assert final_patient_state.isDeleted == 1  # The actual deletion happened

        print(f"DONE: Verified atomic deletion - patient soft-deleted and outbox event created together")