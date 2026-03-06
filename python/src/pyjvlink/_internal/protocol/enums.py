"""Protocol layer enums."""

from enum import Enum


class SaleFlag(str, Enum):
    """O1 sale status."""

    NO_SALE = "0"
    CANCELLED_BEFORE_SALE = "1"
    CANCELLED_AFTER_SALE = "3"
    ON_SALE = "7"
