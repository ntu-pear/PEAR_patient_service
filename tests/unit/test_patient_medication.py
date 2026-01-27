from datetime import datetime
from unittest import mock

import pytest

from app.crud.patient_medication_crud import (
    create_medication,
    delete_medication,
    get_medication,
    get_medications,
    get_patient_medications,
    update_medication,
)
from app.schemas.patient_medication import (
    PatientMedication,
    PatientMedicationCreate,
    PatientMedicationUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_get_medications(db_session_mock):
    # Mock data based on the actual dataset
    mock_medications = [
        mock.MagicMock(
            Id=1,
            IsDeleted="0",
            PatientId=1,
            PrescriptionListId=1,
            AdministerTime="1030",
            Dosage="2 tabs",
            Instruction="Always leave at least 4 hours between doses",
            StartDate=datetime(2023, 1, 1),
            EndDate=datetime(2023, 12, 31),
            PrescriptionRemarks="Take with food",
            CreatedDateTime=datetime(2023, 1, 1, 10, 54, 34),
            UpdatedDateTime=datetime(2023, 1, 1, 11, 35, 5),
            CreatedById="1",
            ModifiedById="1"
        ),
        mock.MagicMock(
            Id=2,
            IsDeleted="0",
            PatientId=2,
            PrescriptionListId=2,
            AdministerTime="1300",
            Dosage="10 ml",
            Instruction="To be eaten after meals",
            StartDate=datetime(2023, 2, 1),
            EndDate=datetime(2023, 2, 28),
            PrescriptionRemarks="Shake well before use",
            CreatedDateTime=datetime(2023, 2, 1, 9, 54, 34),
            UpdatedDateTime=datetime(2023, 2, 1, 9, 54, 34),
            CreatedById="2",
            ModifiedById="2"
        ),
        mock.MagicMock(
            Id=33,
            IsDeleted="0", 
            PatientId=2,
            PrescriptionListId=10,
            AdministerTime="1346",
            Dosage="2 Pills a day",
            Instruction="Take twice a day",
            StartDate=datetime(2023, 4, 17),
            EndDate=datetime(2023, 5, 17),
            PrescriptionRemarks="NIL",
            CreatedDateTime=datetime(2023, 4, 17, 14, 44, 44),
            UpdatedDateTime=datetime(2023, 4, 17, 14, 44, 44),
            CreatedById="3",
            ModifiedById="3"
        )
    ]

    # Mock the query result
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = len(mock_medications)
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_medications
    
    db_session_mock.query.return_value = mock_query

    medications, total_records, total_pages = get_medications(db_session_mock, pageNo=0, pageSize=10)
    
    assert isinstance(medications, list)
    assert len(medications) == 3
    assert total_records == 3
    assert total_pages == 1

    # Test first medication (Ibuprofen-like)
    first_med = medications[0]
    assert first_med.Id == 1
    assert first_med.PatientId == 1
    assert first_med.AdministerTime == "1030"
    assert first_med.Dosage == "2 tabs"
    assert "4 hours between doses" in first_med.Instruction


def test_get_patient_medications(db_session_mock):
    # Mock data for patient ID 2
    mock_medications = [
        mock.MagicMock(
            Id=2,
            IsDeleted="0",
            PatientId=2,
            PrescriptionListId=2,
            AdministerTime="1300",
            Dosage="10 ml",
            Instruction="To be eaten after meals",
            StartDate=datetime(2023, 2, 1),
            EndDate=datetime(2023, 2, 28),
            PrescriptionRemarks="None",
            CreatedDateTime=datetime(2023, 2, 1, 9, 54, 34),
            UpdatedDateTime=datetime(2023, 2, 1, 9, 54, 34),
            CreatedById="2",
            ModifiedById="2"
        ),
        mock.MagicMock(
            Id=33,
            IsDeleted="0",
            PatientId=2,
            PrescriptionListId=10,
            AdministerTime="1346",
            Dosage="2 Pills a day",
            Instruction="Take twice a day",
            StartDate=datetime(2023, 4, 17),
            EndDate=datetime(2023, 5, 17),
            PrescriptionRemarks="NIL",
            CreatedDateTime=datetime(2023, 4, 17, 14, 44, 44),
            UpdatedDateTime=datetime(2023, 4, 17, 14, 44, 44),
            CreatedById="3",
            ModifiedById="3"
        )
    ]

    # Mock the query result
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = len(mock_medications)
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_medications
    
    db_session_mock.query.return_value = mock_query

    medications, total_records, total_pages = get_patient_medications(db_session_mock, patient_id=2, pageNo=0, pageSize=100)
    
    assert isinstance(medications, list)
    assert len(medications) == 2
    assert total_records == 2
    assert total_pages == 1
    
    # Verify all medications belong to patient 2
    for medication in medications:
        assert medication.PatientId == 2


def test_get_medication(db_session_mock):
    # Mock data based on Memantine medication (ID 4 in real data)
    mock_medication = mock.MagicMock(
        Id=4,
        IsDeleted="0",
        PatientId=4,
        PrescriptionListId=4,
        AdministerTime="1115",
        Dosage="4 tabs",
        Instruction="Nil",
        StartDate=datetime(2023, 3, 1),
        EndDate=datetime(2023, 12, 31),
        PrescriptionRemarks="None",
        CreatedDateTime=datetime(2023, 3, 1, 8, 54, 34),
        UpdatedDateTime=datetime(2023, 3, 1, 9, 34, 44),
        CreatedById="4",
        ModifiedById="4"
    )

    # Mock the query result
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_medication
    
    db_session_mock.query.return_value = mock_query

    medication = get_medication(db_session_mock, medication_id=4)
    
    assert medication is not None
    assert medication.Id == 4
    assert medication.PatientId == 4
    assert medication.AdministerTime == "1115"
    assert medication.Dosage == "4 tabs"
    assert medication.Instruction == "Nil"


def test_create_medication(db_session_mock):
    """Test creating a medication with prescription name handling"""
    # Create test data based on real medication patterns
    medication_data = {
        "IsDeleted": "0",
        "PatientId": 5,
        "PrescriptionListId": 8,
        "AdministerTime": "0945",
        "Dosage": "2 tabs",
        "Instruction": "Take with morning meal",
        "StartDate": datetime(2023, 5, 1),
        "EndDate": datetime(2023, 11, 30),
        "PrescriptionRemarks": "Monitor for side effects",
        "CreatedDateTime": datetime(2023, 5, 1, 10, 0, 0),
        "UpdatedDateTime": datetime(2023, 5, 1, 10, 0, 0),
        "CreatedById": "doctor123",
        "ModifiedById": "doctor123",
    }

    # Create mock medication instance with ALL necessary attributes
    mock_medication_instance = mock.MagicMock()
    mock_medication_instance.Id = 1043
    mock_medication_instance.PatientId = 5
    mock_medication_instance.PrescriptionListId = 8
    mock_medication_instance.AdministerTime = "0945"
    mock_medication_instance.Dosage = "2 tabs"
    mock_medication_instance.Instruction = "Take with morning meal"
    mock_medication_instance.StartDate = datetime(2023, 5, 1)
    mock_medication_instance.EndDate = datetime(2023, 11, 30)
    mock_medication_instance.PrescriptionRemarks = "Monitor for side effects"
    mock_medication_instance.CreatedDateTime = datetime(2023, 5, 1, 10, 0, 0)
    mock_medication_instance.UpdatedDateTime = datetime(2023, 5, 1, 10, 0, 0)
    mock_medication_instance.CreatedById = "test_user"
    mock_medication_instance.ModifiedById = "test_user"
    mock_medication_instance.IsDeleted = "0"
    
    # IMPORTANT: Add PrescriptionName attribute for testing
    mock_medication_instance.PrescriptionName = "Aspirin 100mg"
    
    # Mock the prescription relationship (this is what was causing the test to fail)
    mock_prescription = mock.MagicMock()
    mock_prescription.Value = "Aspirin 100mg"
    mock_medication_instance.prescription_list = mock_prescription
    
    # Mock database operations
    db_session_mock.add = mock.MagicMock()
    db_session_mock.commit = mock.MagicMock()
    db_session_mock.refresh = mock.MagicMock()
    db_session_mock.flush = mock.MagicMock()
    db_session_mock.rollback = mock.MagicMock()
    
    # Mock the query chain for _get_medication_with_prescription_name
    mock_query = mock.MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_medication_instance
    db_session_mock.query.return_value = mock_query

    # Mock the PatientMedication constructor
    with mock.patch('app.crud.patient_medication_crud.PatientMedication') as mock_patient_medication:
        mock_patient_medication.return_value = mock_medication_instance
        
        # Mock the outbox service
        with mock.patch('app.crud.patient_medication_crud.get_outbox_service') as mock_get_outbox_service:
            mock_outbox_service = mock.MagicMock()
            mock_outbox_event = mock.MagicMock()
            mock_outbox_event.id = "test-outbox-id"
            mock_outbox_service.create_event.return_value = mock_outbox_event
            mock_get_outbox_service.return_value = mock_outbox_service
            
            # Mock the logging function
            with mock.patch('app.crud.patient_medication_crud.log_crud_action') as mock_log_crud_action:
                
                # Execute the test
                medication = create_medication(
                    db_session_mock,
                    PatientMedicationCreate(**medication_data),
                    created_by="test_user",
                    user_full_name="Test User"
                )

                # Assertions
                assert medication is not None
                assert medication.Id == 1043
                assert medication.PatientId == 5
                assert medication.PrescriptionListId == 8
                
                # Verify database operations were called
                db_session_mock.add.assert_called_once()
                assert db_session_mock.flush.call_count == 2
                assert db_session_mock.commit.call_count == 2
                assert db_session_mock.refresh.call_count == 2
                db_session_mock.refresh.assert_called_with(mock_medication_instance)
                
                # Verify outbox event was created
                mock_outbox_service.create_event.assert_called_once()
                
                # Get the event payload from the call
                call_args = mock_outbox_service.create_event.call_args
                event_payload = call_args[1]['payload']  # Get the payload from kwargs
                
                # Verify the event payload contains prescription name
                assert event_payload['event_type'] == 'PATIENT_MEDICATION_CREATED'
                assert event_payload['medication_id'] == 1043
                assert event_payload['patient_id'] == 5
                
                # IMPORTANT: Check that prescription name is included
                medication_data_in_payload = event_payload['medication_data']
                assert 'PrescriptionName' in medication_data_in_payload
                assert medication_data_in_payload['PrescriptionName'] == "Aspirin 100mg"
                
                # Verify logging was called
                mock_log_crud_action.assert_called_once()

from datetime import datetime
from unittest import mock

import pytest

from app.crud.patient_medication_crud import update_medication
from app.schemas.patient_medication import PatientMedicationUpdate


def test_update_medication(db_session_mock):
    """Test updating a medication with prescription name handling"""

    # -------------------------
    # Mock medication object
    # -------------------------
    class MockMedication:
        def __init__(self):
            self.Id = 6
            self.PatientId = 5
            self.PrescriptionListId = 6
            self.AdministerTime = "0930"
            self.Dosage = "2 puffs"
            self.Instruction = "Nil"
            self.StartDate = datetime(2023, 5, 1)
            self.EndDate = datetime(2023, 12, 31)
            self.PrescriptionRemarks = "None"
            self.UpdatedDateTime = datetime(2023, 5, 1, 9, 0, 0)
            self.ModifiedById = "5"
            self.IsDeleted = "0"

            self.__dict__ = self.__dict__

    mock_medication = MockMedication()

    # -------------------------
    # Mock prescriptions
    # -------------------------
    class MockPrescription:
        def __init__(self, value):
            self.Value = value
            self.IsDeleted = "0"

    old_prescription = MockPrescription("Old Medicine Name")
    new_prescription = MockPrescription("New Medicine Name")

    # -------------------------
    # Mock query behavior
    # -------------------------
    prescription_call_count = 0

    def mock_query(model):
        nonlocal prescription_call_count
        query = mock.MagicMock()
        query.filter.return_value = query

        if "PatientPrescriptionList" in str(model):
            prescription_call_count += 1
            query.first.return_value = (
                old_prescription if prescription_call_count == 1 else new_prescription
            )
        else:
            query.first.return_value = mock_medication

        return query

    db_session_mock.query.side_effect = mock_query
    db_session_mock.flush = mock.MagicMock()
    db_session_mock.commit = mock.MagicMock()
    db_session_mock.refresh = mock.MagicMock()
    db_session_mock.rollback = mock.MagicMock()

    # -------------------------
    # Update payload
    # -------------------------
    update_data = {
        "IsDeleted": "0",
        "PatientId": 5,
        "PrescriptionListId": 8,
        "AdministerTime": "0930",
        "Dosage": "2 puffs",
        "Instruction": "Use as needed for breathing difficulties",
        "StartDate": datetime(2023, 5, 1),
        "EndDate": datetime(2023, 12, 31),
        "PrescriptionRemarks": "Updated: Use spacer device",
        "UpdatedDateTime": datetime(2023, 5, 15, 14, 30, 0),
        "ModifiedById": "nurse456",
    }

    # -------------------------
    # Mock outbox + logging
    # -------------------------
    with mock.patch(
        "app.crud.patient_medication_crud.get_outbox_service"
    ) as mock_get_outbox_service, mock.patch(
        "app.crud.patient_medication_crud.log_crud_action"
    ) as mock_log_crud_action:

        mock_outbox_service = mock.MagicMock()
        mock_outbox_event = mock.MagicMock()
        mock_outbox_event.id = "test-outbox-id"
        mock_outbox_service.create_event.return_value = mock_outbox_event
        mock_get_outbox_service.return_value = mock_outbox_service

        # -------------------------
        # Execute
        # -------------------------
        medication = update_medication(
            db_session_mock,
            6,
            PatientMedicationUpdate(**update_data),
            modified_by="test_user",
            user_full_name="Test User",
        )

        # -------------------------
        # Assertions
        # -------------------------
        assert medication is not None
        assert medication.Id == 6
        assert medication.PatientId == 5

        mock_outbox_service.create_event.assert_called_once()

        payload = mock_outbox_service.create_event.call_args.kwargs["payload"]

        assert payload["event_type"] == "PATIENT_MEDICATION_UPDATED"
        assert payload["medication_id"] == 6
        assert payload["patient_id"] == 5

        assert payload["old_data"]["PrescriptionName"] == "Old Medicine Name"
        assert payload["new_data"]["PrescriptionName"] == "New Medicine Name"
        assert len(payload["changes"]) > 0

        mock_log_crud_action.assert_called_once()


def test_delete_medication(db_session_mock):
    # Create a simple mock medication
    mock_medication = mock.MagicMock()
    
    # Set up attributes directly
    mock_medication.Id = 1034
    mock_medication.PatientId = 7
    mock_medication.IsDeleted = "0"
    mock_medication.PrescriptionListId = 15
    mock_medication.AdministerTime = "1910"
    mock_medication.Dosage = "2 times"
    mock_medication.Instruction = "TAKE CARE OF INSTRUCTIONS"
    mock_medication.StartDate = datetime(2023, 6, 1)
    mock_medication.EndDate = datetime(2023, 12, 31)
    mock_medication.PrescriptionRemarks = "TAKE NOTES/REMARKS"

    # Set up the mock query
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_medication
    db_session_mock.query.return_value = mock_query

    medication_id = 1034
    result = delete_medication(
        db_session_mock,
        medication_id,
        modified_by="test_user",
        user_full_name="Test User"
    )

    # Verify database operations
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()

    # Verify soft delete - the mock should have IsDeleted set to "1"
    assert result == mock_medication
    assert result.IsDeleted == "1"


def test_get_medication_not_found(db_session_mock):
    # Mock the query to return None (medication not found)
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    
    db_session_mock.query.return_value = mock_query

    medication = get_medication(db_session_mock, medication_id=9999)
    
    assert medication is None


def test_update_medication_not_found(db_session_mock):
    # Mock the query to return None (medication not found)
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    
    db_session_mock.query.return_value = mock_query

    update_data = {
        "IsDeleted": "0",
        "PatientId": 1,
        "PrescriptionListId": 1,
        "AdministerTime": "1200",
        "Dosage": "1 tab",
        "Instruction": "Take with food",
        "StartDate": datetime(2023, 1, 1),
        "EndDate": datetime(2023, 12, 31),
        "PrescriptionRemarks": "Updated remarks",
        "UpdatedDateTime": datetime(2023, 1, 1, 12, 0, 0),
        "ModifiedById": "1",
    }

    result = update_medication(
        db_session_mock,
        9999,
        PatientMedicationUpdate(**update_data),
        modified_by="test_user",
        user_full_name="Test User"
    )

    assert result is None


def test_delete_medication_not_found(db_session_mock):
    # Mock the query to return None (medication not found)
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    
    db_session_mock.query.return_value = mock_query

    result = delete_medication(
        db_session_mock,
        9999,
        modified_by="test_user",
        user_full_name="Test User"
    )

    assert result is None
