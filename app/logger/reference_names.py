"""Add human-readable names next to lookup-list and guardian IDs in audit data.

Name key convention: ``*_id`` -> ``*_name``; ``*Id`` / ``*ID`` -> ``*Name``.
Any failure leaves the data unchanged: logging must never break a request.
"""
import logging
import time
from typing import Dict, Optional

_log = logging.getLogger(__name__)

_TTL_SECONDS = 300

# lowercased ID key -> table key understood by _load_table
ID_KEY_TABLES = {
    "preferredlanguageid": "language",
    "religionlistid": "religion",
    "dietlistid": "diet",
    "educationlistid": "education",
    "livewithlistid": "livewith",
    "occupationlistid": "occupation",
    "petlistid": "pet",
    "prescriptionlistid": "prescription",
    "mobilitylistid": "mobility",
    "albumcategorylistid": "album",
    "personalpreferencelistid": "preference",
    "problemlistid": "problem",
    "medicaldiagnosisid": "diagnosis",
    "highlighttypeid": "highlight_type",
    "relationshipid": "relationship",
    "guardianid": "guardian",
    "guardian2id": "guardian",
}

# table key -> (monotonic timestamp, {id: name})
_cache: Dict[str, tuple] = {}


def _name_key(key: str) -> Optional[str]:
    if key.endswith("_id"):
        return key[:-3] + "_name"
    if key.endswith("Id") or key.endswith("ID"):
        return key[:-2] + "Name"
    return None


def _load_table(table: str) -> dict:
    """Read {id: name} for one lookup table using a short-lived session."""
    from app.database import SessionLocal
    from app.models.patient_list_language_model import PatientListLanguage
    from app.models.patient_list_religion_model import PatientReligionList
    from app.models.patient_list_diet_model import PatientDietList
    from app.models.patient_list_education_model import PatientEducationList
    from app.models.patient_list_livewith_model import PatientLiveWithList
    from app.models.patient_list_occupation_model import PatientOccupationList
    from app.models.patient_list_pet_model import PatientPetList
    from app.models.patient_prescription_list_model import PatientPrescriptionList
    from app.models.patient_mobility_list_model import PatientMobilityList
    from app.models.patient_photo_list_album_model import PatientPhotoListAlbum
    from app.models.patient_personal_preference_list_model import (
        PatientPersonalPreferenceList,
    )
    from app.models.patient_problem_list_model import PatientProblemList
    from app.models.patient_medical_diagnosis_list_model import (
        PatientMedicalDiagnosisList,
    )
    from app.models.patient_highlight_type_model import PatientHighlightType
    from app.models.patient_guardian_relationship_mapping_model import (
        PatientGuardianRelationshipMapping,
    )
    from app.models.patient_guardian_model import PatientGuardian

    simple = {
        "language": (PatientListLanguage, "id", "value"),
        "religion": (PatientReligionList, "Id", "Value"),
        "diet": (PatientDietList, "Id", "Value"),
        "education": (PatientEducationList, "Id", "Value"),
        "livewith": (PatientLiveWithList, "Id", "Value"),
        "occupation": (PatientOccupationList, "Id", "Value"),
        "pet": (PatientPetList, "Id", "Value"),
        "prescription": (PatientPrescriptionList, "Id", "Value"),
        "mobility": (PatientMobilityList, "MobilityListId", "Value"),
        "album": (PatientPhotoListAlbum, "AlbumCategoryListID", "Value"),
        "preference": (PatientPersonalPreferenceList, "Id", "PreferenceName"),
        "problem": (PatientProblemList, "Id", "ProblemName"),
        "diagnosis": (PatientMedicalDiagnosisList, "Id", "DiagnosisName"),
        "highlight_type": (PatientHighlightType, "Id", "TypeName"),
        "relationship": (PatientGuardianRelationshipMapping, "id", "relationshipName"),
    }
    db = SessionLocal()
    try:
        if table == "guardian":
            rows = db.query(
                PatientGuardian.id, PatientGuardian.firstName, PatientGuardian.lastName
            ).all()
            return {r[0]: " ".join(p for p in (r[1], r[2]) if p).strip() for r in rows}
        model, id_attr, name_attr = simple[table]
        rows = db.query(getattr(model, id_attr), getattr(model, name_attr)).all()
        return {r[0]: r[1] for r in rows}
    finally:
        db.close()


def _get_table(table: str) -> dict:
    now = time.monotonic()
    hit = _cache.get(table)
    if hit and now - hit[0] < _TTL_SECONDS:
        return hit[1]
    data = _load_table(table)
    _cache[table] = (now, data)
    return data


def add_reference_names(data: Optional[dict]) -> Optional[dict]:
    """Return a copy of data with name siblings added; data itself on any error."""
    try:
        if not data:
            return data
        wanted = [
            (k, ID_KEY_TABLES[k.lower()])
            for k in data
            if isinstance(k, str) and k.lower() in ID_KEY_TABLES
        ]
        if not wanted:
            return data
        out = dict(data)
        for key, table in wanted:
            name_key = _name_key(key)
            value = data[key]
            if not name_key or name_key in out or value is None:
                continue
            names = _get_table(table)
            name = names.get(value)
            if name is None:
                try:
                    name = names.get(int(value))
                except (TypeError, ValueError):
                    name = None
            if name:
                out[name_key] = name
        return out
    except Exception as exc:  # never break logging
        _log.warning("add_reference_names failed: %s", exc)
        return data
