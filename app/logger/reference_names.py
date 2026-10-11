"""Add human-readable names next to lookup-list and guardian IDs in audit data.

Name key convention: ``*_id`` -> ``*_name``; ``*Id`` / ``*ID`` -> ``*Name``.
Any failure leaves the data unchanged: logging must never break a request.
"""
import logging
import time
from typing import Dict, Optional

from sqlalchemy import text

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

# table key -> database table name (to skip a lookup table's own rows)
TABLE_NAMES = {
    "language": "PATIENT_LIST_LANGUAGE",
    "religion": "PATIENT_LIST_RELIGION",
    "diet": "PATIENT_LIST_DIET",
    "education": "PATIENT_LIST_EDUCATION",
    "livewith": "PATIENT_LIST_LIVEWITH",
    "occupation": "PATIENT_LIST_OCCUPATION",
    "pet": "PATIENT_LIST_PET",
    "prescription": "PATIENT_PRESCRIPTION_LIST",
    "mobility": "PATIENT_MOBILITY_LIST",
    "album": "PATIENT_PHOTO_LIST_ALBUM",
    "preference": "PATIENT_PERSONAL_PREFERENCE_LIST",
    "problem": "PATIENT_PROBLEM_LIST",
    "diagnosis": "PATIENT_MEDICAL_DIAGNOSIS_LIST",
    "highlight_type": "PATIENT_HIGHLIGHT_TYPE",
    "relationship": "PATIENT_GUARDIAN_RELATIONSHIP_MAPPING",
    "guardian": "PATIENT_GUARDIAN",
}

_MISS_TTL_SECONDS = 60
_LOCK_TIMEOUT_MS = 500

# (table key, id) -> (monotonic timestamp, name or None)
_cache: Dict[tuple, tuple] = {}


def _name_key(key: str) -> Optional[str]:
    if key.endswith("_id"):
        return key[:-3] + "_name"
    if key.endswith("Id") or key.endswith("ID"):
        return key[:-2] + "Name"
    return None


def _load_table(table: str, ids) -> dict:
    """Read {id: name} for the given ids of one lookup table.

    Uses a short-lived session that fails fast on locks held by the request.
    """
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
        db.execute(text(f"SET LOCK_TIMEOUT {_LOCK_TIMEOUT_MS}"))
        ids = list(ids)
        if table == "guardian":
            rows = (
                db.query(
                    PatientGuardian.id,
                    PatientGuardian.firstName,
                    PatientGuardian.lastName,
                )
                .filter(PatientGuardian.id.in_(ids))
                .all()
            )
            return {r[0]: " ".join(p for p in (r[1], r[2]) if p).strip() for r in rows}
        model, id_attr, name_attr = simple[table]
        id_col = getattr(model, id_attr)
        rows = (
            db.query(id_col, getattr(model, name_attr)).filter(id_col.in_(ids)).all()
        )
        return {r[0]: r[1] for r in rows}
    finally:
        # The setting outlives the session on a pooled connection; restore the default.
        try:
            db.execute(text("SET LOCK_TIMEOUT -1"))
        except Exception:
            pass
        db.close()


def _coerce_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_names(table: str, ids: set) -> dict:
    """Return {id: name} for the ids that have a name, loading only cache misses."""
    now = time.monotonic()
    found, missing = {}, []
    for i in ids:
        hit = _cache.get((table, i))
        if hit and now < hit[0]:
            if hit[1]:
                found[i] = hit[1]
        else:
            missing.append(i)
    if missing:
        loaded = _load_table(table, missing)
        now = time.monotonic()
        for i in missing:
            name = loaded.get(i)
            ttl = _TTL_SECONDS if name else _MISS_TTL_SECONDS
            _cache[(table, i)] = (now + ttl, name)
            if name:
                found[i] = name
    return found


def add_reference_names(data: Optional[dict], table: Optional[str] = None) -> Optional[dict]:
    """Return a copy of data with name siblings added; data itself on any error.

    ``table`` is the logged table; a lookup table's own ID column is skipped.
    """
    try:
        if not data:
            return data
        own = (table or "").upper()
        wanted = []
        for k, v in data.items():
            if not (isinstance(k, str) and k.lower() in ID_KEY_TABLES):
                continue
            tkey = ID_KEY_TABLES[k.lower()]
            name_key = _name_key(k)
            if TABLE_NAMES.get(tkey) == own or not name_key or name_key in data:
                continue
            ident = _coerce_id(v)
            if ident is None:
                continue
            wanted.append((name_key, tkey, ident))
        if not wanted:
            return data
        by_table: Dict[str, set] = {}
        for _, tkey, ident in wanted:
            by_table.setdefault(tkey, set()).add(ident)
        names = {t: _get_names(t, ids) for t, ids in by_table.items()}
        out = dict(data)
        for name_key, tkey, ident in wanted:
            name = names[tkey].get(ident)
            if name:
                out[name_key] = name
        return out
    except Exception as exc:  # never break logging
        _log.warning("add_reference_names failed: %s", exc)
        return data
