"""HS domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class HSRecord:
    """Horse market transaction price record (競走馬市場取引価格)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    pedigree_reg_num: str | None
    sire_breeding_reg_num: str | None
    dam_breeding_reg_num: str | None
    birth_year: int | None
    market_code: str | None
    organizer_name: str | None
    market_name: str | None
    market_start_date: date | None
    market_end_date: date | None
    horse_age_at_trade: int | None
    trade_price: int | None
