"""
data.py
All market-data retrieval logic (Yahoo Finance via yfinance).

Design principles (per spec):
- Never hardcode prices.
- Never fabricate a value if data is missing -> use None / "N/A".
- Reference price = last close on/before config.REFERENCE_DATE (Dec 24, 2025).
- Latest price = most recent available price (live if market open,
  last close if market closed).
- Cached with a short TTL so a manual "Refresh" button and periodic
  auto-refresh don't hammer Yahoo Finance with requests.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st
import yfinance as yf

import config


# ------------------------------------------------------------------
# TIME HELPERS (dynamic — never hardcoded)
# ------------------------------------------------------------------
def now_eastern() -> dt.datetime:
    """Current date & time in US Eastern Time, computed fresh every call."""
    return dt.datetime.now(tz=config.US_MARKET_TZ)


def is_us_market_open(now: Optional[dt.datetime] = None) -> bool:
    """
    Rough regular-session check (09:30-16:00 ET, Mon-Fri).
    Does not special-case holidays (yfinance data itself reflects holidays
    via the absence of a new trading bar), which is sufficient for a
    "latest available price" style dashboard.
    """
    now = now or now_eastern()
    if now.weekday() >= 5:  # Sat/Sun
        return False
    open_t = now.replace(hour=9, minute=30, second=0, microsecond=0)
    close_t = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_t <= now <= close_t


# ------------------------------------------------------------------
# DATA STRUCTURES
# ------------------------------------------------------------------
@dataclass
class InstrumentRow:
    ticker: str
    name: str
    sector: str
    reference_price: Optional[float]
    reference_date_used: Optional[str]
    latest_price: Optional[float]
    latest_price_date: Optional[str]
    change_abs: Optional[float]
    change_pct: Optional[float]
    status: str  # "ok" | "partial" | "error"
    error_message: Optional[str] = None


# ------------------------------------------------------------------
# CORE FETCH (cached)
# ------------------------------------------------------------------
@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def fetch_history(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    """
    Download daily OHLC history for a single ticker between start and end
    (inclusive-ish; yfinance's `end` is exclusive so we pad by 1 day).
    Returns an empty DataFrame on failure — never raises up to the caller,
    and never fabricates data.
    """
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(
            start=start.isoformat(),
            end=(end + dt.timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=False,
        )
        if hist is None or hist.empty:
            return pd.DataFrame()
        hist = hist[~hist.index.duplicated(keep="last")]
        return hist
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def fetch_latest_quote(ticker: str) -> dict:
    """
    Best-effort "latest price" lookup that works whether the market is
    open or closed:
      1. Try fast_info.last_price (works intraday when market is open).
      2. Fall back to the last row of recent daily history (last close).
    Returns {} on total failure.
    """
    try:
        tk = yf.Ticker(ticker)
        price = None
        price_date = None

        try:
            fi = tk.fast_info
            price = getattr(fi, "last_price", None) or fi.get("last_price")
        except Exception:
            price = None

        if price is None or (isinstance(price, float) and pd.isna(price)):
            recent = tk.history(period="5d", interval="1d", auto_adjust=False)
            if recent is not None and not recent.empty:
                price = float(recent["Close"].iloc[-1])
                price_date = recent.index[-1].date().isoformat()
        else:
            price_date = dt.date.today().isoformat()

        if price is None:
            return {}
        return {"price": float(price), "date": price_date}
    except Exception:
        return {}


def get_reference_price(ticker: str) -> tuple[Optional[float], Optional[str]]:
    """
    Reference price = last available close on or before config.REFERENCE_DATE.
    Looks back up to 7 calendar days to be resilient to any additional
    unexpected holidays/gaps, but never forward past REFERENCE_DATE.
    """
    lookback_start = config.REFERENCE_DATE - dt.timedelta(days=7)
    hist = fetch_history(ticker, lookback_start, config.REFERENCE_DATE)
    if hist.empty:
        return None, None
    hist = hist[hist.index.date <= config.REFERENCE_DATE]
    if hist.empty:
        return None, None
    last_row = hist.iloc[-1]
    used_date = hist.index[-1].date().isoformat()
    return float(last_row["Close"]), used_date


def build_instrument_row(ticker: str) -> InstrumentRow:
    name, sector = config.INSTRUMENTS[ticker]

    ref_price, ref_date_used = get_reference_price(ticker)
    quote = fetch_latest_quote(ticker)
    latest_price = quote.get("price")
    latest_date = quote.get("date")

    if ref_price is None or latest_price is None:
        status = "error"
        change_abs = None
        change_pct = None
        missing = []
        if ref_price is None:
            missing.append("reference price")
        if latest_price is None:
            missing.append("latest price")
        error_message = f"Missing: {', '.join(missing)}"
    elif ref_price <= 0 or latest_price <= 0:
        status = "error"
        change_abs = None
        change_pct = None
        error_message = "Non-positive price encountered"
    else:
        status = "ok"
        change_abs = latest_price - ref_price
        change_pct = (change_abs / ref_price) * 100.0
        error_message = None

    return InstrumentRow(
        ticker=ticker,
        name=name,
        sector=sector,
        reference_price=ref_price,
        reference_date_used=ref_date_used,
        latest_price=latest_price,
        latest_price_date=latest_date,
        change_abs=change_abs,
        change_pct=change_pct,
        status=status,
        error_message=error_message,
    )


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def build_universe_dataframe(_cache_bust: str) -> pd.DataFrame:
    """
    Builds the full 52-instrument dataframe.
    `_cache_bust` is a caller-supplied string (e.g. a timestamp bucket or
    a manual refresh token) used purely to control cache invalidation
    from the Streamlit "Refresh Data" button.
    """
    rows = [build_instrument_row(t) for t in config.INSTRUMENTS.keys()]
    df = pd.DataFrame([r.__dict__ for r in rows])
    return df


def fetch_price_series(ticker: str) -> pd.DataFrame:
    """Full Dec 24, 2025 -> latest daily price series for the explorer chart."""
    today = dt.date.today()
    hist = fetch_history(ticker, config.REFERENCE_DATE, today)
    return hist


# ------------------------------------------------------------------
# VALIDATION LAYER (section 18 of the spec)
# ------------------------------------------------------------------
def validate_universe(df: pd.DataFrame) -> list[str]:
    """Returns a list of human-readable validation issues (empty = all clear)."""
    issues = []

    if len(config.INSTRUMENTS) != config.EXPECTED_INSTRUMENT_COUNT:
        issues.append(
            f"Configured instrument count is {len(config.INSTRUMENTS)}, "
            f"expected {config.EXPECTED_INSTRUMENT_COUNT}."
        )

    tickers = list(config.INSTRUMENTS.keys())
    dupes = {t for t in tickers if tickers.count(t) > 1}
    if dupes:
        issues.append(f"Duplicate tickers found: {sorted(dupes)}")

    valid_sectors = set(config.SECTORS_ORDER)
    for t, (_, sector) in config.INSTRUMENTS.items():
        if sector not in valid_sectors:
            issues.append(f"{t}: invalid sector '{sector}'")

    if df is not None and not df.empty:
        for _, row in df.iterrows():
            t = row["ticker"]
            if row["status"] == "error":
                issues.append(f"{t}: {row['error_message']}")
                continue
            if row["reference_price"] is not None and row["reference_price"] <= 0:
                issues.append(f"{t}: non-positive reference price")
            if row["latest_price"] is not None and row["latest_price"] <= 0:
                issues.append(f"{t}: non-positive latest price")

    return issues
