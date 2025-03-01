import pytest
from datetime import datetime
from fastapi import HTTPException
from app.crud.patient_social_history_crud import (
    get_patient_social_history,
    create_patient_social_history,
    update_patient_social_history,
    delete_patient_social_history,
)
from app.schemas.patient_social_history import (
    PatientSocialHistoryCreate,
    PatientSocialHistoryUpdate,
)
from app.models.patient_model import Patient
from app.models.patient_allergy_mapping_model import PatientAllergyMapping
from app.models.allergy_type_model import AllergyType
from app.models.allergy_reaction_type_model import AllergyReactionType
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_doctor_note_model import PatientDoctorNote
from app.models.patient_photo_model import PatientPhoto
from app.models.patient_photo_list_model import PatientPhotoList
from app.models.patient_model import Patient
from app.models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from app.models.patient_assigned_dementia_mapping_model import PatientAssignedDementiaMapping
from app.models.patient_mobility_list_model import PatientMobilityList
from app.models.patient_mobility_mapping_model import PatientMobility
from app.models.patient_prescription_model import PatientPrescription
from app.models.patient_social_history_model import PatientSocialHistory
from app.models.patient_vital_model import PatientVital
from app.models.patient_highlight_model import PatientHighlight
from app.models.patient_social_history_model import PatientSocialHistory
from app.models.patient_list_diet_model import PatientDietList
from app.models.patient_list_education_model import PatientEducationList
from app.models.patient_list_livewith_model import PatientLiveWithList
from app.models.patient_list_occupation_model import PatientOccupationList
from app.models.patient_list_pet_model import PatientPetList
from app.models.patient_list_religion_model import PatientReligionList
from app.models.patient_guardian_relationship_mapping_model import PatientGuardianRelationshipMapping


from tests.utils.mock_db import get_db_session_mock

def test_get_patient_social_history(db_session_mock, mock_patient_social_history, mock_list_entries):
    """Test case for retrieving social history using fixtures."""
    # Arrange
    patient_id = 1
    mock_record = mock_patient_social_history
    
    # Attach the list values (simulating the JOINs)
    mock_record.DietValue = mock_list_entries["diet"].Value
    mock_record.DietIsDeleted = mock_list_entries["diet"].IsDeleted
    mock_record.EducationValue = mock_list_entries["education"].Value
    mock_record.EducationIsDeleted = mock_list_entries["education"].IsDeleted
    mock_record.LiveWithValue = mock_list_entries["live_with"].Value
    mock_record.LiveWithIsDeleted = mock_list_entries["live_with"].IsDeleted
    mock_record.OccupationValue = mock_list_entries["occupation"].Value
    mock_record.OccupationIsDeleted = mock_list_entries["occupation"].IsDeleted
    mock_record.PetValue = mock_list_entries["pet"].Value
    mock_record.PetIsDeleted = mock_list_entries["pet"].IsDeleted
    mock_record.ReligionValue = mock_list_entries["religion"].Value
    mock_record.ReligionIsDeleted = mock_list_entries["religion"].IsDeleted

    # Mock the query chain result
    db_session_mock.query.return_value.join.return_value.join.return_value.join.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.first.return_value = mock_record

    # Act
    result = get_patient_social_history(db_session_mock, patient_id)

    # Assert
    assert result["id"] == 1
    assert result["patientId"] == patient_id
    assert result["dietValue"] == "Diabetic"
    assert result["educationValue"] == "Primary"
    assert result["liveWithValue"] == "Alone"
    assert result["occupationValue"] == "Accountant"
    assert result["petValue"] == "Bird"
    assert result["religionValue"] == "Atheist"
    assert result["createdById"] == 1
    assert result["modifiedById"] == 1

    # Ensure the query was executed properly
    db_session_mock.query.assert_called_once()

