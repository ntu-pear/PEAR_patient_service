import pytest
from unittest import mock
from datetime import datetime
from app.crud.patient_prescription_crud import get_prescriptions, create_prescription, update_prescription, delete_prescription
from app.schemas.patient_prescription import PatientPrescriptionCreate, PatientPrescriptionUpdate, PatientPrescription

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
#             "id": 1,
#             "active": "1",
#             "patientId": 1,
#             "dosage": "500mg",
#             "frequencyPerDay": 3,
#             "instruction": "Take after meal",
#             "startDate": datetime(2023, 1, 1),
#             "endDate": datetime(2023, 1, 10),
#             "afterMeal": "Yes",
#             "prescriptionRemarks": "No remarks",
#             "status": "Active",
#             "createdDateTime": datetime(2023, 1, 1, 10, 0),
#             "modifiedDateTime": datetime(2023, 1, 1, 10, 0),
#             "createdById": 1,
#             "modifiedById": 1
#         },
#         {
#             "id": 2,
#             "active": "1",
#             "patientId": 2,
#             "dosage": "250mg",
#             "frequencyPerDay": 2,
#             "instruction": "Take before meal",
#             "startDate": datetime(2023, 2, 1),
#             "endDate": datetime(2023, 2, 10),
#             "afterMeal": "No",
#             "prescriptionRemarks": "No remarks",
#             "status": "Active",
#             "createdDateTime": datetime(2023, 2, 1, 10, 0),
#             "modifiedDateTime": datetime(2023, 2, 1, 10, 0),
#             "createdById": 2,
#             "modifiedById": 2
#         }
#     ]

#     # Mock the query result
#     db_session_mock.query.return_value.all.return_value = mock_prescriptions

#     prescriptions = get_prescriptions(db_session_mock)
#     assert isinstance(prescriptions, list)
#     assert len(prescriptions) == 2

#     for prescription in prescriptions:
#         assert isinstance(prescription, dict)
#         assert "id" in prescription
#         assert "patientId" in prescription
#         assert "dosage" in prescription
#         assert "frequencyPerDay" in prescription
#         assert "instruction" in prescription
#         assert "startDate" in prescription
#         assert "endDate" in prescription
#         assert "afterMeal" in prescription
#         assert "prescriptionRemarks" in prescription
#         assert "status" in prescription
#         assert "createdDateTime" in prescription
#         assert "modifiedDateTime" in prescription
#         assert "createdById" in prescription
#         assert "modifiedById" in prescription

# Mocking the relevant models
@mock.patch("app.models.patient_model.Patient")
@mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
@mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
@mock.patch("app.models.allergy_reaction_type_model.AllergyReactionType")  # Ensure AllergyReactionType is mocked
@mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")
@mock.patch("app.models.patient_photo_model.PatientPhoto")
@mock.patch("app.models.patient_assigned_dementia_model.PatientAssignedDementia")
@mock.patch("app.models.patient_mobility_model.PatientMobility")
@mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
@mock.patch("app.models.patient_prescription_model.PatientPrescription")
@mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
@mock.patch("app.models.patient_vital_model.PatientVital")
@mock.patch("app.models.patient_highlight_model.PatientHighlight")
@mock.patch("app.models.allergy_type_model.AllergyType")
@mock.patch("app.models.patient_guardian_relationship_mapping_model.PatientGuardianRelationshipMapping")
def test_create_prescription(
    mock_patient,  
    mock_patient_guardian, 
    mock_patient_allergy_mapping, 
    mock_allergy_reaction_type, 
    mock_patient_doctor_note, 
    mock_patient_photo,  
    mock_patient_assigned_dementia,  
    mock_patient_mobility,  
    mock_patient_prescription_list,
    mock_patient_prescription,  
    mock_patient_vital,
    mock_patient_highlight,
    mock_allergy_type,
    mock_patient_guardian_relationship_mapping,
    db_session_mock, 
):
    data = {
        "active": "1", 
        "patientId": 1,
        "dosage": "500mg",
        "frequencyPerDay": 3,
        "instruction": "Take after meal",
        "startDate": datetime(2023, 1, 1),
        "endDate": datetime(2023, 1, 10),
        "afterMeal": "Yes",
        "prescriptionRemarks": "No remarks",
        "status": "Active",
        "createdDateTime": datetime(2023, 1, 1, 10, 0),
        "modifiedDateTime": datetime(2023, 1, 1, 10, 0),
        "createdById": 1,
        "modifiedById": 1
    }
    prescription = create_prescription(db_session_mock, PatientPrescriptionCreate(**data))
    assert prescription.patientId == 1
    assert prescription.dosage == "500mg"
    assert prescription.frequencyPerDay == 3
    assert prescription.instruction == "Take after meal"
    assert prescription.startDate == datetime(2023, 1, 1)
    assert prescription.endDate == datetime(2023, 1, 10)
    assert prescription.afterMeal == "Yes"
    assert prescription.prescriptionRemarks == "No remarks"
    assert prescription.status == "Active"
    assert prescription.createdDateTime == datetime(2023, 1, 1, 10, 0)
    assert prescription.modifiedDateTime == datetime(2023, 1, 1, 10, 0)
    assert prescription.createdById == 1
    assert prescription.modifiedById == 1

def test_update_prescription(db_session_mock):
    data = {
        "active": "1",
        "patientId": 1,
        "dosage": "500mg",
        "frequencyPerDay": 3,
        "instruction": "Take after meal",
        "startDate": datetime(2023, 1, 1),
        "endDate": datetime(2023, 1, 10),
        "afterMeal": "Yes",
        "prescriptionRemarks": "No remarks",
        "status": "Active",
        "modifiedDateTime": datetime(2023, 1, 1, 10, 0),
        "modifiedById": 1
    }
    prescription = update_prescription(db_session_mock, 1, PatientPrescriptionUpdate(**data))
    db_session_mock.commit.assert_called_once()
    assert prescription.patientId == 1
    assert prescription.dosage == "500mg"
    assert prescription.frequencyPerDay == 3
    assert prescription.instruction == "Take after meal"
    assert prescription.startDate == datetime(2023, 1, 1)
    assert prescription.endDate == datetime(2023, 1, 10)
    assert prescription.afterMeal == "Yes"
    assert prescription.prescriptionRemarks == "No remarks"
    assert prescription.status == "Active"
    assert prescription.modifiedDateTime == datetime(2023, 1, 1, 10, 0)
    assert prescription.modifiedById == 1

def test_delete_prescription(db_session_mock):
    data = {
        "active": "1",
        "patientId": 1,
        "dosage": "500mg",
        "frequencyPerDay": 3,
        "instruction": "Take after meal",
        "startDate": datetime(2023, 1, 1),
        "endDate": datetime(2023, 1, 10),
        "afterMeal": "Yes",
        "prescriptionRemarks": "No remarks",
        "status": "Active",
        "modifiedDateTime": datetime(2023, 1, 1, 10, 0),
        "modifiedById": 1
    }
    prescription_id = 1
    result = delete_prescription(db_session_mock, prescription_id, PatientPrescriptionUpdate(**data))
    db_session_mock.commit.assert_called_once()
    assert result.active == "0"
