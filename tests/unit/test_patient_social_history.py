# import pytest
# from unittest import mock
# from datetime import datetime
# from app.crud.patient_social_history_crud import (
#     get_social_history,
#     create_social_history,
#     update_social_history,
#     delete_social_history
# )
# from app.schemas.patient_social_history import (
#     PatientSocialHistoryCreate,
#     PatientSocialHistoryUpdate
# )
# from app.models.patient_social_history_model import PatientSocialHistory
# from app.models.patient_list_diet_model import PatientDietList
# from app.models.patient_list_education_model import PatientEducationList
# from app.models.patient_list_livewith_model import PatientLiveWithList
# from app.models.patient_list_occupation_model import PatientOccupationList
# from app.models.patient_list_pet_model import PatientPetList
# from app.models.patient_list_religion_model import PatientReligionList
# from tests.utils.mock_db import get_db_session_mock

# # TEST CASES
# @mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
# def test_create_social_history(mock_patient_social_history, db_session_mock, social_history_create):
#     """Test case for creating a social history record."""
    
#     # Arrange
#     mock_patient_social_history.query.filter.return_value.first.return_value = None  # No existing record

#     # Act
#     result = create_social_history(db_session_mock, social_history_create)

#     # Assert
#     db_session_mock.add.assert_called_once_with(result)
#     db_session_mock.commit.assert_called_once()
#     db_session_mock.refresh.assert_called_once_with(result)

#     assert result.patientId == 2
#     assert result.isDeleted == "0"


# def test_get_social_history(db_session_mock):
#     """Test case for retrieving social history by patient ID."""

#     # Arrange
#     db_session_mock.query.return_value.filter.return_value.first.return_value = get_mock_social_history()

#     # Act
#     result = get_social_history(db_session_mock, 1)

#     # Assert
#     assert result is not None
#     assert result.patientId == 1
#     assert result.isDeleted == "0"
#     assert result.alcoholUse == "0"
#     assert result.dietListId == 1
#     assert result.educationListId == 2


# def test_update_social_history(db_session_mock, social_history_update):
#     """Test case for updating a patient's social history."""

#     # Arrange
#     db_session_mock.query.return_value.filter.return_value.first.return_value = get_mock_social_history()

#     # Act
#     result = update_social_history(db_session_mock, 1, social_history_update)

#     # Assert
#     db_session_mock.commit.assert_called_once()
#     db_session_mock.refresh.assert_called_once_with(result)

#     assert result.modifiedById == 3
#     assert result.dietListId == 2
#     assert result.educationListId == 2
#     assert result.liveWithListId == 2
#     assert result.occupationListId == 2

# @mock.patch("app.models.patient_social_history_model.PatientSocialHistory")
# def test_delete_social_history(mock_patient_social_history, db_session_mock):
#     """Test case for soft-deleting a social history record."""

#     # Arrange
#     mock_social_history = get_mock_social_history()
#     db_session_mock.query.return_value.filter.return_value.first.return_value = mock_social_history

#     # Act
#     result = delete_social_history(db_session_mock, 1)

#     # Assert
#     db_session_mock.commit.assert_called_once()
#     assert result.isDeleted == "1"


# ## MOCK DATA ##
# def get_mock_social_history():
#     """Return a mock PatientSocialHistory object."""
#     return PatientSocialHistory(
#         patientId=1,
#         isDeleted="0",
#         sexuallyActive="0",
#         secondHandSmoker="1",
#         alcoholUse="0",
#         caffeineUse="0",
#         tobaccoUse="0",
#         drugUse="0",
#         exercise="1",
#         dietListId=1,
#         educationListId=2,
#         liveWithListId=3,
#         occupationListId=4,
#         petListId=5,
#         religionListId=6,
#         modifiedById=2,
#         modifiedDate=datetime.now()
#     )


# # FIXTURES
# @pytest.fixture
# def db_session_mock():
#     """Fixture to mock the database session."""
#     return get_db_session_mock()

# @pytest.fixture
# def social_history_create():
#     """Fixture to provide a mock PatientSocialHistoryCreate object."""
#     return PatientSocialHistoryCreate(
#         patientId=2,
#         sexuallyActive="0",
#         secondHandSmoker="1",
#         alcoholUse="0",
#         caffeineUse="0",
#         tobaccoUse="0",
#         drugUse="0",
#         exercise="1",
#         dietListId=1,
#         educationListId=1,
#         liveWithListId=1,
#         occupationListId=1,
#         petListId=1,
#         religionListId=1,
#         createdById=2,
#         createdDate=datetime.now(),
#         modifiedById=2,
#         modifiedDate=datetime.now()
#     )


# @pytest.fixture
# def social_history_update():
#     """Fixture to provide a mock PatientSocialHistoryUpdate object."""
#     return PatientSocialHistoryUpdate(
#         patientId=1,
#         sexuallyActive="1",
#         secondHandSmoker="1",
#         alcoholUse="1",
#         caffeineUse="1",
#         tobaccoUse="1",
#         drugUse="1",
#         exercise="1",
#         dietListId=2,
#         educationListId=2,
#         liveWithListId=2,
#         occupationListId=2,
#         petListId=2,
#         religionListId=2,
#         modifiedById=3,
#         modifiedDate=datetime.now()
#     )