def test_create_patient_social_history(db_session_mock, patient_social_history_create):
    """Test case for creating a new patient social history."""
    # Arrange
    created_by = 1
    
    mock_diet = PatientDietList(Id=1, Value="Diabetic", IsDeleted="0")
    mock_education = PatientEducationList(Id=1, Value="Primary or lower", IsDeleted="0")
    mock_livewith = PatientLiveWithList(Id=1, Value="Alone", IsDeleted="0")
    mock_occupation = PatientOccupationList(Id=1, Value="Accountant", IsDeleted="0")
    mock_pet = PatientPetList(Id=1, Value="Bird", IsDeleted="0")
    mock_religion = PatientReligionList(Id=1, Value="Atheist", IsDeleted="0")

    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_diet,
        mock_education,
        mock_livewith,
        mock_occupation,
        mock_pet,
        mock_religion,
        None
    ]

    # Act
    result = create_patient_social_history(db_session_mock, patient_social_history_create, created_by, "USER")

    # Assert
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()
    assert result.createdById == created_by
    assert result.dietListId == 1
    assert result.educationListId == 1


def test_create_patient_social_history_invalid_list_type(db_session_mock, patient_social_history_create):
    """Test case for creating a new patient social history with invalid list type."""
    # Arrange
    created_by = 1
    
    # Simulate valid records for other list types other than diet
    mock_education = PatientEducationList(Id=1, Value="Primary or lower", IsDeleted="0")
    mock_livewith = PatientLiveWithList(Id=1, Value="Alone", IsDeleted="0")
    mock_occupation = PatientOccupationList(Id=1, Value="Accountant", IsDeleted="0")
    mock_pet = PatientPetList(Id=1, Value="Bird", IsDeleted="0")
    mock_religion = PatientReligionList(Id=1, Value="Atheist", IsDeleted="0")

    # Set the side_effect: diet query returns None to simulate an invalid/inactive diet record.
    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        None,               # Diet query returns None
        mock_education,     
        mock_livewith,      
        mock_occupation,    
        mock_pet,           
        mock_religion,      
        None                # Existing record check (if needed)
    ]

    # Act
    with pytest.raises(HTTPException) as exc_info:
        create_patient_social_history(db_session_mock, patient_social_history_create, created_by, "USER")

    # Assert
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid or inactive Diet type"


def test_update_patient_social_history(db_session_mock, patient_social_history_update):
    """Test case for updating a patient social history."""
    # Arrange
    patient_id = 1
    modified_by = 2
    current_time = datetime.now()
    
    # Initial record
    mock_social_history = PatientSocialHistory(
        id=1,
        patientId=patient_id,
        sexuallyActive=0,
        secondHandSmoker=0,
        alcoholUse=0,
        caffeineUse=1,
        tobaccoUse=0,
        drugUse=0,
        exercise=1,
        dietListId=1,
        educationListId=1,
        liveWithListId=1,
        occupationListId=1,
        petListId=1,
        religionListId=1,
        isDeleted="0",
        createdDate=current_time,
        modifiedDate=current_time,
        createdById=1,
        modifiedById=1
    )

    # Mock reference data for validation
    mock_diet = PatientDietList(Id=2, Value="Hypertension", IsDeleted="0")
    mock_education = PatientEducationList(Id=2, Value="Secondary", IsDeleted="0")
    mock_livewith = PatientLiveWithList(Id=2, Value="Family", IsDeleted="0")
    mock_occupation = PatientOccupationList(Id=2, Value="Arts", IsDeleted="0")
    mock_pet = PatientPetList(Id=2, Value="Dog", IsDeleted="0")
    mock_religion = PatientReligionList(Id=2, Value="Buddhist", IsDeleted="0")

    db_session_mock.query.return_value.filter.return_value.first.side_effect = [
        mock_social_history,  # First call for finding the record
        mock_diet,
        mock_education,
        mock_livewith,
        mock_occupation,
        mock_pet,
        mock_religion
    ]

    # Act
    result = update_patient_social_history(db_session_mock, patient_id, patient_social_history_update, modified_by,"USER")

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_social_history)
    assert result.modifiedById == modified_by
    assert result.dietListId == 2
    assert result.educationListId == 2
    assert result.liveWithListId == 2
    assert result.occupationListId == 2

