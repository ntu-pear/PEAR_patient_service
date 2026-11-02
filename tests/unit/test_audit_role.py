"""Audit entries carry the actor's role when one is given, and only then."""
import json
import logging
from unittest.mock import patch

from app.logger import logger_utils
from app.logger.config import ConditionalFormatter


def _extra(**kwargs):
    with patch.object(logger_utils.logger, "info") as info:
        logger_utils.log_crud_action(
            action=logger_utils.ActionType.CREATE,
            user="U1",
            user_full_name="Sam Lee",
            message="m",
            table="T",
            **kwargs,
        )
    return info.call_args.kwargs["extra"]


def test_role_is_passed_when_given():
    assert _extra(role="CAREGIVER")["role"] == "CAREGIVER"


def test_role_is_absent_by_default():
    assert "role" not in _extra()


def _format(**extra):
    record = logging.LogRecord("x", logging.INFO, __file__, 1, {"entity_id": 1}, None, None)
    fields = {"user": "U1", "user_full_name": "Sam Lee", "table": "T", "action": "create", "log_text": "m"}
    for key, value in {**fields, **extra}.items():
        setattr(record, key, value)
    return json.loads(ConditionalFormatter().format(record))


def test_formatter_emits_role_only_when_set():
    assert _format(role="SUPERVISOR")["role"] == "SUPERVISOR"
    assert "role" not in _format()
