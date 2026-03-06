"""JG domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class JGRecord(RaceRecordBase):
    """Horse exclusion info record."""

    pedigree_reg_num: str | None
    horse_name: str | None
    entry_order: int | None
    entry_code: str | None
    exclusion_code: str | None
