# IGOUDAR — Global Markets Dashboard

Institutional-style, dark-terminal Streamlit dashboard tracking 52 stocks/ETFs
across Technology, Industrials, Financials, Healthcare, ETFs, and
Energy/Metals — showing performance since **Dec 24, 2025** (last trading day
before the Dec 25, 2025 US market holiday) vs. the latest available price.

Built for a two-day live investor event: **no dates are hardcoded** — the app
detects "today" and "now" (US Eastern Time) automatically every time it's
opened or refreshed, so it works unattended on Day 1, Day 2, and beyond.

---

## Project structure

```
igoudar-dashboard/
├── app.py             # Streamlit UI — all sections, charts, tables
├── data.py            # Yahoo Finance retrieval, caching, validation layer
├── config.py           # Ticker universe, sectors, colors, constants
├── utils.py            # Formatting helpers ($ / % / dates)
├── requirements.txt
└── README.md
```

## 1. Local installation

Requires Python 3.10+.

```bash
cd igoudar-dashboard
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run locally

```bash
streamlit run app.py
```

This opens the dashboard at `http://localhost:8501`. For the stand display,
open it in a browser in **fullscreen (F11)** at 1920×1080.

**Important — internet access required.** The app calls Yahoo Finance
live via `yfinance`. It must run on a machine/network that can reach
`query1.finance.yahoo.com` / `query2.finance.yahoo.com` (i.e. normal
unrestricted internet — this will NOT work behind a network that blocks
Yahoo Finance).

## 3. Deploy to Streamlit Community Cloud (recommended for the event)

1. Push this folder to a **public or private GitHub repo**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
3. Click **"New app"**, select the repo, branch, and set the main file
   to `app.py`.
4. Deploy. Streamlit Cloud installs `requirements.txt` automatically.
5. Once live, open the app URL on the stand's screen/laptop and leave it
   open — use the in-app **"↻ Refresh Market Data"** button whenever you
   want to force an immediate update, or just reload the page.

No secrets/API keys are required — Yahoo Finance data via `yfinance` is
free and keyless.

## 4. How automatic date detection works

- `data.now_eastern()` calls `datetime.now(tz=ZoneInfo("America/New_York"))`
  **every time the page renders** — nothing about "today" is ever stored
  or hardcoded. On day 2 of the event, the header, KPI period, and
  "Data updated" stamp update themselves with zero code changes.
- `data.is_us_market_open()` checks the current ET time against the
  09:30–16:00 regular session window (Mon–Fri) to decide whether to label
  prices "live" or "latest available closing price."
- The **reference date** is fixed at **Dec 24, 2025** (config.py), because
  Dec 25, 2025 was a market holiday — this is the one date in the app that
  is intentionally fixed, since it's the historical baseline for the
  performance calculation, not "today."

## 5. How market data is refreshed

- All Yahoo Finance calls go through `st.cache_data(ttl=120s)` in `data.py`,
  so the app doesn't re-hit Yahoo Finance on every single widget
  interaction (filtering the table, picking a different ticker in the
  Explorer, etc.) — only when the cache expires or is explicitly cleared.
- The **"↻ Refresh Market Data"** button clears the cache
  (`st.cache_data.clear()`) and reruns the app, forcing a fresh pull for
  all 52 instruments and the selected Explorer chart.
- Reference prices (Dec 24, 2025 close) are cached the same way but change
  far less often in practice, since that date is in the past.
- If you want true unattended auto-refresh (no one pressing the button),
  the simplest reliable option is an OS-level browser auto-reload
  extension or a kiosk browser configured to refresh the tab every few
  minutes — Streamlit Cloud's own session lifetime handles the rest.

## 6. Data quality & validation

On every load, `data.validate_universe()` checks:
- Exactly 52 configured instruments, no duplicate tickers, valid sectors
- Every instrument has both a reference price and a latest price
- No non-positive prices
- Any failure is shown as **"N/A"** for that instrument with a reason
  in the "⚠ Data quality notes" expander — nothing is ever fabricated
  or estimated.

## 7. Known caveats to check before the event

- **GOOGL vs GOOG**: the source list said "Google" without a share class.
  `GOOGL` (Class A) is used by default — flagged in the "ℹ Data notes"
  expander in the app. Swap to `GOOG` in `config.py` if the investor
  wants Class C instead.
- Some smaller-cap tickers (e.g. `VKTX`, `DVAX`, `OMER`, `SNDK`, `EQX`)
  can occasionally have gaps or delayed data on Yahoo Finance — the
  validation layer will surface these as "N/A" rather than guessing.
- **Test this on the actual event WiFi at least once before the event**,
  since some corporate/conference networks block financial-data domains.
  If Yahoo Finance is blocked on-site, use a phone hotspot as a fallback.

---

*This dashboard is for informational purposes only and does not
constitute investment advice.*
