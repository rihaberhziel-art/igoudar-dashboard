"""
utils.py
Pure formatting/helper functions used by app.py.
"""

from __future__ import annotations

import datetime as dt
from typing import Optional

import config


def fmt_usd(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def fmt_pct(value: Optional[float], signed: bool = True) -> str:
    if value is None:
        return "N/A"
    sign = "+" if (signed and value > 0) else ""
    return f"{sign}{value:,.2f}%"


def fmt_change(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:,.2f}"


def pct_color(value: Optional[float]) -> str:
    if value is None:
        return config.COLOR_NEUTRAL
    if value > 0:
        return config.COLOR_POSITIVE
    if value < 0:
        return config.COLOR_NEGATIVE
    return config.COLOR_NEUTRAL


def format_asof(now: dt.datetime) -> str:
    """'Sep 02, 2026 | 10:41 AM ET' style stamp — always computed live."""
    return now.strftime("%b %d, %Y | %I:%M %p ET").replace(" 0", " ")


def performance_period_label(now: dt.datetime) -> str:
    return f"{config.REFERENCE_DATE_LABEL} → {now.strftime('%b %d, %Y')}"
