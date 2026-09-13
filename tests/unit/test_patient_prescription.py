from datetime import datetime
from unittest import mock
from fastapi import HTTPException

import pytest

from app.crud.patient_prescription_crud import (
    create_prescription,
    delete_prescription,
    get_prescriptions,
    update_prescription,
)
from app.schemas.patient_prescription import (
    PatientPrescription,
    PatientPrescriptionCreate,
    PatientPrescriptionUpdate,
)
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


# TODO: fix this test
# def test_get_prescriptions(db_session_mock):
#     # Mock data
#     mock_prescriptions = [
#         {
#             "Id": 1,
#             "IsDeleted": "1",
#             "PatientId": 1,
#             "Dosage": "500mg",
#             "FrequencyPerDay": 3,
#             "Instruction": "Take after meal",
#             "StartDate": datetime(2023, 1, 1),
#             "EndDate": datetime(2023, 1, 10),
#             "IsAfterMeal": "Yes",
#             "PrescriptionRemarks": "No remarks",
#             "Status": "Active",
#             "CreatedDateTime": datetime(2023, 1, 1, 10, 0),
#             "UpdatedDateTime": datetime(2023, 1, 1, 10, 0),
#             "CreatedById": 1,
#             "UpdatedById": 1
#         },
#         {
#             "Id": 2,
#             "IsDeleted": "1",
#             "PatientId": 2,
#             "Dosage": "250mg",
#             "FrequencyPerDay": 2,
#             "Instruction": "Take before meal",
#             "StartDate": datetime(2023, 2, 1),
#             "EndDate": datetime(2023, 2, 10),
#             "IsAfterMeal": "No",
#             "PrescriptionRemarks": "No remarks",
#             "Status": "Active",
#             "CreatedDateTime": datetime(2023, 2, 1, 10, 0),
#             "UpdatedDateTime": datetime(2023, 2, 1, 10, 0),
#             "CreatedById": 2,
#             "UpdatedById": 2
#         }
#     ]

#     # Mock the query result
#     db_session_mock.query.return_value.all.return_value = mock_prescriptions

#     prescriptions = get_prescriptions(db_session_mock)
#     assert isinstance(prescriptions, list)
#     assert len(prescriptions) == 2

#     for prescription in prescriptions:
#         assert isinstance(prescription, dict)
#         assert "Id" in prescription
#         assert "PatientId" in prescription
#         assert "Dosage" in prescription
#         assert "FrequencyPerDay" in prescription
#         assert "Instruction" in prescription
#         assert "StartDate" in prescription
#         assert "EndDate" in prescription
#         assert "IsAfterMeal" in prescription
#         assert "PrescriptionRemarks" in prescription
#         assert "Status" in prescription
#         assert "CreatedDateTime" in prescription
#         assert "UpdatedDateTime" in prescription
#         assert "CreatedById" in prescription
#         assert "UpdatedById" in prescription


