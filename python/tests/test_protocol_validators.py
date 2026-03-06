"""Tests for protocol validators."""

from pyjvlink._internal.protocol.enums import SaleFlag
from pyjvlink._internal.protocol.validators import (
    to_date_yyyymmdd,
    to_enum,
    to_float,
    to_int,
    to_mmddhhmm_parts,
    to_month_day,
    to_time_hhmm,
)


def test_to_int_and_float() -> None:
    assert to_int("0012") == 12
    assert to_int("abc") is None
    assert to_float("0123", scale=10) == 12.3


def test_to_date_and_month_day() -> None:
    assert str(to_date_yyyymmdd("20260302")) == "2026-03-02"
    assert to_date_yyyymmdd("20260230") is None
    assert to_month_day("0302") == (3, 2)
    assert to_month_day("1399") == (None, None)


def test_to_time_and_mmddhhmm_parts() -> None:
    assert str(to_time_hhmm("1545")) == "15:45:00"
    assert to_time_hhmm("0000") is None
    assert to_time_hhmm("2460") is None
    assert to_mmddhhmm_parts("03020930") == (3, 2, 9, 30)
    assert to_mmddhhmm_parts("13329999") == (None, None, None, None)


def test_to_enum() -> None:
    assert to_enum("7", SaleFlag) == SaleFlag.ON_SALE
    assert to_enum("x", SaleFlag) is None
