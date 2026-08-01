"""Cleaning + validation. This is the 'is this data actually good?' gate.

Every number that comes back from an API passes through here before an agent is
allowed to use it. If something is missing, non-numeric, or nonsensical, we raise
DataQualityError instead of letting bad data reach a trading decision.
"""
from __future__ import annotations


class DataQualityError(Exception):
    """The data failed a sanity check."""


def as_float(value, field: str = "value") -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise DataQualityError(f"{field} is not a number: {value!r}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DataQualityError(message)


def clean_quote(raw: dict, symbol: str) -> dict:
    """Turn a raw Twelve Data quote into a small, checked dict."""
    require(isinstance(raw, dict), f"{symbol}: no quote returned")
    price = as_float(raw.get("close") or raw.get("price"), f"{symbol} price")
    require(price > 0, f"{symbol}: price is not positive ({price})")

    pct_raw = raw.get("percent_change")
    percent_change = as_float(pct_raw, f"{symbol} percent_change") if pct_raw is not None else None

    return {"symbol": symbol, "price": price, "percent_change": percent_change}
