from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.logger.logger_utils import ActionType
from app.services.highlight_helper import create_highlight_if_needed
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    return get_db_session_mock()


def _enabled_type(type_id=9, type_code="VITAL"):
    return MagicMock(Id=type_id, TypeCode=type_code, IsEnabled=True, IsDeleted=False)


def test_create_branch_logs_create_with_forwarded_user_full_name(db_session_mock):
    highlight_type = _enabled_type()

    type_query = MagicMock()
    type_query.filter.return_value.first.return_value = highlight_type

    highlight_query = MagicMock()
    highlight_query.filter.return_value.first.return_value = None  # no existing highlight

    db_session_mock.query.side_effect = [type_query, highlight_query]

    mock_strategy = MagicMock()
    mock_strategy.should_generate_highlight.return_value = True
    mock_strategy.generate_highlight_text.return_value = "High BP: 180/110 mmHg"

    with mock.patch("app.services.highlight_helper.HighlightStrategyFactory") as mock_factory_cls, \
         mock.patch("app.services.highlight_helper.log_crud_action") as mock_log:
        mock_factory_cls.return_value.get_strategy.return_value = mock_strategy

        create_highlight_if_needed(
            db=db_session_mock,
            source_record=MagicMock(),
            type_code="VITAL",
            patient_id=42,
            source_table="PATIENT_VITAL",
            source_record_id=7,
            created_by="user_service",
            user_full_name="User Service",
        )

    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["action"] == ActionType.CREATE
    assert kwargs["user"] == "user_service"
    assert kwargs["user_full_name"] == "User Service"
    assert kwargs["table"] == "PatientHighlight"
    assert kwargs["patient_id"] == 42
    db_session_mock.add.assert_called_once()


def test_create_branch_defaults_user_full_name_to_created_by_when_omitted(db_session_mock):
    """Backward compatibility for callers (patient_problem_crud.py, patient_vital_router.py)
    that don't pass user_full_name at all."""
    highlight_type = _enabled_type()

    type_query = MagicMock()
    type_query.filter.return_value.first.return_value = highlight_type

    highlight_query = MagicMock()
    highlight_query.filter.return_value.first.return_value = None

    db_session_mock.query.side_effect = [type_query, highlight_query]

    mock_strategy = MagicMock()
    mock_strategy.should_generate_highlight.return_value = True
    mock_strategy.generate_highlight_text.return_value = "Some highlight text"

    with mock.patch("app.services.highlight_helper.HighlightStrategyFactory") as mock_factory_cls, \
         mock.patch("app.services.highlight_helper.log_crud_action") as mock_log:
        mock_factory_cls.return_value.get_strategy.return_value = mock_strategy

        create_highlight_if_needed(
            db=db_session_mock,
            source_record=MagicMock(),
            type_code="PROBLEM",
            patient_id=1,
            source_table="PATIENT_PROBLEM",
            source_record_id=3,
            created_by="user_service",
        )

    assert mock_log.call_args.kwargs["user_full_name"] == "user_service"


def test_update_branch_logs_update(db_session_mock):
    existing_highlight = MagicMock(
        Id=55, PatientId=42, HighlightTypeId=9, HighlightText="Old text",
        SourceTable="PATIENT_VITAL", SourceRecordId=7, IsDeleted=0,
        CreatedById="user_service", ModifiedById="user_service",
    )
    highlight_type = _enabled_type()

    type_query = MagicMock()
    type_query.filter.return_value.first.return_value = highlight_type

    highlight_query = MagicMock()
    highlight_query.filter.return_value.first.return_value = existing_highlight

    db_session_mock.query.side_effect = [type_query, highlight_query]

    mock_strategy = MagicMock()
    mock_strategy.should_generate_highlight.return_value = True
    mock_strategy.generate_highlight_text.return_value = "New text"

    with mock.patch("app.services.highlight_helper.HighlightStrategyFactory") as mock_factory_cls, \
         mock.patch("app.services.highlight_helper.log_crud_action") as mock_log:
        mock_factory_cls.return_value.get_strategy.return_value = mock_strategy

        create_highlight_if_needed(
            db=db_session_mock,
            source_record=MagicMock(),
            type_code="VITAL",
            patient_id=42,
            source_table="PATIENT_VITAL",
            source_record_id=7,
            created_by="user_service",
            user_full_name="User Service",
        )

    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["action"] == ActionType.UPDATE
    assert kwargs["entity_id"] == 55
    assert kwargs["original_data"]["HighlightText"] == "Old text"
    assert kwargs["updated_data"]["HighlightText"] == "New text"


def test_delete_branch_logs_delete_when_no_longer_qualifies(db_session_mock):
    existing_highlight = MagicMock(
        Id=55, PatientId=42, HighlightTypeId=9, HighlightText="Old text",
        SourceTable="PATIENT_VITAL", SourceRecordId=7, IsDeleted=0,
        CreatedById="user_service", ModifiedById="user_service",
    )
    highlight_type = _enabled_type()

    type_query = MagicMock()
    type_query.filter.return_value.first.return_value = highlight_type

    highlight_query = MagicMock()
    highlight_query.filter.return_value.first.return_value = existing_highlight

    db_session_mock.query.side_effect = [type_query, highlight_query]

    mock_strategy = MagicMock()
    mock_strategy.should_generate_highlight.return_value = False

    with mock.patch("app.services.highlight_helper.HighlightStrategyFactory") as mock_factory_cls, \
         mock.patch("app.services.highlight_helper.log_crud_action") as mock_log:
        mock_factory_cls.return_value.get_strategy.return_value = mock_strategy

        create_highlight_if_needed(
            db=db_session_mock,
            source_record=MagicMock(),
            type_code="VITAL",
            patient_id=42,
            source_table="PATIENT_VITAL",
            source_record_id=7,
            created_by="user_service",
            user_full_name="User Service",
        )

    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["action"] == ActionType.DELETE
    assert kwargs["entity_id"] == 55
    assert kwargs["updated_data"] is None


def test_delete_branch_logs_delete_when_type_disabled(db_session_mock):
    existing_highlight = MagicMock(
        Id=77, PatientId=42, HighlightTypeId=9, HighlightText="Some text",
        SourceTable="PATIENT_VITAL", SourceRecordId=7, IsDeleted=0,
        CreatedById="user_service", ModifiedById="user_service",
    )
    disabled_type = MagicMock(Id=9, TypeCode="VITAL", IsEnabled=False, IsDeleted=False)

    type_query = MagicMock()
    type_query.filter.return_value.first.return_value = disabled_type

    highlight_query = MagicMock()
    highlight_query.filter.return_value.first.return_value = existing_highlight

    db_session_mock.query.side_effect = [type_query, highlight_query]

    with mock.patch("app.services.highlight_helper.log_crud_action") as mock_log:
        create_highlight_if_needed(
            db=db_session_mock,
            source_record=MagicMock(),
            type_code="VITAL",
            patient_id=42,
            source_table="PATIENT_VITAL",
            source_record_id=7,
            created_by="user_service",
            user_full_name="User Service",
        )

    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["action"] == ActionType.DELETE
    assert kwargs["entity_id"] == 77
    assert "disabled" in kwargs["message"].lower()