def test_delete_patient_social_history(db_session_mock):
    """Test case for deleting (soft-deleting) a patient social history."""
    # Arrange
    social_history_id = 1
    modified_by = 2
    current_time = datetime.now()
    mock_social_history = PatientSocialHistory(
        id=social_history_id,
        patientId=1,
        sexuallyActive=0,
        secondHandSmoker=0,
        alcoholUse=0,
        caffeineUse=1,
        tobaccoUse=0,
        drugUse=0,
        exercise=1,
        dietListId=1,
        educationListId=1,
        liveWithListId=1,
        occupationListId=1,
        petListId=1,
        religionListId=1,
        isDeleted="0",
        createdDate=current_time,
        modifiedDate=current_time,
        createdById=1,
        modifiedById=1
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_social_history

    # Act
    result = delete_patient_social_history(db_session_mock, social_history_id, modified_by, "USER")

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(mock_social_history)
    assert result.isDeleted == "1"
    assert result.modifiedById == modified_by

@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()

@pytest.fixture
def mock_patient_social_history():
    """Fixture for a single patient social history entry with related list values."""
    return PatientSocialHistory(
        id=1,
        patientId=1,
        sexuallyActive=1,
        secondHandSmoker=0,
        alcoholUse=1,
        caffeineUse=1,
        tobaccoUse=0,
        drugUse=0,
        exercise=1,
        dietListId=2,
        educationListId=2,
        liveWithListId=2,
        occupationListId=2,
        petListId=2,
        religionListId=2,
        isDeleted="0",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        createdById=1,
        modifiedById=1
    )

@pytest.fixture
def mock_list_entries():
    """Fixture for related patient list records."""
    return {
        "diet": PatientDietList(Id=2, Value="Diabetic", IsDeleted="0"),
        "education": PatientEducationList(Id=2, Value="Primary", IsDeleted="0"),
        "live_with": PatientLiveWithList(Id=2, Value="Alone", IsDeleted="0"),
        "occupation": PatientOccupationList(Id=2, Value="Accountant", IsDeleted="0"),
        "pet": PatientPetList(Id=2, Value="Bird", IsDeleted="0"),
        "religion": PatientReligionList(Id=2, Value="Atheist", IsDeleted="0"),
    }

@pytest.fixture
def patient_social_history_create():
    """Fixture to provide a PatientSocialHistoryCreate object."""
    current_time = datetime.now()
    return PatientSocialHistoryCreate(
        patientId=1,
        sexuallyActive=1,
        secondHandSmoker=0,
        alcoholUse=0,
        caffeineUse=1,
        tobaccoUse=0,
        drugUse=0,
        exercise=1,
        dietListId=1,  # Diabetic
        educationListId=1,  # Primary or lower
        liveWithListId=1,  # Alone
        occupationListId=1,  # Accountant
        petListId=1,  # Bird
        religionListId=1,  # Atheist
        isDeleted="0",
        createdDate=current_time,
        modifiedDate=current_time,
        createdById=1,
        modifiedById=1
    )

@pytest.fixture
def patient_social_history_update():
    """Fixture to provide a PatientSocialHistoryUpdate object."""
    current_time = datetime.now()
    return PatientSocialHistoryUpdate(
        id=1,
        patientId=1,
        sexuallyActive=1,
        secondHandSmoker=0,
        alcoholUse=1,
        caffeineUse=1,
        tobaccoUse=0,
        drugUse=0,
        exercise=1,
        dietListId=2,  # Hypertension
        educationListId=2,  # Secondary
        liveWithListId=2,  # Family
        occupationListId=2,  # Arts
        petListId=2,  # Dog
        religionListId=2,  # Buddhist
        isDeleted="0",
        modifiedDate=current_time,
        modifiedById=2
    )

