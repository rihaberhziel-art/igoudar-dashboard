"""
config.py
Static configuration for the IGOUDAR — Global Markets Dashboard.
No market data lives here — only structural configuration:
tickers, sectors, display names, colors, and constants.
"""

from datetime import date
from zoneinfo import ZoneInfo

# ------------------------------------------------------------------
# TIMEZONE
# ------------------------------------------------------------------
US_MARKET_TZ = ZoneInfo("America/New_York")

# ------------------------------------------------------------------
# REFERENCE DATE
# ------------------------------------------------------------------
# Dec 25, 2025 (Christmas) was a US market holiday (NYSE/NASDAQ closed).
# The last trading day before it was Dec 24, 2025 (a half day, closed 1pm ET).
# We therefore use Dec 24, 2025 as the performance reference date.
REQUESTED_REFERENCE_DATE = date(2025, 12, 25)
REFERENCE_DATE = date(2025, 12, 24)
REFERENCE_DATE_LABEL = "Dec 24, 2025"
REFERENCE_DATE_NOTE = (
    "Reference date adjusted from Dec 25, 2025 to Dec 24, 2025 "
    "because Dec 25, 2025 was a US market holiday (Christmas Day)."
)

# ------------------------------------------------------------------
# INSTRUMENT UNIVERSE
# Ticker -> (Display Name, Sector)
# Sector buckets exactly as requested: Technology, Industrials,
# Financials, Healthcare, ETFs, Energy / Metals.
# ------------------------------------------------------------------
SECTOR_TECHNOLOGY = "Technology"
SECTOR_INDUSTRIALS = "Industrials"
SECTOR_FINANCIALS = "Financials"
SECTOR_HEALTHCARE = "Healthcare"
SECTOR_ETF = "ETFs"
SECTOR_ENERGY_METALS = "Energy / Metals"

SECTORS_ORDER = [
    SECTOR_TECHNOLOGY,
    SECTOR_INDUSTRIALS,
    SECTOR_FINANCIALS,
    SECTOR_HEALTHCARE,
    SECTOR_ETF,
    SECTOR_ENERGY_METALS,
]

# NOTE ON GOOGL vs GOOG: the source list said "Google" without specifying
# the share class. GOOGL (Class A, voting) is used by default, as instructed.
# This is flagged explicitly in the UI (see app.py "Data notes" expander).
GOOGL_AMBIGUITY_NOTE = (
    "Ticker 'GOOGL' was used for Alphabet/Google (Class A shares) because "
    "the source list did not specify GOOGL vs GOOG. Flagged per instructions."
)

