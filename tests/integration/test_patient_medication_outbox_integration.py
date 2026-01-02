"""
Integration tests for Patient Service (Publisher) Outbox Pattern
Tests for flow: Patient Medication CRUD -> OUTBOX_EVENTS table creation
"""
import uuid
from datetime import datetime
from sqlalchemy import text

import pytest
from app.crud.patient_medication_crud import (
    create_medication, update_medication, delete_medication, get_medication_include_deleted, get_medication
)
from app.database import SessionLocal
from app.models import PatientPrescriptionList
from app.models.outbox_model import OutboxEvent
from app.schemas.patient_medication import PatientMedicationCreate, PatientMedicationUpdate
from app.models.patient_medication_model import PatientMedication
from app.models.patient_model import Patient
from app.models.patient_list_language_model import PatientListLanguage

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
        existing_prescription_1 = session_db.query(PatientPrescriptionList).filter_by(Id=1).first()
        existing_prescription_2 = session_db.query(PatientPrescriptionList).filter_by(Id=2).first()

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
        if not existing_prescription_1:
            prescription1 = PatientPrescriptionList(
                Id=1,
                IsDeleted='0',
                CreatedDateTime=datetime.now(),
                UpdatedDateTime=datetime.now(),
                Value="1",
            )
            session_db.add(prescription1)
        if not existing_prescription_2:
            prescription2 = PatientPrescriptionList(
                Id=2,
                IsDeleted='0',
                CreatedDateTime=datetime.now(),
                UpdatedDateTime=datetime.now(),
                Value="2",
            )
            session_db.add(prescription2)
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
def sample_created_patient_medication_data(integration_db):
    # Check if patient with id=100000000 already exists
    existing_patient = integration_db.query(Patient).filter(Patient.id == 100000000).first()

    if not existing_patient:
        # Create a new patient record
        test_patient = Patient(
            id=100000000,
            name="Test Patient",
            nric="S1234567A",
            gender="M",
            dateOfBirth=datetime(1990, 1, 1),
            isApproved="1",
            startDate=datetime(2020, 1, 1),
            isRespiteCare="0",
            createdDate=datetime.now(),
            modifiedDate=datetime.now(),
            CreatedById="test-user-1",
            ModifiedById="test-user-1",
            isDeleted=0,
            preferredLanguageId=1
        )
        integration_db.add(test_patient)
        integration_db.flush()  # Flush to make the patient available for the medication foreign key

    # Return the PatientMedicationCreate object with the valid PatientId
    return PatientMedicationCreate(
        IsDeleted="0",
        PatientId=100000000,  # Now this patient exists
        PrescriptionListId=1,
        AdministerTime="Test Administer Time",
        Dosage="Test Dosage",
        Instruction="Test Instruction",
        StartDate=datetime(2020, 1, 1),
        EndDate=datetime(2020, 1, 1),
        PrescriptionRemarks="Test Prescription Remarks",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById="test-user-1",
        ModifiedById="test-user-1",
    )
@pytest.fixture
def sample_updated_patient_medication_data():
    return PatientMedicationUpdate(
        IsDeleted="0",
        PatientId=100000000,
        PrescriptionListId=2,
        AdministerTime="Updated Administer Time",
        Dosage="Updated Dosage",
        Instruction="Updated Instruction",
        StartDate=datetime(2020, 1, 1),
        EndDate=datetime(2020, 1, 1),
        PrescriptionRemarks="Updated Prescription Remarks",
        UpdatedDateTime=datetime.now(),
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
        # Delete all outbox events created by test user
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.created_by == "test-user-1"
        ).delete()
        integration_db.commit()

        # Delete all patients created by test user
        integration_db.query(PatientMedication).filter(
            PatientMedication.CreatedById == "test-user-1"
        ).delete()
        integration_db.commit()

        integration_db.query(Patient).filter(
            Patient.CreatedById == "test-user-1"
        ).delete()
        integration_db.commit()
        print("\n[CLEANUP] Test data cleared successfully")
        
    except Exception as e:
        integration_db.rollback()
        print(f"\n[CLEANUP] Warning: Failed to cleanup test data: {str(e)}")

