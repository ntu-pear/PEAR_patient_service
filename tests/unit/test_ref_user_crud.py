from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.crud.ref_user_crud import create_ref_userconfig, update_ref_userconfig
from app.logger.logger_utils import ActionType
from app.models.ref_userconfig_model import RefUserConfig
from app.schemas.ref_userconfig import refUserConfigCreate, refUserConfigUpdate
from tests.utils.mock_db import get_db_session_mock


@pytest.fixture
def db_session_mock():
    """Fixture to mock the database session."""
    return get_db_session_mock()


def test_create_ref_userconfig_logs_create_action(db_session_mock):
    """create_ref_userconfig must call log_crud_action once with ActionType.CREATE."""
    userconfig_data = refUserConfigCreate(
        UserConfigId=501,
        configBlob={"theme": "dark"},
        modifiedDate=datetime(2024, 1, 1),
        modifiedById="user_service",
    )

    created_row = RefUserConfig(
        UserConfigID=501,
        configBlob='{"theme": "dark"}',
        modifiedDate=datetime(2024, 1, 1),
        modifiedById="user_service",
    )

    query_mock = MagicMock()
    # 1st .first() call: existing-check inside create_operation -> None (no duplicate)
    # 2nd .first() call: re-fetch of the created row
    query_mock.filter.return_value.first.side_effect = [None, created_row]
    db_session_mock.query.return_value = query_mock

    with mock.patch(
        "app.crud.ref_user_crud.IdempotencyService.process_idempotent"
    ) as mock_process_idempotent, mock.patch(
        "app.crud.ref_user_crud.log_crud_action"
    ) as mock_log:
        mock_process_idempotent.side_effect = lambda **kwargs: (kwargs["operation"](), False)

        result, was_duplicate = create_ref_userconfig(
            db_session_mock,
            userconfig_data,
            correlation_id="corr-1",
            created_by="user_service",
        )

    assert was_duplicate is False
    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["action"] == ActionType.CREATE
    assert kwargs["user"] == "user_service"
    assert kwargs["table"] == "RefUserConfig"
    assert kwargs["entity_id"] == 501
    assert kwargs["is_system_config"] is True


def test_update_ref_userconfig_logs_update_action(db_session_mock):
    """update_ref_userconfig must call log_crud_action once with ActionType.UPDATE,
    using userconfig_update.modifiedById as the actor (no separate modified_by param exists)."""
    existing_row = RefUserConfig(
        UserConfigID=501,
        configBlob='{"theme": "light"}',
        modifiedDate=datetime(2024, 1, 1),
        modifiedById="user_service",
    )

    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = existing_row
    db_session_mock.query.return_value = query_mock

    update_data = refUserConfigUpdate(
        UserConfigId=501,
        configBlob={"theme": "dark"},
        modifiedDate=datetime(2024, 1, 2),
        modifiedById="user_service_2",
    )

    with mock.patch(
        "app.crud.ref_user_crud.IdempotencyService.process_idempotent"
    ) as mock_process_idempotent, mock.patch(
        "app.crud.ref_user_crud.log_crud_action"
    ) as mock_log:
        mock_process_idempotent.side_effect = lambda **kwargs: (kwargs["operation"](), False)

        result, was_duplicate = update_ref_userconfig(
            db_session_mock,
            userconfig_id="501",
            userconfig_update=update_data,
            correlation_id="corr-2",
        )

    assert was_duplicate is False
    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["action"] == ActionType.UPDATE
    assert kwargs["user"] == "user_service_2"
    assert kwargs["table"] == "RefUserConfig"
    assert kwargs["entity_id"] == 501
    assert kwargs["original_data"]["configBlob"] == '{"theme": "light"}'
    assert kwargs["is_system_config"] is True


def test_update_ref_userconfig_sync_event_logs_update_action(db_session_mock):
    """The skip_duplicate_check=True (sync event) branch must also log, since it
    converges with the normal branch before the log call."""
    existing_row = RefUserConfig(
        UserConfigID=501,
        configBlob='{"theme": "light"}',
        modifiedDate=datetime(2024, 1, 1),
        modifiedById="user_service",
    )

    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = existing_row
    db_session_mock.query.return_value = query_mock

    update_data = refUserConfigUpdate(
        UserConfigId=501,
        configBlob={"theme": "dark"},
        modifiedDate=datetime(2024, 1, 2),
        modifiedById="sync_service",
    )

    with mock.patch(
        "app.crud.ref_user_crud.IdempotencyService.record_processed_event"
    ), mock.patch("app.crud.ref_user_crud.log_crud_action") as mock_log:
        result, was_duplicate = update_ref_userconfig(
            db_session_mock,
            userconfig_id="501",
            userconfig_update=update_data,
            correlation_id="corr-3",
            skip_duplicate_check=True,
        )

    assert was_duplicate is False
    mock_log.assert_called_once()
    assert mock_log.call_args.kwargs["user"] == "sync_service"