# Mocking the relevant models
@mock.patch("app.models.patient_model.Patient")
@mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
@mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
@mock.patch(
    "app.models.allergy_reaction_type_model.AllergyReactionType"
)  # Ensure AllergyReactionType is mocked
@mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")
@mock.patch("app.models.patient_photo_model.PatientPhoto")
@mock.patch("app.models.patient_photo_list_album_model.PatientPhotoListAlbum")  # Mock PatientPhotoListAlbum
@mock.patch(
    "app.models.patient_assigned_dementia_list_model.PatientAssignedDementiaList"
)
@mock.patch(
    "app.models.patient_assigned_dementia_mapping_model.PatientAssignedDementiaMapping"
)
@mock.patch("app.models.patient_mobility_list_model.PatientMobilityList")  # Mock PatientMobilityList
@mock.patch("app.models.patient_mobility_mapping_model.PatientMobility") 
@mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
@mock.patch("app.models.patient_prescription_model.PatientPrescription")
@mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
@mock.patch("app.models.patient_vital_model.PatientVital")
@mock.patch("app.models.patient_highlight_model.PatientHighlight")
@mock.patch("app.models.allergy_type_model.AllergyType")
@mock.patch(
    "app.models.patient_guardian_relationship_mapping_model.PatientGuardianRelationshipMapping"
)
def test_create_prescription(
    mock_patient,
    mock_patient_guardian,
    mock_patient_allergy_mapping,
    mock_allergy_reaction_type,
    mock_patient_doctor_note,
    mock_patient_photo,
    mock_patient_photo_list,
    mock_patient_assigned_dementia_list,
    mock_patient_assigned_dementia_mapping,
    mock_patient_mobility,
    mock_patient_mobility_list,
    mock_patient_prescription_list,
    mock_patient_prescription,
    mock_patient_vital,
    mock_patient_highlight,
    mock_allergy_type,
    mock_patient_guardian_relationship_mapping,
    db_session_mock,
):
    # If this returns None, it means no existing prescription found
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    data = {
        "IsDeleted": "1",
        "PatientId": 1,
        "Dosage": "500mg",
        "PrescriptionListId": 1,
        "FrequencyPerDay": 3,
        "Instruction": "Take after meal",
        "StartDate": datetime(2023, 1, 1),
        "EndDate": datetime(2023, 1, 10),
        "IsAfterMeal": "Yes",
        "PrescriptionRemarks": "No remarks",
        "Status": "Active",
        "CreatedDateTime": datetime(2023, 1, 1, 10, 0),
        "UpdatedDateTime": datetime(2023, 1, 1, 10, 0),
        "CreatedById": "1",
        "ModifiedById": "1",
    }
    prescription = create_prescription(
        db_session_mock,
        PatientPrescriptionCreate(**data),
        created_by="test_user",       # <--- FIX
        user_full_name="Test User"    # <--- FIX
    )
    assert prescription.PatientId == 1
    assert prescription.Dosage == "500mg"
    assert prescription.FrequencyPerDay == 3
    assert prescription.Instruction == "Take after meal"
    assert prescription.StartDate == datetime(2023, 1, 1)
    assert prescription.EndDate == datetime(2023, 1, 10)
    assert prescription.IsAfterMeal == "Yes"
    assert prescription.PrescriptionRemarks == "No remarks"
    assert prescription.Status == "Active"
    assert prescription.CreatedDateTime is not None
    assert prescription.UpdatedDateTime is not None
    assert prescription.CreatedById == "test_user"
    assert prescription.ModifiedById == "test_user"


def test_update_prescription(db_session_mock):
    # Mock data
    mock_data = mock.MagicMock(
        Id=1,
        PatientId=1,
        PrescriptionListId=1, 
        Dosage="500mg",
        FrequencyPerDay=3,
        Instruction="Take after meal",
        StartDate=datetime(2023, 1, 1),
        EndDate=datetime(2023, 1, 10),
        IsAfterMeal="1",
        PrescriptionRemarks="No remarks",
        Status="Active",
        UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
        ModifiedById="1",
    )
    

    # Set up the mock query to return the mock prescriptions
    #db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [mock_data, None]

    data = {
        "Active": "1",
        "PatientId": 1,
        "Dosage": "500mg",
        "PrescriptionListId": 1,
        "FrequencyPerDay": 3,
        "Instruction": "Take after meal",
        "StartDate": datetime(2023, 1, 1),
        "EndDate": datetime(2023, 1, 10),
        "IsAfterMeal": "1",
        "PrescriptionRemarks": "No remarks",
        "Status": "Active",
        "UpdatedDateTime": datetime(2023, 1, 1, 10, 0),
        "ModifiedById": "1",
    }
    prescription = update_prescription(
        db_session_mock,
        1,
        PatientPrescriptionUpdate(**data),
        modified_by="test_user",       # <--- FIX
        user_full_name="Test User"     # <--- FIX
    )
    db_session_mock.commit.assert_called_once()
    assert prescription.PatientId == 1
    assert prescription.Dosage == "500mg"
    assert prescription.FrequencyPerDay == 3
    assert prescription.Instruction == "Take after meal"
    assert prescription.StartDate == datetime(2023, 1, 1)
    assert prescription.EndDate == datetime(2023, 1, 10)
    assert prescription.IsAfterMeal == "1"
    assert prescription.PrescriptionRemarks == "No remarks"
    assert prescription.Status == "Active"
    assert prescription.UpdatedDateTime == datetime(2023, 1, 1, 10, 0)
    assert prescription.ModifiedById == "test_user"

