import pytest
from unittest import mock
from app.crud.patient_guardian_crud import (
    get_guardian,
    create_guardian,
    update_guardian,
)
from app.crud.patient_patient_guardian_crud import create_patient_patient_guardian
from app.schemas.patient_guardian import PatientGuardianCreate, PatientGuardianUpdate
from app.schemas.patient_patient_guardian import PatientPatientGuardianCreate
from app.models.patient_guardian_model import PatientGuardian
from app.models.patient_patient_guardian_model import PatientPatientGuardian
from app.models.patient_guardian_relationship_mapping_model import (
    PatientGuardianRelationshipMapping,
)
from app.models.patient_model import Patient
from datetime import datetime
from tests.utils.mock_db import get_db_session_mock
from unittest.mock import call


# @mock.patch("app.models.patient_guardian_model.PatientGuardian")
# def test_create_patient_guardian(
#  # Ensure this mock is passed in
#     mock_patient_guardian,
#     db_session_mock,
# ):
#     """Test case for creating a social history."""

#     # Arrange
#     patient_guardian = patient_guardian_create()

#     # Act
#     created_guardian = create_guardian(db_session_mock, patient_guardian)

#     #Assert
#     db_session_mock.commit.assert_called_once()
#     db_session_mock.refresh.assert_called_once_with(created_guardian)


@mock.patch("app.models.patient_guardian_model.PatientGuardian")
def test_update_patient_guardian(
    # Ensure this mock is passed in
    mock_patient_guardian,
    db_session_mock,
):

    # Arrange
    patient_guardian = patient_guardian_update()

    # Act
    updated_guardian = update_guardian(db_session_mock, 1, patient_guardian)

    # Assert
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once_with(updated_guardian)


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def get_mock_patient_guardian():
    """Return a mock PatientSocialHistory object."""
    return PatientGuardian(
        active="Y",
        firstName="Test",
        lastName="TestLastName",
        preferredName="Test",
        gender="M",
        contactNo="91234567",
        nric="S1234567Z",
        email="test@test.com",
        dateOfBirth=datetime.strptime("2024-10-23 15:45:30", "%Y-%m-%d %H:%M:%S"),
        address="123",
        tempAddress="123",
        status="Y",
        isDeleted="0",
        guardianApplicationUserId="B22698B8-42A2-4115-9631-1C2D1E2AC5F5",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
    )


def patient_guardian_update():
    return PatientGuardianUpdate(
        active="Y",
        firstName="Test",
        lastName="TestLastName",
        preferredName="Test",
        gender="M",
        contactNo="91234567",
        nric="S1234567Z",
        email="test@test.com",
        dateOfBirth="2024-10-23 15:45:30",
        address="123",
        tempAddress="123",
        status="Y",
        isDeleted="0",
        guardianApplicationUserId="B22698B8-42A2-4115-9631-1C2D1E2AC5F5",
        modifiedDate=datetime.now(),
        ModifiedById="1",
        patientId="1",
        relationshipName="Husband",
    )


def patient_guardian_create():
    return PatientGuardianCreate(
        active="Y",
        firstName="Test",
        lastName="TestLastName",
        preferredName="Test",
        gender="M",
        contactNo="91234567",
        nric="S1234567Z",
        email="test@test.com",
        dateOfBirth="2024-10-23 15:45:30",
        address="123",
        tempAddress="123",
        status="Y",
        isDeleted="0",
        guardianApplicationUserId="B22698B8-42A2-4115-9631-1C2D1E2AC5F5",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
        patientId="1",
        relationshipName="Husband",
    )


def get_mock_patient():
    return Patient(
        id="1",
        firstName="John",
        lastName="Doe",
        nric="S1234567D",
        address="123 Main St",
        tempAddress="456 Secondary St",
        homeNo="12345678",
        handphoneNo="87654321",
        gender="M",
        dateOfBirth="1990-01-01 00:00:00.000",
        isApproved="1",
        preferredName="Johnny",
        preferredLanguageId=1,
        updateBit="1",
        autoGame="1",
        startDate="2021-01-01 00:00:00.000",
        endDate=None,
        isActive="1",
        isRespiteCare="1",
        privacyLevel=2,
        terminationReason=None,
        inActiveReason=None,
        inActiveDate=None,
        profilePicture=None,
        createdDate="2021-01-01 00:00:00.000",
        modifiedDate="2021-01-01 00:00:00.000",
        CreatedById="1",
        ModifiedById="1",
        isDeleted="0",
    )


def get_patient_patient_guardian():
    return PatientPatientGuardian(
        id="1",
        patientId="1",
        guardianId="1",
        relationshipId="1",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
        isDeleted="0",
    )


def patient_patient_guardian_create():
    return PatientPatientGuardianCreate(
        patientId="1",
        guardianId="1",
        relationshipId="1",
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
        isDeleted="0",
    )


def get_patient_guardian_relationship_mapping():
    return PatientGuardianRelationshipMapping(
        id="1",
        isDeleted="0",
        relationshipName="Husband",
        createdDate="2021-01-01 00:00:00.000",
        modifiedDate="2021-01-01 00:00:00.000",
        CreatedById="1",
        ModifiedById="1",
    )
