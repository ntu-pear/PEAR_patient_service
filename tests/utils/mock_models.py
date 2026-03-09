# tests/utils/mock_models.py
"""Centralized mock model factories for unit tests."""

from datetime import datetime
from app.models.patient_model import Patient

def get_mock_patient(
    patient_id=1,
    name="Test Patient",
    nric="S9876543Z",
    is_deleted="0"
):
    """Return a mock Patient object."""
    return Patient(
        id=patient_id,
        name=name,
        nric=nric,
        address="Test Address",
        tempAddress="Test Temp Address",
        homeNo="61234567",
        handphoneNo="91234567",
        gender="M",
        dateOfBirth=datetime.strptime("1990-01-01", "%Y-%m-%d"),
        isApproved="Y",
        preferredName="Test",
        preferredLanguageId=1,
        updateBit=0,
        autoGame=0,
        startDate=datetime.now(),
        endDate=None,
        isActive="1",
        isRespiteCare="N",
        privacyLevel="Low",
        terminationReason=None,
        inActiveReason=None,
        inActiveDate=None,
        profilePicture=None,
        createdDate=datetime.now(),
        modifiedDate=datetime.now(),
        CreatedById="1",
        ModifiedById="1",
        isDeleted=is_deleted,
    )