def test_update_prescription_duplicate_error(db_session_mock):
    #Mock
    mock_existing = mock.MagicMock(
        Id=1, 
        PatientId=1, 
        PrescriptionListId=1, 
        IsDeleted='0'
    )
    
    #Mock a dupe
    mock_duplicate = mock.MagicMock(
        Id=2, 
        PatientId=1, 
        PrescriptionListId=5, 
        IsDeleted='0'
    )

    # Mock query
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_existing, 
        mock_duplicate
    ]

    data = {
        "PatientId": 1,
        "PrescriptionListId": 5, 
        "Dosage": "500mg",
        "FrequencyPerDay": 3,
        "Instruction": "Take after meal",
        "StartDate": datetime(2023, 1, 1),
        "PrescriptionRemarks": "Duplicate attempt",
        "Status": "Active",
        "IsAfterMeal": "1",                
        "UpdatedDateTime": datetime.now(), 
        "ModifiedById": "1"
    }

    # Checking for error
    with pytest.raises(HTTPException) as excinfo:
        update_prescription(
            db_session_mock,
            1,
            PatientPrescriptionUpdate(**data),
            modified_by="test_user",
            user_full_name="Test User"
        )
    
    assert excinfo.value.status_code == 400
    assert "Another prescription with this name already exists" in excinfo.value.detail
    db_session_mock.commit.assert_not_called()


def test_delete_prescription(db_session_mock):
    # Mock data
    mock_data = mock.MagicMock(
        Id=1,
        PatientId=1,
        IsDeleted="0",
    )
    
    # Set up the mock query to return the mock prescriptions
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_data

    data = {
        "IsDeleted": "0",
        "PatientId": 1,
        "PrescriptionListId": 1,
        "Dosage": "500mg",
        "FrequencyPerDay": 3,
        "Instruction": "Take after meal",
        "StartDate": datetime(2023, 1, 1),
        "EndDate": datetime(2023, 1, 10),
        "AfterMeal": "Yes",
        "PrescriptionRemarks": "No remarks",
        "Status": "Active",
        "UpdatedDateTime": datetime(2023, 1, 1, 10, 0),
        "ModifiedById": "1",
    }

    prescription_id = 1
    result = delete_prescription(
        db_session_mock,
        prescription_id,
        modified_by="test_user",      # <--- FIX
        user_full_name="Test User"    # <--- FIX
    )
    # Highlight integration causes 2 comits (prescription + highlight)
    assert db_session_mock.commit.call_count == 2
    assert result.IsDeleted == "1"


def test_create_prescription_forwards_user_full_name_to_highlight_helper(db_session_mock):
    mock_prescription = mock.MagicMock(Id=1, PatientId=1)
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    db_session_mock.query.return_value.options.return_value.filter.return_value.first.return_value = mock_prescription
    db_session_mock.refresh.side_effect = lambda obj: None

    with mock.patch("app.crud.patient_prescription_crud.create_highlight_if_needed") as mock_highlight, \
         mock.patch("app.crud.patient_prescription_crud.log_crud_action"):
        create_prescription(
            db_session_mock,
            PatientPrescriptionCreate(
                PatientId=1,
                PrescriptionListId=1,
                Dosage="500mg",
                FrequencyPerDay=3,
                Instruction="Take after meal",
                StartDate=datetime(2023, 1, 1),
                EndDate=datetime(2023, 1, 10),
                IsAfterMeal="Yes",
                PrescriptionRemarks="No remarks",
                Status="Active",
                CreatedDateTime=datetime(2023, 1, 1, 10, 0),
                UpdatedDateTime=datetime(2023, 1, 1, 10, 0),
                CreatedById="user123",
                ModifiedById="user123",
            ),
            created_by="user123",
            user_full_name="Test User",
        )

    mock_highlight.assert_called_once()
    assert mock_highlight.call_args.kwargs["user_full_name"] == "Test User"