class TestPatientMedicationCreateOutbox:
    def test_create_medication_medication_creates_outbox(self, integration_db, mock_user, sample_created_patient_medication_data):
        """
        GIVEN: Patient Medication data
        WHEN: create_medication is called
        THEN: PatientMedication and OutboxEvent are created atomically.

        Goal: Check if the creation of PatientMedication also creates an OutboxEvent. This function checks if the created records are the same
        """
        medication_data = sample_created_patient_medication_data

        # create patient medication
        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\n[DONE]: Created Medication ID: {medication.Id}")
        print(f"Prescription Remarks: {medication.PrescriptionRemarks}")
        print(f"Prescription Instructions: {medication.Instruction}")
        print(f"Medication Created By: {medication.CreatedById}")

        # Assert if medication is created
        assert medication.Id is not None
        assert medication.AdministerTime == "Test Administer Time"
        assert medication.PatientId == 100000000
        assert medication.CreatedById == 'test-user-1'
        assert medication.IsDeleted == '0'

        # Assert that outbox event is created
        outbox_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(medication.Id)
        ).first()

        assert outbox_event is not None
        assert outbox_event.event_type == "PATIENT_MEDICATION_CREATED"
        assert outbox_event.aggregate_id == str(medication.Id)
        assert outbox_event.routing_key == f"patient.medication.created.{medication.Id}"

        print(f"\n[DONE]: Created OutboxEvent ID: {outbox_event.id}")
        print(f" Event Type: {outbox_event.event_type}")
        print(f" Correlation ID: {outbox_event.correlation_id}")

        # Verify payload
        payload = outbox_event.get_payload()
        assert payload["event_type"] == "PATIENT_MEDICATION_CREATED"
        assert payload["medication_id"] == medication.Id
        assert payload["created_by"] == "test-user-1"
        assert "correlation_id" in payload
        assert "timestamp" in payload

