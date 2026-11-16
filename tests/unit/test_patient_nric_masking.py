"""Regression tests: masking the NRIC for a response must never change the stored NRIC.

Before the fix, get_patient() masked the NRIC on the session-attached ORM row. Routes that
call get_patient() and then commit in the same session (DoctorNote add/update, MedicalHistory
add) saved the masked value, e.g. S1234567D became *****567D.
"""
from datetime import datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.crud.patient_crud import get_patient, get_patients
from app.models.patient_list_language_model import PatientListLanguage
from app.models.patient_model import Patient as PatientModel
from app.schemas.patient import PatientUpdate, mask_nric_value, to_patient_response

REAL_NRIC = "S1234567D"


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    PatientListLanguage.__table__.create(engine)
    PatientModel.__table__.create(engine)
    db = sessionmaker(bind=engine)()
    now = datetime(2026, 1, 1)
    db.add(PatientListLanguage(id=1, value="English", isDeleted="0", createdDate=now, modifiedDate=now))
    db.add(PatientModel(
        id=1, name="ALICE LEE", nric=REAL_NRIC, gender="F", dateOfBirth=datetime(1950, 1, 1),
        isApproved="1", preferredLanguageId=1, updateBit="1", autoGame="0", startDate=now,
        isActive="1", isRespiteCare="0", privacyLevel=0, isDeleted=0,
        createdDate=now, modifiedDate=now, CreatedById="1", ModifiedById="1",
    ))
    db.commit()
    yield db
    db.close()


def _stored_nric(db):
    return db.execute(text('SELECT nric FROM "PATIENT" WHERE id = 1')).scalar()


def test_get_patient_then_commit_keeps_real_nric(session):
    """Same flow as POST /DoctorNote/add: existence check, then a commit in the same session."""
    db_patient = get_patient(session, 1)
    assert db_patient.nric == REAL_NRIC

    response = to_patient_response(db_patient, mask=True)
    assert response.nric == "*****567D"

    session.commit()
    session.expire_all()
    assert _stored_nric(session) == REAL_NRIC
    assert get_patient(session, 1).nric == REAL_NRIC


def test_patient_list_then_commit_keeps_real_nric(session):
    patients, _, _ = get_patients(session)
    masked = [to_patient_response(p, mask=True) for p in patients]
    assert masked[0].nric == "*****567D"

    session.commit()
    assert _stored_nric(session) == REAL_NRIC


def test_unmasked_response_returns_real_nric(session):
    assert to_patient_response(get_patient(session, 1), mask=False).nric == REAL_NRIC


def test_orm_refuses_masked_nric(session):
    db_patient = get_patient(session, 1)
    with pytest.raises(ValueError):
        db_patient.nric = "*****567D"


def test_update_schema_rejects_masked_nric():
    base = dict(
        name="ALICE LEE", gender="F", dateOfBirth=datetime(1950, 1, 1), isApproved="1",
        updateBit="1", autoGame="0", startDate=datetime(2026, 1, 1), isActive="1",
        isRespiteCare="0", privacyLevel=0, modifiedDate=datetime(2026, 1, 1), ModifiedById="1",
    )
    with pytest.raises(ValidationError):
        PatientUpdate(nric="*****567D", **base)
    assert PatientUpdate(nric=REAL_NRIC, **base).nric == REAL_NRIC


def test_mask_nric_value():
    assert mask_nric_value(REAL_NRIC) == "*****567D"
    assert mask_nric_value(None) is None
