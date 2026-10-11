"""Audit entries for allergy and dementia mappings carry readable names."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.crud import (
    patient_allergy_mapping_crud as allergy_crud,
    patient_assigned_dementia_mapping_crud as dementia_crud,
)
from app.schemas.patient_allergy_mapping import (
    PatientAllergyCreate,
    PatientAllergyUpdateReq,
)
from app.schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementiaCreate,
    PatientAssignedDementiaUpdate,
)


def make_db(results):
    """results: {model: [first() return values in call order]}; default None."""
    queues = {m: list(v) for m, v in results.items()}

    def query(*args, **kwargs):
        model = args[0] if args else None
        q = MagicMock()
        chain = q.filter.return_value
        chain.first.side_effect = lambda: (
            queues[model].pop(0) if queues.get(model) else None
        )
        return q

    db = MagicMock()
    db.query.side_effect = query
    return db


def test_allergy_create_logs_names():
    db = make_db(
        {
            allergy_crud.AllergyType: [SimpleNamespace(Value="Peanut", IsDeleted="0")],
            allergy_crud.AllergyReactionType: [SimpleNamespace(Value="Rash")],
            allergy_crud.Patient: [SimpleNamespace(name="Tan")],
        }
    )
    data = PatientAllergyCreate(PatientID=1, AllergyTypeID=3, AllergyReactionTypeID=2)
    with patch.object(allergy_crud, "log_crud_action") as log, patch.object(
        allergy_crud, "create_highlight_if_needed"
    ):
        allergy_crud.create_patient_allergy(db, data, "1", "Admin")
    updated = log.call_args.kwargs["updated_data"]
    assert updated["AllergyTypeName"] == "Peanut"
    assert updated["AllergyReactionTypeName"] == "Rash"


def test_allergy_update_logs_new_names():
    db_allergy = SimpleNamespace(
        Patient_AllergyID=5, PatientID=1, AllergyTypeID=3, AllergyReactionTypeID=2,
        AllergyRemarks=None, IsDeleted="0",
    )
    db = make_db(
        {
            allergy_crud.AllergyType: [SimpleNamespace(Value="Shellfish", IsDeleted="0")],
            allergy_crud.AllergyReactionType: [SimpleNamespace(Value="Hives")],
            allergy_crud.PatientAllergyMapping: [db_allergy, None],
            allergy_crud.Patient: [SimpleNamespace(name="Tan")],
        }
    )
    data = PatientAllergyUpdateReq(PatientID=1, AllergyTypeID=4, AllergyReactionTypeID=6)
    with patch.object(allergy_crud, "log_crud_action") as log, patch.object(
        allergy_crud, "create_highlight_if_needed"
    ):
        allergy_crud.update_patient_allergy(db, 5, data, "1", "Admin")
    updated = log.call_args.kwargs["updated_data"]
    assert updated["AllergyTypeName"] == "Shellfish"
    assert updated["AllergyReactionTypeName"] == "Hives"


def test_allergy_delete_logs_names_in_original_data():
    db_allergy = SimpleNamespace(
        Patient_AllergyID=5, PatientID=1, AllergyTypeID=3, AllergyReactionTypeID=2,
        AllergyRemarks=None, IsDeleted="0",
    )
    db = make_db(
        {
            allergy_crud.PatientAllergyMapping: [db_allergy],
            allergy_crud.Patient: [SimpleNamespace(name="Tan")],
            allergy_crud.AllergyType: [SimpleNamespace(Value="Peanut")],
            allergy_crud.AllergyReactionType: [SimpleNamespace(Value="Rash")],
        }
    )
    with patch.object(allergy_crud, "log_crud_action") as log:
        allergy_crud.delete_patient_allergy(db, 5, "1", "Admin")
    original = log.call_args.kwargs["original_data"]
    assert original["AllergyTypeName"] == "Peanut"
    assert original["AllergyReactionTypeName"] == "Rash"


def test_dementia_create_logs_names():
    db = make_db(
        {
            dementia_crud.PatientAssignedDementiaList: [
                SimpleNamespace(Value="Alzheimer's")
            ],
            dementia_crud.PatientDementiaStageList: [
                SimpleNamespace(DementiaStage="Mild")
            ],
            dementia_crud.Patient: [SimpleNamespace(name="Tan")],
        }
    )
    data = PatientAssignedDementiaCreate(
        PatientId=1, DementiaTypeListId=1, DementiaStageId=1,
        CreatedById="1", ModifiedById="1",
    )
    with patch.object(dementia_crud, "log_crud_action") as log:
        dementia_crud.create_assigned_dementia(db, data, "1", "Admin")
    updated = log.call_args.kwargs["updated_data"]
    assert updated["DementiaTypeName"] == "Alzheimer's"
    assert updated["DementiaStageName"] == "Mild"


def test_dementia_update_logs_old_and_new_names():
    db_assignment = SimpleNamespace(
        id=7, PatientId=1, DementiaTypeListId=1, DementiaStageId=1, IsDeleted="0"
    )
    db = make_db(
        {
            dementia_crud.PatientAssignedDementiaMapping: [db_assignment],
            # validate, old, new
            dementia_crud.PatientAssignedDementiaList: [
                SimpleNamespace(Value="Vascular", DementiaTypeListId=2),
                SimpleNamespace(Value="Alzheimer's", DementiaTypeListId=1),
                SimpleNamespace(Value="Vascular", DementiaTypeListId=2),
            ],
            dementia_crud.PatientDementiaStageList: [
                SimpleNamespace(DementiaStage="Severe", id=3),
                SimpleNamespace(DementiaStage="Mild", id=1),
                SimpleNamespace(DementiaStage="Severe", id=3),
            ],
            dementia_crud.Patient: [SimpleNamespace(name="Tan")],
        }
    )
    data = PatientAssignedDementiaUpdate(
        DementiaTypeListId=2, DementiaStageId=3, ModifiedById="1"
    )
    with patch.object(dementia_crud, "log_crud_action") as log:
        dementia_crud.update_assigned_dementia(db, 7, data, "1", "Admin")
    kw = log.call_args.kwargs
    assert kw["original_data"]["DementiaTypeName"] == "Alzheimer's"
    assert kw["original_data"]["DementiaStageName"] == "Mild"
    assert kw["updated_data"]["DementiaTypeName"] == "Vascular"
    assert kw["updated_data"]["DementiaStageName"] == "Severe"


def test_dementia_delete_logs_names_in_original_data():
    db_assignment = SimpleNamespace(
        id=7, PatientId=1, DementiaTypeListId=1, DementiaStageId=1, IsDeleted="0"
    )
    db = make_db(
        {
            dementia_crud.PatientAssignedDementiaMapping: [db_assignment],
            dementia_crud.Patient: [SimpleNamespace(name="Tan")],
            dementia_crud.PatientAssignedDementiaList: [
                SimpleNamespace(Value="Alzheimer's")
            ],
            dementia_crud.PatientDementiaStageList: [
                SimpleNamespace(DementiaStage="Mild")
            ],
        }
    )
    with patch.object(dementia_crud, "log_crud_action") as log:
        dementia_crud.delete_assigned_dementia(db, 7, "1", "Admin")
    original = log.call_args.kwargs["original_data"]
    assert original["DementiaTypeName"] == "Alzheimer's"
    assert original["DementiaStageName"] == "Mild"