class TestPatientMedicationUpdateOutbox:
    def test_update_medication_medication_creates_outbox_event(self, integration_db, mock_user, sample_created_patient_medication_data, sample_updated_patient_medication_data):
        """
        GIVEN: An existing Medication
        WHEN: update_medication is called with changes
        THEN: OutboxEvent records changes atomically

        Goal: This function checks if updating a medication creates an outbox event with the changes.
        """
        # create initial medication
        medication_data = sample_created_patient_medication_data

        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        original_id = medication.Id

        print(f"\n[DONE]: Created Medication ID: {medication.Id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Update medication
        update_data = sample_updated_patient_medication_data

        updated_medication = update_medication(
            medication_id= original_id,
            db=integration_db,
            medication_data=update_data,
            modified_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        print(f"\n[DONE]: Updated Medication ID: {original_id}")

        # Assert that Medication is updated
        assert updated_medication.PrescriptionListId == 2
        assert updated_medication.AdministerTime == "Updated Administer Time"
        assert updated_medication.Instruction == "Updated Instruction"

        # Assert that outbox event is created
        outbox_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_UPDATED",
            OutboxEvent.aggregate_id == str(original_id)
        ).first()

        assert outbox_event is not None
        assert outbox_event.routing_key == f"patient.medication.updated.{original_id}"

        print(f"DONE: Created UPDATE Outbox Event ID: {outbox_event.id}")

        # Verify payload contains changes
        payload = outbox_event.get_payload()
        assert "changes" in payload
        assert "PrescriptionRemarks" in payload["changes"]
        assert payload["changes"]["PrescriptionRemarks"]["old"] == "Test Prescription Remarks"
        assert payload["changes"]["PrescriptionRemarks"]["new"] == "Updated Prescription Remarks"

    def test_update_with_no_changes_does_not_create_outbox(self, integration_db, mock_user, sample_created_patient_medication_data, sample_updated_patient_medication_data):
        """
        GIVEN: An existing Medication
        WHEN: update_medication is called with no actual changes
        THEN: No new OutboxEvent is created for PATIENT_MEDICATION_UPDATED
        NOTE: This function will create one extra record in the PatientMedication table, and no record in Outbox table.

        Goal: This function checks if updating a patient with no actual changes does NOT create an outbox event.
        """
        # Create medication
        medication_data = sample_created_patient_medication_data
        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\nDONE: Created Medication ID: {medication.Id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(medication.Id)
        ).delete()
        integration_db.commit()

        # "Update" with same values (no actual changes)
        update_data = sample_created_patient_medication_data
        update_medication(
            medication_id=medication.Id,
            medication_data=update_data,
            db=integration_db,
            modified_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: No-change update processed")

        # No new PATIENT_MEDICATION_UPDATED event should be created
        updated_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_UPDATED",
            OutboxEvent.aggregate_id == str(medication.Id)
        ).first()

        assert updated_event is None
        print(f"DONE: Verified no UPDATE event created")

    def test_update_nonexistent_medication_fails(self, integration_db, mock_user, sample_updated_patient_medication_data):
        """
        GIVEN: Non-existent medication ID
        WHEN: update_medication is called
        THEN: HTTPException raised and no outbox event created

        Goal: This function checks if updating a non-existent medication is rejected properly and no outbox event is created.
        """
        initial_outbox_count = integration_db.query(OutboxEvent).count()

        update_data = sample_updated_patient_medication_data

        result = update_medication(
            medication_id=999999999999,
            db=integration_db,
            medication_data=update_data,
            modified_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        assert result is None

        print(f"\nDONE: Update of non-existent medication properly rejected")

        # No outbox event created
        final_outbox_count = integration_db.query(OutboxEvent).count()
        assert final_outbox_count == initial_outbox_count

class TestPatientMedicationDeleteOutbox:
    def test_delete_medication_creates_outbox_event(self, integration_db, mock_user, sample_created_patient_medication_data):
        """
        GIVEN: An existing medication
        WHEN: delete_medication is called
        THEN: OutboxEvent records deletion atomically

        Goal: This function checks if soft-deleting a medication creates an outbox event with the deletion info.
        """
        # Create medication
        medication_data = sample_created_patient_medication_data
        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        original_id = medication.Id

        print(f"\nDONE: Created Medication ID: {original_id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Delete medication
        deleted_medication = delete_medication(
            medication_id= original_id,
            db=integration_db,
            modified_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: Deleted Medication ID: {original_id}")

        # Assertions: Patient soft-deleted
        assert deleted_medication.IsDeleted == '1'

        # There is no get_patient_by_id in the patient_crud thus unable to assert refreshed = get_patient
        refreshed = get_medication_include_deleted(
            db=integration_db,
            medication_id=original_id,
            include_deleted="1"
        )
        assert refreshed.IsDeleted == '1'

        # Assertions: Outbox event created
        outbox_event = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_DELETED",
            OutboxEvent.aggregate_id == str(original_id)
        ).first()

        assert outbox_event is not None
        assert outbox_event.routing_key == f"patient.medication.deleted.{original_id}"

        print(f"DONE: Created DELETE Outbox Event ID: {outbox_event.id}")

        # Verify payload
        payload = outbox_event.get_payload()
        assert payload["deleted_by"] == "test-user-1"
        assert "medication_data" in payload

    def test_delete_nonexistent_medication_fails(self, integration_db, mock_user):
        """
        GIVEN: Non-existent medication ID
        WHEN: delete_medication is called
        THEN: HTTPException raised and no outbox event created

        Goal: This function checks if deleting a non-existent medication is rejected properly and no outbox event is created.
        """
        initial_outbox_count = integration_db.query(OutboxEvent).count()

        result = delete_medication(
                db=integration_db,
                medication_id=999999,
                modified_by=mock_user['id'],
                user_full_name=mock_user['fullname'],
                correlation_id=str(uuid.uuid4())
            )

        assert result is None

        print(f"\nDONE: Delete of non-existent medication properly rejected")

        # No outbox event created
        final_outbox_count = integration_db.query(OutboxEvent).count()
        assert final_outbox_count == initial_outbox_count


class TestOutboxTransactionAtomicity:
    """Test that medication and outbox events are created atomically"""

    def test_medication_and_outbox_created_together_or_not_at_all(self, integration_db, mock_user, sample_created_patient_medication_data):
        """
        GIVEN: Create operation succeeds
        WHEN: Transaction is committed
        THEN: Both medication and outbox event exist

        Goal: This function checks if the creation of medication and outbox event are atomic - both created or neither.
        """
        initial_medication_count = integration_db.query(PatientMedication).count()
        initial_outbox_count = integration_db.query(OutboxEvent).count()

        medication_data = sample_created_patient_medication_data

        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"\nDONE: Created medication ID: {medication.Id}")

        final_medication_count = integration_db.query(PatientMedication).count()
        final_outbox_count = integration_db.query(OutboxEvent).count()

        # Both should be created together
        assert final_medication_count == initial_medication_count + 1
        assert final_outbox_count == initial_outbox_count + 1

        print(f"DONE: Medication count: {initial_medication_count} → {final_medication_count}")
        print(f"DONE: Outbox count: {initial_outbox_count} → {final_outbox_count}")

        # Verify they reference the same aggregate
        outbox = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(medication.Id)
        ).first()
        assert outbox is not None

        print(f"DONE: Verified atomic creation")

    def test_medication_update_and_outbox_created_atomically(self, integration_db, mock_user, sample_created_patient_medication_data,sample_updated_patient_medication_data):
        """
        GIVEN: An existing medication that will be updated
        WHEN: Update operation succeeds
        THEN: medication modification and outbox event creation occur atomically

        Goal: This function checks if updating a medication creates an outbox event with the same data.
        """
        # Create initial medication
        medication_data = sample_created_patient_medication_data

        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        original_id = medication.Id
        original_modified_date = medication.UpdatedDateTime

        print(f"\nDONE: Created medication ID: {original_id}")

        # Clear outbox from creation
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Get initial state
        initial_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_UPDATED"
        ).count()

        # Update patient
        update_data = sample_updated_patient_medication_data

        updated_medication = update_medication(
            medication_id= original_id,
            db=integration_db,
            medication_data=update_data,
            modified_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: Updated medication ID: {original_id}")

        # Verify medication was actually modified in the database
        refreshed_medication = get_medication(
            db=integration_db,
            medication_id=original_id,
        )
        assert refreshed_medication.Instruction == "Updated Instruction"
        assert refreshed_medication.UpdatedDateTime > original_modified_date  # Timestamp changed
        assert refreshed_medication.ModifiedById == "test-user-1"

        # Verify outbox event was created in the same transaction
        final_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_UPDATED"
        ).count()
        assert final_outbox_count == initial_outbox_count + 1

        print(f"DONE: Medication modified and Outbox UPDATED count: {initial_outbox_count} -> {final_outbox_count}")

        # Verify the outbox event references the updated patient
        outbox = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id),
            OutboxEvent.event_type == "PATIENT_MEDICATION_UPDATED"
        ).first()
        assert outbox is not None
        assert outbox.routing_key == f"patient.medication.updated.{original_id}"
        assert outbox.created_by == "test-user-1"

        # Verify payload reflects the actual changes
        payload = outbox.get_payload()
        assert payload["medication_id"] == original_id
        assert "changes" in payload
        assert "PrescriptionRemarks" in payload["changes"]
        assert payload["changes"]["PrescriptionRemarks"]["old"] == "Test Prescription Remarks"
        assert payload["changes"]["PrescriptionRemarks"]["new"] == "Updated Prescription Remarks"

        print(f"DONE: Verified atomic update - patient modified and outbox event created together")

    def test_medication_delete_and_outbox_created_atomically(self, integration_db, mock_user, sample_created_patient_medication_data):
        """
        GIVEN: An existing medication that will be deleted
        WHEN: Delete operation succeeds
        THEN: patient soft-deletion and outbox event creation occur atomically

        Goal: This function checks if soft-deleting a patient creates an outbox event with the same deletion info.
        """
        # Create initial medication
        medication_data = sample_created_patient_medication_data
        medication = create_medication(
            db=integration_db,
            medication_data=medication_data,
            created_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )
        original_id = medication.Id
        original_modified_date = medication.UpdatedDateTime

        print(f"\nDONE: Created patient ID: {original_id}")

        # Verify medication is not deleted initially
        assert medication.IsDeleted == '0'

        # Clear outbox from creation - since we only want to look at the deletion event
        integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id)
        ).delete()
        integration_db.commit()

        # Get initial state
        initial_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_DELETED"
        ).count()

        # Delete medication (soft delete)
        deleted_medication = delete_medication(
            medication_id= original_id,
            db=integration_db,
            modified_by=mock_user['id'],
            user_full_name=mock_user['fullname'],
            correlation_id=str(uuid.uuid4())
        )

        print(f"DONE: Deleted medication ID: {original_id}")

        # verify that medication was soft deleted in database
        refreshed_medication = get_medication_include_deleted(
            db=integration_db,
            medication_id=original_id,
            include_deleted="1",
        )
        assert refreshed_medication is not None
        assert refreshed_medication.IsDeleted == '1'
        assert refreshed_medication.UpdatedDateTime > original_modified_date
        assert refreshed_medication.ModifiedById == "test-user-1"

        # Verify the medication is NOT retrievable with get_medication
        non_deleted_medication = get_medication(
            medication_id= original_id,
            db=integration_db,
        )
        assert non_deleted_medication is None  # Should not be found

        # Verify outbox event was created in the same transaction
        final_outbox_count = integration_db.query(OutboxEvent).filter(
            OutboxEvent.event_type == "PATIENT_MEDICATION_DELETED"
        ).count()
        assert final_outbox_count == initial_outbox_count + 1

        print(f"DONE: patient soft-deleted and Outbox DELETED count: {initial_outbox_count} → {final_outbox_count}")

        # Verify the outbox event references the deleted patient
        outbox = integration_db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == str(original_id),
            OutboxEvent.event_type == "PATIENT_MEDICATION_DELETED"
        ).first()
        assert outbox is not None
        assert outbox.routing_key == f"patient.medication.deleted.{original_id}"
        assert outbox.created_by == "test-user-1"

        # Verify payload contains deletion information
        payload = outbox.get_payload()
        assert payload["medication_id"] == original_id
        assert payload["deleted_by"] == "test-user-1"
        assert "medication_data" in payload
        assert payload["medication_data"]["PrescriptionRemarks"] == "Test Prescription Remarks"

        # Verify actual patient in DB has isDeleted == '1' - confirms soft delete actually happened
        final_medication_state = get_medication_include_deleted(
            db=integration_db,
            medication_id=original_id,
            include_deleted="1"
        )
        assert final_medication_state.IsDeleted == '1'  # The actual deletion happened

        print(f"DONE: Verified atomic deletion - patient soft-deleted and outbox event created together")