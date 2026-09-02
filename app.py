"""
app.py
IGOUDAR — GLOBAL MARKETS DASHBOARD

Run with:  streamlit run app.py

This file wires together config.py (static config), data.py (all market
data retrieval / caching / validation) and utils.py (formatting), and
renders the full institutional-style dashboard described in the brief.

Nothing in this file hardcodes a date, a time, or a price. The current
date/time is computed fresh on every render via data.now_eastern().
"""

from __future__ import annotations

import base64
import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from PIL import Image

import config
import data
import utils

LOGO_PATH = "assets/igoudar_logo.png"
_favicon = Image.open(LOGO_PATH)
with open(LOGO_PATH, "rb") as _f:
    _LOGO_B64 = base64.b64encode(_f.read()).decode("ascii")

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="IGOUDAR — Global Markets Dashboard",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# GLOBAL CSS — institutional dark terminal look, tuned for 1920x1080
# ------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
        }}
        .stApp {{
            background: radial-gradient(circle at top left, #0E1830 0%, {config.COLOR_BG} 55%);
            color: {config.COLOR_TEXT};
        }}
        #MainMenu, header, footer {{visibility: hidden;}}
        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1900px;
        }}
        .igd-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 1px solid {config.COLOR_BORDER};
            padding-bottom: 14px;
            margin-bottom: 18px;
        }}
        .igd-logo {{
            display: block;
            width: 300px;
            max-width: 100%;
            height: auto;
            margin-bottom: 6px;
        }}
        .igd-subtitle {{
            font-size: 0.95rem;
            color: {config.COLOR_TEXT_MUTED};
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 2px;
        }}
        .igd-updated {{
            text-align: right;
            color: {config.COLOR_TEXT_MUTED};
            font-size: 0.85rem;
            line-height: 1.4;
        }}
        .igd-live-dot {{
            display: inline-block;
            width: 8px; height: 8px;
            border-radius: 50%;
            background: {config.COLOR_POSITIVE};
            margin-right: 6px;
            box-shadow: 0 0 6px {config.COLOR_POSITIVE};
        }}
        .igd-card {{
            background: {config.COLOR_BG_CARD};
            border: 1px solid {config.COLOR_BORDER};
            border-radius: 10px;
            padding: 16px 18px;
        }}
        .igd-kpi-label {{
            color: {config.COLOR_TEXT_MUTED};
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }}
        .igd-kpi-value {{
            font-size: 1.9rem;
            font-weight: 700;
            color: {config.COLOR_TEXT};
        }}
        .igd-section-title {{
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: {config.COLOR_TEXT};
            margin: 26px 0 10px 0;
            border-left: 3px solid {config.COLOR_ACCENT_GOLD};
            padding-left: 10px;
        }}
        .igd-footer {{
            margin-top: 30px;
            border-top: 1px solid {config.COLOR_BORDER};
            padding-top: 14px;
            color: {config.COLOR_TEXT_MUTED};
            font-size: 0.78rem;
            line-height: 1.7;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {config.COLOR_BORDER};
            border-radius: 8px;
        }}
        .stButton>button {{
            background: {config.COLOR_ACCENT};
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            padding: 0.5rem 1.1rem;
        }}
        .stButton>button:hover {{
            background: #2563EB;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=config.COLOR_TEXT, size=13),
    margin=dict(l=10, r=10, t=40, b=10),
)


# ------------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------------
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = "initial"

now = data.now_eastern()
market_open = data.is_us_market_open(now)

with st.spinner("Loading latest market data..."):
    df = data.build_universe_dataframe(st.session_state.refresh_token)

validation_issues = data.validate_universe(df)
ok_df = df[df["status"] == "ok"].copy()

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
header_l, header_r = st.columns([3, 1.4])
with header_l:
    st.markdown(
        f"""
        <img src="data:image/png;base64,{_LOGO_B64}" alt="IGOUDAR — Research, Consult &amp; Invest Wisely" class="igd-logo" />
        <div class="igd-subtitle">Market Performance &nbsp;|&nbsp; {utils.performance_period_label(now)}</div>
        """,
        unsafe_allow_html=True,
    )
with header_r:
    status_word = "MARKET OPEN" if market_open else "MARKET CLOSED"
    price_note = "Live/latest available price" if market_open else "Latest available closing price"
    st.markdown(
        f"""
        <div class="igd-updated">
            <span class="igd-live-dot"></span><b>{status_word}</b> (US Eastern Time)<br>
            {price_note}<br>
            Data updated: {utils.format_asof(now)}
        </div>
        """,
        unsafe_allow_html=True,
    )

btn_col, _ = st.columns([1, 5])
with btn_col:
    if st.button("↻ Refresh Market Data", use_container_width=True):
        st.session_state.refresh_token = dt.datetime.utcnow().isoformat()
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<div style='color:{config.COLOR_TEXT_MUTED}; font-size:0.8rem; margin-top:4px;'>"
            f"Reference date: {config.REFERENCE_DATE_LABEL} — last trading day before Christmas Day"
            f"</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------------
n_total = len(df)
n_ok = len(ok_df)
avg_perf = ok_df["change_pct"].mean() if n_ok else None
n_pos = int((ok_df["change_pct"] > 0).sum()) if n_ok else 0
n_neg = int((ok_df["change_pct"] < 0).sum()) if n_ok else 0

k1, k2, k3, k4 = st.columns(4)
kpi_defs = [
    (k1, "Instruments Tracked", f"{n_total}"),
    (k2, "Average Performance", utils.fmt_pct(avg_perf)),
    (k3, "Positive Performers", f"{n_pos}"),
    (k4, "Negative Performers", f"{n_neg}"),
]
for col, label, value in kpi_defs:
    color = config.COLOR_TEXT
    if "Performance" in label:
        color = utils.pct_color(avg_perf)
    elif "Positive" in label:
        color = config.COLOR_POSITIVE
    elif "Negative" in label:
        color = config.COLOR_NEGATIVE
    col.markdown(
        f"""<div class="igd-card">
                <div class="igd-kpi-label">{label}</div>
                <div class="igd-kpi-value" style="color:{color}">{value}</div>
            </div>""",
        unsafe_allow_html=True,
    )

if validation_issues:
    with st.expander(f"⚠ Data quality notes ({len(validation_issues)})", expanded=False):
        for issue in validation_issues:
            st.write(f"- {issue}")

with st.expander("ℹ Data notes (ticker ambiguity)", expanded=False):
    st.write(config.GOOGL_AMBIGUITY_NOTE)

# ------------------------------------------------------------------
# SECTOR PERFORMANCE
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">AVERAGE PERFORMANCE BY SECTOR</div>', unsafe_allow_html=True)

if n_ok:
    sector_stats = (
        ok_df.groupby("sector")["change_pct"]
        .agg(avg="mean", median="median",
             positive=lambda s: int((s > 0).sum()),
             negative=lambda s: int((s < 0).sum()))
        .reindex(config.SECTORS_ORDER)
        .dropna(how="all")
        .reset_index()
        .sort_values("avg", ascending=True)
    )
    fig_sector = go.Figure()
    fig_sector.add_trace(go.Bar(
        x=sector_stats["avg"],
        y=sector_stats["sector"],
        orientation="h",
        marker_color=[utils.pct_color(v) for v in sector_stats["avg"]],
        text=[utils.fmt_pct(v) for v in sector_stats["avg"]],
        textposition="outside",
    ))
    fig_sector.update_layout(**PLOTLY_LAYOUT, height=280,
                              xaxis_title="Average performance (%)", yaxis_title=None)
    st.plotly_chart(fig_sector, use_container_width=True)

    with st.expander("Sector detail table"):
        detail = sector_stats.copy()
        detail["avg"] = detail["avg"].map(utils.fmt_pct)
        detail["median"] = detail["median"].map(utils.fmt_pct)
        detail.columns = ["Sector", "Avg Performance", "Median Performance", "Positive #", "Negative #"]
        st.dataframe(detail, use_container_width=True, hide_index=True)
else:
    st.info("No sector data available yet.")

# ------------------------------------------------------------------
# TOP / BOTTOM PERFORMERS
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">TOP &amp; BOTTOM PERFORMERS</div>', unsafe_allow_html=True)
tcol, bcol = st.columns(2)

if n_ok:
    top10 = ok_df.sort_values("change_pct", ascending=False).head(10)
    bottom10 = ok_df.sort_values("change_pct", ascending=True).head(10)

    def perf_bar(dframe, ascending_display):
        d = dframe.sort_values("change_pct", ascending=ascending_display)
        fig = go.Figure(go.Bar(
            x=d["change_pct"],
            y=d["ticker"] + " — " + d["name"].str.slice(0, 22),
            orientation="h",
            marker_color=[utils.pct_color(v) for v in d["change_pct"]],
            text=[utils.fmt_pct(v) for v in d["change_pct"]],
            textposition="outside",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=380, xaxis_title="Performance (%)", yaxis_title=None)
        return fig

    with tcol:
        st.plotly_chart(perf_bar(top10, True), use_container_width=True)
    with bcol:
        st.plotly_chart(perf_bar(bottom10, False), use_container_width=True)
else:
    st.info("No performer data available yet.")

# ------------------------------------------------------------------
# MARKET HEATMAP
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">MARKET HEATMAP</div>', unsafe_allow_html=True)

if n_ok:
    heat_df = ok_df.copy()
    heat_df["label"] = heat_df["ticker"] + "<br>" + heat_df["change_pct"].map(lambda v: utils.fmt_pct(v))
    fig_heat = px.treemap(
        heat_df,
        path=["sector", "label"],
        values=heat_df["change_pct"].abs().clip(lower=0.5),
        color="change_pct",
        color_continuous_scale=["#7F1D1D", config.COLOR_NEGATIVE, "#374151",
                                 config.COLOR_POSITIVE, "#14532D"],
        color_continuous_midpoint=0,
    )
    fig_heat.update_traces(
        textinfo="label",
        texttemplate="%{label}",
        textfont_size=15,
        marker=dict(line=dict(width=1, color=config.COLOR_BORDER)),
    )
    fig_heat.update_layout(**PLOTLY_LAYOUT, height=560, coloraxis_showscale=True)
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("No heatmap data available yet.")

# ------------------------------------------------------------------
# DISTRIBUTION + BOX PLOT
# ------------------------------------------------------------------
dcol, bxcol = st.columns(2)

with dcol:
    st.markdown('<div class="igd-section-title">DISTRIBUTION OF RETURNS</div>', unsafe_allow_html=True)
    if n_ok:
        mean_v = ok_df["change_pct"].mean()
        median_v = ok_df["change_pct"].median()
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=ok_df["change_pct"], nbinsx=18,
                                         marker_color=config.COLOR_ACCENT, opacity=0.85))
        fig_hist.add_vline(x=0, line_dash="dash", line_color=config.COLOR_TEXT_MUTED,
                            annotation_text="0%")
        fig_hist.add_vline(x=mean_v, line_color=config.COLOR_ACCENT_GOLD,
                            annotation_text=f"Mean {mean_v:.2f}%")
        fig_hist.add_vline(x=median_v, line_color=config.COLOR_POSITIVE,
                            annotation_text=f"Median {median_v:.2f}%")
        fig_hist.update_layout(**PLOTLY_LAYOUT, height=340,
                                xaxis_title="Performance (%)", yaxis_title="Count")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No distribution data available yet.")

