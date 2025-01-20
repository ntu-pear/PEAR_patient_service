import pytest
from unittest import mock
from datetime import datetime
from app.crud.patient_vital_crud import (
    get_vital_list,
    create_vital,
    update_vital,
    delete_vital,
)
from app.schemas.patient_vital import (
    PatientVitalCreate,
    PatientVitalUpdate,
    PatientVitalDelete,
)
from app.models.patient_vital_model import PatientVital

from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


# Mocking the relevant models
@mock.patch("app.models.patient_model.Patient")
@mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
@mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
@mock.patch(
    "app.models.allergy_reaction_type_model.AllergyReactionType"
)  # Ensure AllergyReactionType is mocked
@mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")
@mock.patch("app.models.patient_photo_model.PatientPhoto")
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
def test_create_patient_vital(
    mock_patient,
    mock_patient_guardian,
    mock_patient_allergy_mapping,
    mock_allergy_reaction_type,
    mock_patient_doctor_note,
    mock_patient_photo,
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
    vital_create,
):
    """Test case for creating a patient vital."""

    # Arrange
    mock_patient_vital.return_value = PatientVital(
        **vital_create.model_dump(),
        Id=1,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now()
    )

    # Act
    result = create_vital(db_session_mock, vital_create)

    # Assert
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(result)
    assert result.PatientId == vital_create.PatientId
    assert result.SystolicBP == vital_create.SystolicBP
    assert result.DiastolicBP == vital_create.DiastolicBP
    assert result.Temperature == vital_create.Temperature
    assert result.VitalRemarks == vital_create.VitalRemarks


@mock.patch("app.models.patient_vital_model.PatientVital")
def test_update_patient_vital(mock_patient_vital, db_session_mock, vital_update):
    """Test case for updating a patient vital."""

    # Arrange
    patient_vital_id = 1
    mock_patient_vital.query.filter.return_value.first.return_value = (
        get_mock_patient_vitals()[0]
    )  # Mocking existing vital

    # Act
    result = update_vital(db_session_mock, patient_vital_id, vital_update)

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.PatientId == vital_update.PatientId
    assert result.SystolicBP == vital_update.SystolicBP
    assert result.DiastolicBP == vital_update.DiastolicBP
    assert result.Temperature == vital_update.Temperature
    assert result.VitalRemarks == vital_update.VitalRemarks
    assert result.HeartRate == vital_update.HeartRate
    assert result.SpO2 == vital_update.SpO2
    assert result.BloodSugarLevel == vital_update.BloodSugarLevel
    assert result.Height == vital_update.Height
    assert result.Weight == vital_update.Weight


@mock.patch("app.models.patient_vital_model.PatientVital")
def test_delete_patient_vital(mock_patient_vital, db_session_mock):
    """Test case for deleting a patient vital."""

    # Arrange
    patient_vital_id = 1
    mock_patient_vital.query.filter.return_value.first.return_value = (
        get_mock_patient_vitals()[0]
    )  # Mocking existing vital

    # Act
    result = delete_vital(db_session_mock, patient_vital_id)

    # Assert
    db_session_mock.commit.assert_called_once()
    assert result.IsDeleted == "1"


