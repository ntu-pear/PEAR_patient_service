"""Audit entries carry lookup-list and guardian names next to their IDs."""
from unittest.mock import patch

import pytest

from app.logger import reference_names
from app.logger.reference_names import add_reference_names
from app.logger import logger_utils
from app.logger.logger_utils import ActionType, filter_data, log_crud_action

CASES = [
    ("preferredLanguageId", "preferredLanguageName", "language"),
    ("religionListId", "religionListName", "religion"),
    ("dietListId", "dietListName", "diet"),
    ("educationListId", "educationListName", "education"),
    ("liveWithListId", "liveWithListName", "livewith"),
    ("occupationListId", "occupationListName", "occupation"),
    ("petListId", "petListName", "pet"),
    ("PrescriptionListId", "PrescriptionListName", "prescription"),
    ("MobilityListId", "MobilityListName", "mobility"),
    ("AlbumCategoryListID", "AlbumCategoryListName", "album"),
    ("PersonalPreferenceListID", "PersonalPreferenceListName", "preference"),
    ("ProblemListID", "ProblemListName", "problem"),
    ("MedicalDiagnosisID", "MedicalDiagnosisName", "diagnosis"),
    ("HighlightTypeId", "HighlightTypeName", "highlight_type"),
    ("relationshipId", "relationshipName", "relationship"),
    ("guardianId", "guardianName", "guardian"),
    ("guardian2Id", "guardian2Name", "guardian"),
]


@pytest.fixture(autouse=True)
def clear_cache():
    reference_names._cache.clear()
    yield
    reference_names._cache.clear()


def fake_loader(table):
    return {1: "Alpha-" + table, 2: "Beta"}


@pytest.mark.parametrize("key,name_key,table", CASES)
def test_names_added_to_both_dicts(key, name_key, table):
    with patch.object(reference_names, "_load_table", side_effect=fake_loader):
        o = add_reference_names({key: 1, "other": "x"})
        u = add_reference_names({key: 2})
    assert o[name_key] == "Alpha-" + table
    assert o[key] == 1 and o["other"] == "x"
    assert u[name_key] == "Beta"


def test_unknown_id_adds_nothing():
    with patch.object(reference_names, "_load_table", return_value={1: "A"}):
        out = add_reference_names({"guardianId": 99})
    assert out == {"guardianId": 99}


def test_exception_returns_data_unchanged():
    data = {"guardianId": 1, "x": 2}
    with patch.object(reference_names, "_load_table", side_effect=RuntimeError("db")):
        assert add_reference_names(data) == {"guardianId": 1, "x": 2}


def test_existing_name_key_not_overwritten():
    with patch.object(reference_names, "_load_table", return_value={1: "A"}):
        out = add_reference_names({"guardianId": 1, "guardianName": "Keep"})
    assert out["guardianName"] == "Keep"


def test_no_known_key_never_touches_db():
    with patch.object(reference_names, "_load_table") as m:
        assert add_reference_names({"foo": 1}) == {"foo": 1}
        assert add_reference_names(None) is None
    m.assert_not_called()


def test_lookup_cached():
    with patch.object(reference_names, "_load_table", return_value={1: "A"}) as m:
        add_reference_names({"guardianId": 1})
        add_reference_names({"guardian2Id": 1})
    assert m.call_count == 1


def test_input_not_mutated():
    data = {"guardianId": 1}
    with patch.object(reference_names, "_load_table", return_value={1: "A"}):
        add_reference_names(data)
    assert data == {"guardianId": 1}


def test_created_by_ids_kept():
    out = filter_data(
        {"CreatedById": "u1", "ModifiedById": "u2", "CreatedDate": "d", "IsDeleted": 0}
    )
    assert out == {"CreatedById": "u1", "ModifiedById": "u2"}


def test_log_crud_action_enriches_and_keeps_ids():
    with patch.object(reference_names, "_load_table", return_value={1: "Mum"}), patch.object(
        logger_utils, "logger"
    ) as lg:
        log_crud_action(
            ActionType.UPDATE, "u", "U", "m", "T", 5,
            original_data={"guardianId": 1, "CreatedById": "a"},
            updated_data={"guardianId": 1, "ModifiedById": "b"},
        )
    msg = lg.info.call_args[0][0]
    assert msg["original_data"] == {"guardianId": 1, "guardianName": "Mum", "CreatedById": "a"}
    assert msg["updated_data"]["guardianName"] == "Mum"
    assert msg["updated_data"]["ModifiedById"] == "b"