with bxcol:
    st.markdown('<div class="igd-section-title">PERFORMANCE DISTRIBUTION BY SECTOR</div>', unsafe_allow_html=True)
    if n_ok:
        fig_box = px.box(ok_df, x="sector", y="change_pct", points="all",
                          category_orders={"sector": config.SECTORS_ORDER},
                          color="sector",
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig_box.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                               xaxis_title=None, yaxis_title="Performance (%)")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No sector distribution data available yet.")

# ------------------------------------------------------------------
# DYNAMIC INSIGHTS
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">KEY INSIGHTS</div>', unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)

if n_ok:
    best_row = ok_df.loc[ok_df["change_pct"].idxmax()]
    worst_row = ok_df.loc[ok_df["change_pct"].idxmin()]
    sector_avg = ok_df.groupby("sector")["change_pct"].mean()
    best_sector = sector_avg.idxmax()
    best_sector_val = sector_avg.max()

    i1.markdown(f"""<div class="igd-card">
        <div class="igd-kpi-label">Best Performer</div>
        <div class="igd-kpi-value" style="color:{config.COLOR_POSITIVE}">{best_row['ticker']}</div>
        <div style="color:{config.COLOR_TEXT_MUTED}; font-size:0.85rem;">{best_row['name']}</div>
        <div style="color:{config.COLOR_POSITIVE}; font-weight:700; margin-top:4px;">{utils.fmt_pct(best_row['change_pct'])}</div>
        </div>""", unsafe_allow_html=True)

    i2.markdown(f"""<div class="igd-card">
        <div class="igd-kpi-label">Worst Performer</div>
        <div class="igd-kpi-value" style="color:{config.COLOR_NEGATIVE}">{worst_row['ticker']}</div>
        <div style="color:{config.COLOR_TEXT_MUTED}; font-size:0.85rem;">{worst_row['name']}</div>
        <div style="color:{config.COLOR_NEGATIVE}; font-weight:700; margin-top:4px;">{utils.fmt_pct(worst_row['change_pct'])}</div>
        </div>""", unsafe_allow_html=True)

    i3.markdown(f"""<div class="igd-card">
        <div class="igd-kpi-label">Best Sector</div>
        <div class="igd-kpi-value" style="color:{config.COLOR_ACCENT_GOLD}">{best_sector}</div>
        <div style="color:{config.COLOR_TEXT_MUTED}; font-size:0.85rem;">Average performance</div>
        <div style="color:{utils.pct_color(best_sector_val)}; font-weight:700; margin-top:4px;">{utils.fmt_pct(best_sector_val)}</div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("No insight data available yet.")

# ------------------------------------------------------------------
# MARKET BREADTH
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">MARKET BREADTH</div>', unsafe_allow_html=True)
if n_ok:
    pct_positive = (n_pos / n_ok) * 100 if n_ok else 0
    fig_breadth = go.Figure(go.Pie(
        labels=["Positive", "Negative", "Flat"],
        values=[n_pos, n_neg, n_ok - n_pos - n_neg],
        hole=0.65,
        marker_colors=[config.COLOR_POSITIVE, config.COLOR_NEGATIVE, config.COLOR_NEUTRAL],
        textinfo="label+value",
    ))
    fig_breadth.add_annotation(text=f"{pct_positive:.0f}%<br>Positive", showarrow=False,
                                font=dict(size=20, color=config.COLOR_TEXT))
    fig_breadth.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=True)
    st.plotly_chart(fig_breadth, use_container_width=True)
else:
    st.info("No breadth data available yet.")

# ------------------------------------------------------------------
# INSTRUMENT EXPLORER
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">INSTRUMENT EXPLORER</div>', unsafe_allow_html=True)

ex1, ex2 = st.columns([1, 3])
with ex1:
    sector_filter = st.selectbox("Sector", ["All"] + config.SECTORS_ORDER, key="explorer_sector")
    pool = df if sector_filter == "All" else df[df["sector"] == sector_filter]
    search = st.text_input("Search ticker or company", key="explorer_search")
    if search:
        s = search.strip().upper()
        pool = pool[pool["ticker"].str.upper().str.contains(s) | pool["name"].str.upper().str.contains(s)]
    options = (pool["ticker"] + " — " + pool["name"]).tolist()
    chosen = st.selectbox("Select instrument", options if options else ["No match"], key="explorer_pick")

with ex2:
    if options and chosen != "No match":
        sel_ticker = chosen.split(" — ")[0]
        row = df[df["ticker"] == sel_ticker].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Reference Price", utils.fmt_usd(row["reference_price"]))
        c2.metric("Latest Price", utils.fmt_usd(row["latest_price"]))
        c3.metric("Change ($)", utils.fmt_change(row["change_abs"]))
        c4.metric("Performance", utils.fmt_pct(row["change_pct"]))

        series = data.fetch_price_series(sel_ticker)
        if series is not None and not series.empty:
            fig_line = go.Figure(go.Scatter(
                x=series.index, y=series["Close"], mode="lines",
                line=dict(color=config.COLOR_ACCENT_GOLD, width=2),
                fill="tozeroy", fillcolor="rgba(201,162,75,0.08)",
            ))
            fig_line.update_layout(**PLOTLY_LAYOUT, height=320,
                                    xaxis_title=None, yaxis_title="Price (USD)")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning(f"No historical price series available for {sel_ticker}.")
    else:
        st.info("No instrument matches the current filter/search.")

# ------------------------------------------------------------------
# MAIN DATA TABLE
# ------------------------------------------------------------------
st.markdown('<div class="igd-section-title">FULL INSTRUMENT TABLE</div>', unsafe_allow_html=True)

tf1, tf2, tf3, tf4 = st.columns([1, 1, 1, 2])
with tf1:
    tbl_sector = st.selectbox("Sector filter", ["All"] + config.SECTORS_ORDER, key="tbl_sector")
with tf2:
    tbl_direction = st.selectbox("Direction", ["All", "Positive only", "Negative only"], key="tbl_dir")
with tf3:
    tbl_sort = st.selectbox("Sort by", ["Performance % (desc)", "Performance % (asc)", "Ticker (A-Z)"], key="tbl_sort")
with tf4:
    tbl_search = st.text_input("Search table (ticker or company)", key="tbl_search")

table_df = df.copy()
if tbl_sector != "All":
    table_df = table_df[table_df["sector"] == tbl_sector]
if tbl_direction == "Positive only":
    table_df = table_df[table_df["change_pct"] > 0]
elif tbl_direction == "Negative only":
    table_df = table_df[table_df["change_pct"] < 0]
if tbl_search:
    s = tbl_search.strip().upper()
    table_df = table_df[table_df["ticker"].str.upper().str.contains(s) | table_df["name"].str.upper().str.contains(s)]

if tbl_sort == "Performance % (desc)":
    table_df = table_df.sort_values("change_pct", ascending=False, na_position="last")
elif tbl_sort == "Performance % (asc)":
    table_df = table_df.sort_values("change_pct", ascending=True, na_position="last")
else:
    table_df = table_df.sort_values("ticker", ascending=True)

display_df = table_df[[
    "sector", "name", "ticker", "reference_price", "latest_price", "change_abs", "change_pct"
]].copy()
display_df.columns = ["Sector", "Company", "Ticker", "Reference Price", "Latest Price", "Change", "Performance %"]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=460,
    column_config={
        "Reference Price": st.column_config.NumberColumn(format="$%.2f"),
        "Latest Price": st.column_config.NumberColumn(format="$%.2f"),
        "Change": st.column_config.NumberColumn(format="%.2f"),
        "Performance %": st.column_config.NumberColumn(format="%.2f%%"),
    },
)

# ------------------------------------------------------------------
# FOOTER — DATA SOURCE TRANSPARENCY
# ------------------------------------------------------------------
st.markdown(
    f"""
    <div class="igd-footer">
        Market data source: Yahoo Finance (via yfinance)<br>
        Reference price: {config.REFERENCE_DATE_LABEL} closing price<br>
        Latest price: Latest available market data<br>
        Prices in USD<br>
        Data updated: {utils.format_asof(now)}<br>
        {config.REFERENCE_DATE_NOTE}<br><br>
        {config.DISCLAIMER}
    </div>
    """,
    unsafe_allow_html=True,
)