# Mocking the relevant models
# TODO: this test fails
# @mock.patch("app.models.patient_model.Patient")
# @mock.patch("app.models.patient_patient_guardian_model.PatientPatientGuardian")
# @mock.patch("app.models.patient_allergy_mapping_model.PatientAllergyMapping")
# @mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
# @mock.patch("app.models.allergy_reaction_type_model.AllergyReactionType")  # Mock AllergyReactionType
# @mock.patch("app.models.patient_doctor_note_model.PatientDoctorNote")  # Mock PatientDoctorNote
# @mock.patch("app.models.patient_photo_model.PatientPhoto")  # Mock PatientPhoto
# @mock.patch("app.models.patient_assigned_dementia_model.PatientAssignedDementia")  # Mock PatientAssignedDementia
# @mock.patch("app.models.patient_mobility_model.PatientMobility")  # Mock PatientMobility
# @mock.patch("app.models.patient_prescription_list_model.PatientPrescriptionList")
# @mock.patch("app.models.patient_prescription_model.PatientPrescription")  # Mock PatientPrescription
# @mock.patch("app.models.patient_vital_model.PatientVital")
# @mock.patch("app.models.patient_highlight_model.PatientHighlight")
# @mock.patch("app.models.allergy_type_model.AllergyType")
# @mock.patch("app.models.patient_guardian_relationship_mapping_model.PatientGuardianRelationshipMapping")
# def test_get_vital_list(
#     mock_patient,
#     mock_patient_guardian,
#     mock_patient_allergy_mapping,
#     mock_patient_doctor_note,
#     mock_patient_photo,
#     mock_patient_assigned_dementia,
#     mock_patient_mobility,
#     mock_patient_prescription_list,
#     mock_patient_prescription,
#     mock_patient_vital,
#     mock_patient_highlight,
#     mock_allergy_type,
#     mock_patient_guardian_relationship_mapping,  # Ensure this mock is passed in
#     get_vital_list,
#     db_session_mock):
#     # Mock the Patient object
#     # patient_mock = get_mock_patient()
#     # db_session_mock.query.return_value.filter.return_value.first.return_value = patient_mock

#     # Arrange
#     patient_id = 1
#     skip = 0
#     limit = 2
#     # query_mock = db_session_mock.query.return_value
#     # filter_mock = query_mock.filter.return_value
#     # order_by_mock = filter_mock.order_by.return_value
#     # offset_mock = order_by_mock.offset.return_value
#     # limit_mock = offset_mock.limit.return_value
#     # limit_mock.all.return_value = get_mock_patient_vitals()
#     mock_patient_vital = get_mock_patient_vitals()

#     with mock.patch.object(db_session_mock.query(PatientVital).filter().order_by().offset().limit(), 'all', return_value=get_mock_patient_vitals()):
#         result = get_vital_list(db_session_mock, patient_id, skip, limit)
#     # Act
#     result = get_vital_list(db_session_mock, patient_id, skip, limit)

#     # Assert
#     assert len(result) == 2
#     assert result[0].patientId == patient_id
#     assert result[0].systolicBP == 120
#     assert result[0].diastolicBP == 80
#     assert result[1].patientId == patient_id
#     assert result[1].systolicBP == 130
#     assert result[1].diastolicBP == 85


## MOCK DATA ##
def get_mock_patient_vitals():
    """Return a list of mock PatientVital objects."""
    return [
        PatientVital(
            Id=1,
            PatientId=1,
            IsAfterMeal="0",
            Temperature=36.6,
            SystolicBP=120,
            DiastolicBP=80,
            HeartRate=70,
            SpO2=98,
            BloodSugarLevel=90,
            Height=170.0,
            Weight=70.0,
            VitalRemarks="Normal",
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=1,
            UpdatedById=1,
        ),
        PatientVital(
            Id=2,
            PatientId=1,
            IsAfterMeal="1",
            Temperature=37.0,
            SystolicBP=130,
            DiastolicBP=85,
            HeartRate=75,
            SpO2=97,
            BloodSugarLevel=110,
            Height=170.0,
            Weight=70.0,
            VitalRemarks="Slightly high BP",
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=1,
            UpdatedById=1,
        ),
    ]


@pytest.fixture
def vital_create():
    return PatientVitalCreate(
        PatientId=1,
        IsAfterMeal="0",
        Temperature=36.6,
        SystolicBP=120,
        DiastolicBP=80,
        HeartRate=70,
        SpO2=98,
        BloodSugarLevel=9,
        Height=170.0,
        Weight=70.0,
        VitalRemarks="Normal",
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=1,
        UpdatedById=1,
    )


@pytest.fixture
def vital_update():
    return PatientVitalUpdate(
        PatientId=1,
        IsAfterMeal="1",
        Temperature=37.0,
        SystolicBP=130,
        DiastolicBP=85,
        HeartRate=75,
        SpO2=97,
        BloodSugarLevel=9,
        Height=170.0,
        Weight=70.0,
        VitalRemarks="Slightly high BP",
        UpdatedById=1,
        UpdatedDateTime=datetime.now(),
    )


@pytest.fixture
def vital_delete():
    return PatientVitalDelete(IsDeleted="0")