INSTRUMENTS = {
    # --- Technology (15) ---
    "GOOGL": ("Alphabet Inc. (Class A)", SECTOR_TECHNOLOGY),
    "NVDA":  ("NVIDIA Corporation", SECTOR_TECHNOLOGY),
    "MU":    ("Micron Technology, Inc.", SECTOR_TECHNOLOGY),
    "WDC":   ("Western Digital Corporation", SECTOR_TECHNOLOGY),
    "STX":   ("Seagate Technology Holdings plc", SECTOR_TECHNOLOGY),
    "AVGO":  ("Broadcom Inc.", SECTOR_TECHNOLOGY),
    "KLAC":  ("KLA Corporation", SECTOR_TECHNOLOGY),
    "LRCX":  ("Lam Research Corporation", SECTOR_TECHNOLOGY),
    "MSFT":  ("Microsoft Corporation", SECTOR_TECHNOLOGY),
    "PLTR":  ("Palantir Technologies Inc.", SECTOR_TECHNOLOGY),
    "APP":   ("AppLovin Corporation", SECTOR_TECHNOLOGY),
    "SNDK":  ("Sandisk Corporation", SECTOR_TECHNOLOGY),
    "CLS":   ("Celestica Inc.", SECTOR_TECHNOLOGY),
    "TSM":   ("Taiwan Semiconductor Manufacturing Co.", SECTOR_TECHNOLOGY),
    "INTC":  ("Intel Corporation", SECTOR_TECHNOLOGY),

    # --- Industrials (4) ---
    "CAT":   ("Caterpillar Inc.", SECTOR_INDUSTRIALS),
    "BWXT":  ("BWX Technologies, Inc.", SECTOR_INDUSTRIALS),
    "HWM":   ("Howmet Aerospace Inc.", SECTOR_INDUSTRIALS),
    "GE":    ("GE Aerospace", SECTOR_INDUSTRIALS),

    # --- Financials (7) ---
    "JPM":   ("JPMorgan Chase & Co.", SECTOR_FINANCIALS),
    "BAC":   ("Bank of America Corporation", SECTOR_FINANCIALS),
    "HOOD":  ("Robinhood Markets, Inc.", SECTOR_FINANCIALS),
    "MS":    ("Morgan Stanley", SECTOR_FINANCIALS),
    "AXP":   ("American Express Company", SECTOR_FINANCIALS),
    "V":     ("Visa Inc.", SECTOR_FINANCIALS),
    "ALLY":  ("Ally Financial Inc.", SECTOR_FINANCIALS),

    # --- Healthcare (6) ---
    "ISRG":  ("Intuitive Surgical, Inc.", SECTOR_HEALTHCARE),
    "JNJ":   ("Johnson & Johnson", SECTOR_HEALTHCARE),
    "LLY":   ("Eli Lilly and Company", SECTOR_HEALTHCARE),
    "VKTX":  ("Viking Therapeutics, Inc.", SECTOR_HEALTHCARE),
    "DVAX":  ("Dynavax Technologies Corporation", SECTOR_HEALTHCARE),
    "OMER":  ("Omeros Corporation", SECTOR_HEALTHCARE),

    # --- ETFs (7) ---
    "ICLN":  ("iShares Global Clean Energy ETF", SECTOR_ETF),
    "TQQQ":  ("ProShares UltraPro QQQ", SECTOR_ETF),
    "VTV":   ("Vanguard Value ETF", SECTOR_ETF),
    "AGG":   ("iShares Core U.S. Aggregate Bond ETF", SECTOR_ETF),
    "EEM":   ("iShares MSCI Emerging Markets ETF", SECTOR_ETF),
    "SLVP":  ("iShares MSCI Global Silver & Metals Miners ETF", SECTOR_ETF),
    "GLD":   ("SPDR Gold Shares", SECTOR_ETF),

    # --- Energy / Metals (13) ---
    "KGC":   ("Kinross Gold Corporation", SECTOR_ENERGY_METALS),
    "SLV":   ("iShares Silver Trust", SECTOR_ENERGY_METALS),
    "AA":    ("Alcoa Corporation", SECTOR_ENERGY_METALS),
    "NEM":   ("Newmont Corporation", SECTOR_ENERGY_METALS),
    "SCCO":  ("Southern Copper Corporation", SECTOR_ENERGY_METALS),
    "FCX":   ("Freeport-McMoRan Inc.", SECTOR_ENERGY_METALS),
    "IAG":   ("IAMGOLD Corporation", SECTOR_ENERGY_METALS),
    "CDE":   ("Coeur Mining, Inc.", SECTOR_ENERGY_METALS),
    "PAAS":  ("Pan American Silver Corp.", SECTOR_ENERGY_METALS),
    "EQX":   ("Equinox Gold Corp.", SECTOR_ENERGY_METALS),
    "AGI":   ("Alamos Gold Inc.", SECTOR_ENERGY_METALS),
    "NEE":   ("NextEra Energy, Inc.", SECTOR_ENERGY_METALS),
    "FSLR":  ("First Solar, Inc.", SECTOR_ENERGY_METALS),
}

EXPECTED_INSTRUMENT_COUNT = 52

# ------------------------------------------------------------------
# VISUAL THEME (institutional / Bloomberg-style dark terminal)
# ------------------------------------------------------------------
COLOR_BG = "#0B1220"          # near-black navy background
COLOR_BG_CARD = "#111A2C"     # card background
COLOR_BG_CARD_ALT = "#0F1A2E"
COLOR_BORDER = "#22304A"
COLOR_TEXT = "#F5F7FA"
COLOR_TEXT_MUTED = "#8A97AD"
COLOR_ACCENT = "#3B82F6"      # institutional blue accent
COLOR_ACCENT_GOLD = "#C9A24B" # subtle gold accent (nods to "Igoudar")
COLOR_POSITIVE = "#22C55E"    # green
COLOR_NEGATIVE = "#EF4444"    # red
COLOR_NEUTRAL = "#94A3B8"     # neutral gray

# ------------------------------------------------------------------
# CACHE / REFRESH SETTINGS
# ------------------------------------------------------------------
CACHE_TTL_SECONDS = 120          # market data cache lifetime
AUTO_REFRESH_MS = 120_000        # optional auto-refresh interval (2 min)

DISCLAIMER = (
    "This dashboard is for informational purposes only and does not "
    "constitute investment advice."
)
