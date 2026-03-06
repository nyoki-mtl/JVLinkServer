"""Tests for JRACodeTables helper methods."""

from __future__ import annotations

import pytest

from pyjvlink.codes import JRACodeTables
from pyjvlink.errors import JVInvalidParameterError


def test_list_table_names_contains_known_table() -> None:
    table_names = JRACodeTables.list_table_names()
    assert "RACECOURSE_CODES" in table_names
    assert "WEATHER_CODES" in table_names


def test_get_table_by_name_is_case_insensitive() -> None:
    racecourse_table = JRACodeTables.get_table("racecourse_codes")
    assert racecourse_table["05"] == "東京競馬場"


def test_get_table_unknown_raises_validation_error() -> None:
    with pytest.raises(JVInvalidParameterError, match="Unknown code table"):
        JRACodeTables.get_table("UNKNOWN_CODES")


def test_has_code_and_get_name() -> None:
    assert JRACodeTables.has_code("WEATHER_CODES", "1")
    assert JRACodeTables.get_name("WEATHER_CODES", "1") == "晴"
    assert JRACodeTables.get_name("WEATHER_CODES", "9", default="不明") == "不明"