def test_delete_prescription_logs_cascaded_highlight_delete(db_session_mock):
    mock_data = mock.MagicMock(Id=1, PatientId=1, IsDeleted="0")
    mock_patient = mock.MagicMock()
    mock_patient.name = "Jane Doe"
    mock_highlight = mock.MagicMock(
        Id=903, PatientId=1, HighlightTypeId=3, HighlightText="Prescription: Panadol",
        SourceTable="PATIENT_PRESCRIPTION", SourceRecordId=1, IsDeleted=0,
        CreatedById="1", ModifiedById="1",
    )

    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [mock_data, mock_patient]  # prescription lookup, then patient lookup
    mock_query.all.return_value = [mock_highlight]
    db_session_mock.query.return_value = mock_query

    with mock.patch("app.crud.patient_prescription_crud.log_crud_action") as mock_log:
        delete_prescription(
            db_session_mock,
            1,
            modified_by="test_user",
            user_full_name="Test User",
        )

    highlight_calls = [
        c for c in mock_log.call_args_list if c.kwargs["table"] == "PatientHighlight"
    ]
    assert len(highlight_calls) == 1
    assert highlight_calls[0].kwargs["entity_id"] == 903
    assert highlight_calls[0].kwargs["user"] == "test_user"
    assert highlight_calls[0].kwargs["user_full_name"] == "Test User"
    assert highlight_calls[0].kwargs["patient_id"] == 1
    assert highlight_calls[0].kwargs["patient_full_name"] == "Jane Doe"


def test_delete_prescription_logs_cascaded_highlight_delete_multiple_highlights(db_session_mock):
    mock_data = mock.MagicMock(Id=1, PatientId=1, IsDeleted="0")
    mock_patient = mock.MagicMock()
    mock_patient.name = "John Smith"
    mock_highlight_1 = mock.MagicMock(
        Id=901, PatientId=1, HighlightTypeId=3, HighlightText="Prescription: Aspirin",
        SourceTable="PATIENT_PRESCRIPTION", SourceRecordId=1, IsDeleted=0,
        CreatedById="1", ModifiedById="1",
    )
    mock_highlight_2 = mock.MagicMock(
        Id=902, PatientId=1, HighlightTypeId=3, HighlightText="Prescription: Panadol",
        SourceTable="PATIENT_PRESCRIPTION", SourceRecordId=1, IsDeleted=0,
        CreatedById="1", ModifiedById="1",
    )

    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.side_effect = [mock_data, mock_patient]  # prescription lookup, then patient lookup
    mock_query.all.return_value = [mock_highlight_1, mock_highlight_2]
    db_session_mock.query.return_value = mock_query

    with mock.patch("app.crud.patient_prescription_crud.log_crud_action") as mock_log:
        delete_prescription(
            db_session_mock,
            1,
            modified_by="test_user",
            user_full_name="Test User",
        )

    highlight_calls = [
        c for c in mock_log.call_args_list if c.kwargs["table"] == "PatientHighlight"
    ]
    assert len(highlight_calls) == 2

    # Verify both highlights are logged separately with their own entity_ids
    entity_ids = [c.kwargs["entity_id"] for c in highlight_calls]
    assert 901 in entity_ids
    assert 902 in entity_ids

    # Verify all calls have the correct patient name
    for call in highlight_calls:
        assert call.kwargs["patient_full_name"] == "John Smith"
        assert call.kwargs["user"] == "test_user"
        assert call.kwargs["user_full_name"] == "Test User"
        assert call.kwargs["patient_id"] == 1
