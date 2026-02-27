"""
CyFin — Systemic Risk Intelligence Platform
================================================
Light Theme · Google Material Design Principles
Clean, accessible, professional.

Run:
    streamlit run cyfin_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestration.master_orchestration_engine import (
    MasterOrchestrationEngine, CycleResult
)
from resilience.stress_simulation_engine import StressSimulationEngine

# ══════════════════════════════════════════════════════════════════
# Page Config
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CyFin — Systemic Risk Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════
# Google-Inspired Light Theme CSS
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

    /* ── Reset & Base ─────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #202124;
    }
    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 1380px;
    }
    .stApp {
        background-color: #f8f9fa;
    }

    /* ── Sidebar ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h5 {
        color: #3c4043;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #e8eaed;
    }

    /* ── Header ───────────────────────────────────────── */
    .app-header {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 1px 3px rgba(60,64,67,0.08), 0 1px 2px rgba(60,64,67,0.04);
    }
    .app-header .logo {
        width: 40px;
        height: 40px;
        background: #1a73e8;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .app-header .title-block h1 {
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1.35rem;
        font-weight: 500;
        color: #202124;
        margin: 0;
        letter-spacing: -0.2px;
    }
    .app-header .title-block .tagline {
        font-size: 0.78rem;
        color: #5f6368;
        margin-top: 0.15rem;
        font-weight: 400;
    }

    /* ── Metric Cards (KPI) ───────────────────────────── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        box-shadow: 0 1px 3px rgba(60,64,67,0.08), 0 1px 2px rgba(60,64,67,0.04);
        transition: box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 2px 6px rgba(60,64,67,0.15), 0 1px 3px rgba(60,64,67,0.08);
    }
    .kpi-label {
        font-size: 0.68rem;
        font-weight: 500;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1.75rem;
        font-weight: 500;
        line-height: 1.15;
        letter-spacing: -0.5px;
    }
    .kpi-sub {
        font-size: 0.7rem;
        color: #80868b;
        margin-top: 0.2rem;
        font-weight: 400;
    }

    /* ── Color Tokens (Google-style) ──────────────────── */
    .g-blue    { color: #1a73e8; }
    .g-green   { color: #1e8e3e; }
    .g-yellow  { color: #f9ab00; }
    .g-orange  { color: #e8710a; }
    .g-red     { color: #d93025; }
    .g-teal    { color: #007b83; }
    .g-gray    { color: #5f6368; }

    /* ── Tier Chips ───────────────────────────────────── */
    .tier-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.75rem;
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .chip-normal   { background: #e6f4ea; color: #1e8e3e; }
    .chip-elevated { background: #fef7e0; color: #e37400; }
    .chip-high     { background: #fce8e6; color: #c5221f; }
    .chip-crisis   { background: #d93025; color: #ffffff; }

    /* ── Section Label ────────────────────────────────── */
    .section-label {
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 0.72rem;
        font-weight: 500;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1.25rem 0 0.6rem 0.1rem;
    }

    /* ── Cards ────────────────────────────────────────── */
    .g-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 1px 3px rgba(60,64,67,0.08), 0 1px 2px rgba(60,64,67,0.04);
    }

    /* ── Pipeline Grid ────────────────────────────────── */
    .pipe-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.4rem;
    }
    .pipe-item {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-left: 3px solid #1e8e3e;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        font-size: 0.75rem;
        color: #3c4043;
    }
    .pipe-item b { color: #202124; }

    /* ── Incident Panel ───────────────────────────────── */
    .incident-panel {
        background: #fce8e6;
        border: 1px solid #f5c6c2;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    .incident-panel .inc-title {
        font-family: 'Google Sans', sans-serif;
        color: #c5221f;
        font-weight: 500;
        font-size: 0.85rem;
    }
    .incident-panel .inc-detail {
        color: #5f6368;
        font-size: 0.75rem;
        margin-top: 0.35rem;
        line-height: 1.7;
    }

    /* ── Stress Row ───────────────────────────────────── */
    .stress-row {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.3rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.15s;
    }
    .stress-row:hover { background: #f8f9fa; }
    .stress-row .sr-name {
        font-family: 'Google Sans', sans-serif;
        color: #202124;
        font-weight: 500;
        font-size: 0.82rem;
    }
    .stress-row .sr-detail { color: #80868b; font-size: 0.72rem; }

    /* ── Welcome Cards ────────────────────────────────── */
    .welcome-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(60,64,67,0.08), 0 1px 2px rgba(60,64,67,0.04);
        height: 100%;
    }
    .welcome-card .wc-title {
        font-family: 'Google Sans', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        color: #1a73e8;
        margin-bottom: 0.75rem;
    }
    .welcome-card .wc-body {
        font-size: 0.8rem;
        color: #5f6368;
        line-height: 2;
    }
    .welcome-card .wc-body b { color: #1a73e8; }
    .welcome-card .wc-body .teal { color: #007b83; }
    .welcome-card .wc-body .purple { color: #7c4dff; }
    .welcome-card .wc-body .red { color: #d93025; }

    /* ── Tabs ─────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.15rem;
        border-bottom: 2px solid #e8eaed;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Google Sans', sans-serif;
        font-weight: 500;
        font-size: 0.82rem;
        color: #5f6368;
        padding: 0.55rem 1rem;
        border-radius: 0;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1a73e8;
    }

    /* ── Misc ─────────────────────────────────────────── */
    div[data-testid="stHorizontalBlock"] { gap: 0.75rem; }

    /* ── Clean Up Streamlit Defaults ──────────────────── */
    .stMetric label { color: #5f6368 !important; font-weight: 500 !important; }
    .stMetric [data-testid="stMetricValue"] {
        font-family: 'Google Sans', sans-serif !important;
        color: #202124 !important;
    }
    .stProgress > div > div > div > div { background: #1a73e8 !important; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# Design Helpers
# ══════════════════════════════════════════════════════════════════

# Chart palette (Google-inspired, light backgrounds)
G_BLUE   = "#1a73e8"
G_GREEN  = "#1e8e3e"
G_YELLOW = "#f9ab00"
G_ORANGE = "#e8710a"
G_RED    = "#d93025"
G_TEAL   = "#007b83"
G_PURPLE = "#7c4dff"
SERIES   = [G_BLUE, G_TEAL, G_ORANGE, G_RED, G_PURPLE, G_GREEN, G_YELLOW]


def g_layout(title="", height=280, ml=50, mr=20, mt=36, mb=30, yrange=None):
    """Google-style chart layout with white background."""
    layout = dict(
        title=dict(
            text=title,
            font=dict(size=13, color="#3c4043", family="Google Sans, Roboto, sans-serif"),
            x=0.01, y=0.97
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=height,
        margin=dict(l=ml, r=mr, t=mt, b=mb),
        xaxis=dict(
            gridcolor="#f1f3f4", tickfont=dict(color="#80868b", size=10),
            title_font=dict(color="#5f6368", size=11),
            zeroline=False, showline=True, linecolor="#e8eaed", linewidth=1,
            mirror=False
        ),
        yaxis=dict(
            gridcolor="#f1f3f4", tickfont=dict(color="#80868b", size=10),
            title_font=dict(color="#5f6368", size=11),
            zeroline=False, showline=False
        ),
        legend=dict(
            font=dict(color="#5f6368", size=11, family="Roboto, sans-serif"),
            bgcolor="rgba(255,255,255,0.9)", borderwidth=0
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#ffffff", font_color="#202124",
            bordercolor="#e8eaed", font_size=12,
            font_family="Roboto, sans-serif"
        )
    )
    if yrange:
        layout["yaxis"]["range"] = yrange
    return layout


def msi_color(v):
    if v >= 80: return G_GREEN
    if v >= 60: return G_YELLOW
    if v >= 40: return G_ORANGE
    return G_RED

def msi_class(v):
    if v >= 80: return "g-green"
    if v >= 60: return "g-yellow"
    if v >= 40: return "g-orange"
    return "g-red"

def tier_chip_class(tier):
    m = {"NORMAL": "chip-normal", "ELEVATED_RISK": "chip-elevated",
         "HIGH_VOLATILITY": "chip-high", "SYSTEMIC_CRISIS": "chip-crisis"}
    return m.get(tier, "chip-normal")

def tier_icon(tier):
    return {"NORMAL":"●","ELEVATED_RISK":"●","HIGH_VOLATILITY":"●","SYSTEMIC_CRISIS":"●"}.get(tier, "●")

def frag_color(f):
    return {"ROBUST": G_GREEN, "MODERATE_SENSITIVITY": G_YELLOW,
            "FRAGILE": G_ORANGE, "CRISIS_PRONE": G_RED}.get(f, "#80868b")


def make_gauge(value):
    """Google-style clean gauge."""
    color = msi_color(value)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(
            font=dict(size=52, color=color, family="Google Sans, Roboto"),
            valueformat=".1f"
        ),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=0, visible=False),
            bar=dict(color=color, thickness=0.3),
            bgcolor="#f1f3f4",
            borderwidth=0,
            steps=[
                dict(range=[0, 40], color="#fce8e6"),
                dict(range=[40, 60], color="#fef7e0"),
                dict(range=[60, 80], color="#e6f4ea"),
                dict(range=[80, 100], color="#e6f4ea"),
            ],
            threshold=dict(
                line=dict(color=color, width=2),
                thickness=0.85, value=value
            )
        )
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=220, margin=dict(l=30, r=30, t=15, b=10),
        annotations=[dict(
            text="Market Stability Index",
            x=0.5, y=-0.05, showarrow=False,
            font=dict(size=10, color="#5f6368", family="Google Sans"),
            xref="paper", yref="paper"
        )]
    )
    return fig


# ══════════════════════════════════════════════════════════════════
# Header
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
    <div class="logo">🏛️</div>
    <div class="title-block">
        <h1>CyFin</h1>
        <div class="tagline">Systemic Risk Intelligence Platform &nbsp;·&nbsp; Real-Time Monitoring &nbsp;·&nbsp; Feed Integrity &nbsp;·&nbsp; Governance</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # ── Demo Presets ───────────────────────────────────
    st.markdown("##### 🎯 Demo Presets")
    preset = st.selectbox(
        "Scenario",
        ["Custom", "✅ Clean Market", "⚠️ Mild Stress", "🔥 Feed Corruption", "🚨 Full Crisis"],
        index=0,
        help="Pre-configured scenarios for jury demonstration"
    )

    # Apply preset values
    # Each preset specifies:
    #   dev      = secondary feed deviation (basis points)
    #   cor      = secondary feed corruption probability
    #   ticks    = max ticks per symbol
    #   delay    = inter-tick sleep
    #   period   = yfinance period (controls data volatility level)
    #   interval = yfinance interval
    #   vol_f    = volatility amplifier — multiplies price *returns* to simulate
    #              a stressed market where anomalies actually occur
    #              1.0 = real data unchanged; 3.0 = 3× amplified price swings
    PRESETS = {
        "✅ Clean Market":    {"dev": 0.5,  "cor": 0.00, "ticks": 60, "delay": 0.0, "period": "1d", "interval": "1m",  "vol_f": 1.0},
        "⚠️ Mild Stress":    {"dev": 3.0,  "cor": 0.05, "ticks": 60, "delay": 0.0, "period": "5d", "interval": "5m",  "vol_f": 2.0},
        "🔥 Feed Corruption": {"dev": 8.0,  "cor": 0.20, "ticks": 60, "delay": 0.0, "period": "5d", "interval": "5m",  "vol_f": 3.0},
        "🚨 Full Crisis":     {"dev": 10.0, "cor": 0.30, "ticks": 60, "delay": 0.0, "period": "5d", "interval": "15m", "vol_f": 5.0},
    }

    st.markdown("---")

    symbols = st.multiselect(
        "Assets",
        ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NVDA"],
        default=["AAPL", "MSFT", "GOOGL"]
    )

    st.markdown("---")
    st.markdown("##### Data Source")
    period = st.selectbox("Period", ["1d", "5d", "1mo"], index=0)
    interval = st.selectbox("Interval", ["1m", "5m", "15m"], index=0)

    if preset in PRESETS:
        p = PRESETS[preset]
        max_ticks = p["ticks"]
        delay = p["delay"]
        feed_dev = p["dev"]
        feed_cor = p["cor"]
        period = p["period"]
        interval = p["interval"]
        vol_factor = p["vol_f"]
        st.info(f"**{preset}**\nDev: {feed_dev} bps · Corruption: {feed_cor:.0%} · Vol×{vol_factor:.0f}")
    else:
        c1, c2 = st.columns(2)
        max_ticks = c1.number_input("Ticks", 10, 200, 60, step=10)
        delay = c2.number_input("Delay (s)", 0.0, 2.0, 0.0, step=0.05)
        vol_factor = 1.0
        st.markdown("---")
        st.markdown("##### Feed Simulation")
        feed_dev = st.slider("Deviation (bps)", 0.0, 10.0, 1.0, step=0.5)
        feed_cor = st.slider("Corruption Prob", 0.0, 0.3, 0.0, step=0.01)

    st.markdown("---")
    run_btn = st.button("▶  Start Monitoring", type="primary", use_container_width=True)
    stress_btn = st.button("🔬  Stress Testing", use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# Session State
# ══════════════════════════════════════════════════════════════════

for k, v in {"engine": None, "results": [], "stress_results": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════
# Tabs
# ══════════════════════════════════════════════════════════════════

tab_live, tab_stress, tab_explain, tab_incidents = st.tabs([
    "📊  Monitor", "🔬  Stress Lab", "🔍  Explainability", "📋  Incidents"
])


# ══════════════════════════════════════════════════════════════════
# TAB 1 — LIVE MONITOR
# ══════════════════════════════════════════════════════════════════

with tab_live:
    if run_btn and symbols:
        with st.spinner("Initializing CyFin pipeline…"):
            engine = MasterOrchestrationEngine(
                symbols=symbols,
                feed_deviation_bps=feed_dev,
                feed_corruption_prob=feed_cor,
                contagion_window=20
            )
            st.session_state.engine = engine
            st.session_state.results = []

        # Placeholders
        kpi_ph = st.empty()

        st.markdown('<div class="section-label">System Overview</div>', unsafe_allow_html=True)
        ov = st.columns([5, 2])
        msi_line_ph = ov[0].empty()
        gauge_ph = ov[1].empty()

        st.markdown('<div class="section-label">Market Intelligence</div>', unsafe_allow_html=True)
        mi = st.columns(2)
        price_ph = mi[0].empty()
        comp_ph = mi[1].empty()

        st.markdown('<div class="section-label">Pipeline Status</div>', unsafe_allow_html=True)
        ps = st.columns([3, 2])
        pipe_ph = ps[0].empty()
        alert_ph = ps[1].empty()

        bar = st.progress(0, text="Starting…")

        # Data
        from data_stream.data_loader import load_market_data

        msi_h, trust_h, crs_h = [], [], []
        px_h = {s: [] for s in symbols}
        all_res = []

        # ── Load all data first, then interleave ──────────────────────
        # CRITICAL: process ticks in synchronized round-robin order so
        # ContagionEngine receives time-aligned series across all assets.
        #
        # vol_factor amplifies price *returns* to simulate market stress.
        # The anomaly detector uses Z-score on price changes, so amplifying
        # returns is the mechanism that causes anomalies to fire in crisis
        # scenarios, degrading trust and lowering MSI correctly.
        sym_data = {}
        for sym in symbols:
            try:
                raw = load_market_data(sym, period, interval)
                raw_prices = raw['Close'].tolist()[:max_ticks]

                if vol_factor != 1.0 and len(raw_prices) > 1:
                    # Amplify returns, keep first price as anchor
                    amplified = [raw_prices[0]]
                    for i in range(1, len(raw_prices)):
                        ret = (raw_prices[i] - raw_prices[i-1]) / raw_prices[i-1]
                        amplified_ret = ret * vol_factor
                        amplified.append(amplified[-1] * (1 + amplified_ret))
                    sym_data[sym] = amplified
                else:
                    sym_data[sym] = raw_prices
            except Exception as e:
                st.error(f"Error loading {sym}: {e}")

        if not sym_data:
            st.error("No data loaded. Check your internet connection.")
        else:
            # Determine common tick count
            n_ticks = min(len(v) for v in sym_data.values())
            total = n_ticks * len(sym_data)
            cur = 0

            for t in range(n_ticks):
                for sym in symbols:
                    if sym not in sym_data or t >= len(sym_data[sym]):
                        continue

                    price = sym_data[sym][t]
                    cur += 1
                    pct = min(cur / total, 1.0)

                    r = engine.process_tick(sym, price)
                    all_res.append(r)
                    msi_h.append(r.msi_score)
                    trust_h.append(r.trust_score)
                    crs_h.append(r.contagion_risk_score)
                    px_h[sym].append(r.primary_price)

                    # ── KPI Cards ──
                    if cur % 4 == 0 or cur >= total:
                        avg_t = engine._compute_average_trust()
                        ar = engine._compute_anomaly_rate()
                        tier = r.risk_tier
                        chip = tier_chip_class(tier)
                        kpi_ph.markdown(f"""
                        <div class="kpi-grid">
                            <div class="kpi-card">
                                <div class="kpi-label">MSI</div>
                                <div class="kpi-value {msi_class(r.msi_score)}">{r.msi_score:.1f}</div>
                                <div class="kpi-sub">Stability Index</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-label">Risk Tier</div>
                                <div class="kpi-value" style="font-size:0.95rem;padding-top:0.15rem;">
                                    <span class="tier-chip {chip}">{tier_icon(tier)} {tier.replace('_',' ')}</span>
                                </div>
                                <div class="kpi-sub">{r.recommended_action.replace('_',' ').title()}</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-label">Avg Trust</div>
                                <div class="kpi-value {'g-green' if avg_t >= 80 else 'g-yellow' if avg_t >= 50 else 'g-red'}">{avg_t:.0f}</div>
                                <div class="kpi-sub">Asset Reliability</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-label">Contagion</div>
                                <div class="kpi-value {'g-green' if r.contagion_risk_score < 30 else 'g-orange' if r.contagion_risk_score < 60 else 'g-red'}">{r.contagion_risk_score:.1f}</div>
                                <div class="kpi-sub">Cross-Asset Risk</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-label">Feed Health</div>
                                <div class="kpi-value {'g-green' if r.feed_mismatch_rate < 0.02 else 'g-orange' if r.feed_mismatch_rate < 0.05 else 'g-red'}">{r.feed_mismatch_rate*100:.2f}%</div>
                                <div class="kpi-sub">Cross-Feed Deviation</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-label">Anomalies</div>
                                <div class="kpi-value g-teal">{engine._total_anomalies}</div>
                                <div class="kpi-sub">Rate: {ar*100:.1f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # ── Charts ──
                    if cur % 6 == 0 or cur >= total - 1:
                        # MSI Timeline
                        fig_m = go.Figure()
                        fig_m.add_trace(go.Scatter(
                            y=msi_h, mode='lines',
                            line=dict(color=G_BLUE, width=2),
                            fill='tozeroy', fillcolor='rgba(26,115,232,0.06)',
                            hovertemplate='Tick %{x}<br>MSI: %{y:.1f}<extra></extra>'
                        ))
                        for yv, c, lbl in [(80, G_GREEN, "Stable"), (60, G_YELLOW, "Elevated"), (40, G_ORANGE, "High Risk")]:
                            fig_m.add_hline(
                                y=yv, line_dash="dot", line_width=1,
                                line_color=c,
                                annotation_text=lbl,
                                annotation_font_size=9,
                                annotation_font_color=c,
                                annotation_position="right"
                            )
                        fig_m.update_layout(**g_layout("MSI Timeline", height=280, yrange=[0, 100]))
                        fig_m.update_layout(xaxis_title="Tick")
                        msi_line_ph.plotly_chart(fig_m, use_container_width=True, key=f"msi_{cur}")

                        # Gauge
                        gauge_ph.plotly_chart(make_gauge(r.msi_score), use_container_width=True, key=f"g_{cur}")

                        # Price
                        fig_p = go.Figure()
                        for i, s in enumerate(symbols):
                            if px_h[s]:
                                fig_p.add_trace(go.Scatter(
                                    y=px_h[s], mode='lines', name=s,
                                    line=dict(color=SERIES[i % len(SERIES)], width=1.8),
                                    hovertemplate='%{fullData.name}<br>$%{y:.2f}<extra></extra>'
                                ))
                        fig_p.update_layout(**g_layout("Price Movements", height=268))
                        fig_p.update_layout(showlegend=True, legend=dict(
                            orientation="h", yanchor="top", y=1.12, xanchor="right", x=1
                        ))
                        price_ph.plotly_chart(fig_p, use_container_width=True, key=f"px_{cur}")

                        # Attribution bar
                        if r.msi_explanation and 'component_contributions' in r.msi_explanation:
                            comps = r.msi_explanation['component_contributions']
                            names = [n.replace('_',' ').replace('component','').replace('penalty','').strip().title() for n in comps.keys()]
                            vals = list(comps.values())
                            colors = [G_GREEN if v > 0 else G_RED for v in vals]

                            fig_c = go.Figure(go.Bar(
                                x=vals, y=names, orientation='h',
                                marker_color=colors, marker_line_width=0,
                                text=[f"{v:+.1f}" for v in vals],
                                textposition='outside',
                                textfont=dict(color="#5f6368", size=10),
                                hovertemplate='%{y}: %{x:+.2f}<extra></extra>'
                            ))
                            fig_c.update_layout(**g_layout("MSI Component Attribution", height=268, ml=120, mr=55))
                            fig_c.update_layout(
                                xaxis=dict(zeroline=True, zerolinecolor="#dadce0", zerolinewidth=1),
                                yaxis=dict(tickfont=dict(color="#3c4043", size=11))
                            )
                            comp_ph.plotly_chart(fig_c, use_container_width=True, key=f"cp_{cur}")

                    # ── Pipeline Status ──
                    if cur % 10 == 0 or cur >= total - 1:
                        dom = r.dominant_risk_factor.replace('_',' ').title()
                        pipe_ph.markdown(f"""
                        <div class="pipe-grid">
                            <div class="pipe-item">✓ <b>Feed Integrity</b> — {r.feed_mismatch_rate*100:.3f}%</div>
                            <div class="pipe-item">✓ <b>Anomaly Detection</b> — Z: {r.z_score:.2f} {'⚠' if r.is_anomaly else '✓'}</div>
                            <div class="pipe-item">✓ <b>Trust Scoring</b> — {r.trust_score:.0f}/100</div>
                            <div class="pipe-item">✓ <b>Contagion Engine</b> — CRS: {r.contagion_risk_score:.1f}</div>
                            <div class="pipe-item">✓ <b>MSI Computed</b> — {r.msi_score:.1f}</div>
                            <div class="pipe-item">✓ <b>Systemic Action</b> — {r.risk_tier.replace('_',' ')}</div>
                            <div class="pipe-item">✓ <b>Explainability</b> — {dom}</div>
                            <div class="pipe-item">✓ <b>Cycle</b> — {r.processing_time_ms:.1f}ms</div>
                        </div>
                        """, unsafe_allow_html=True)

                        incs = engine.get_incidents()
                        if incs:
                            lat = incs[-1]
                            alert_ph.markdown(f"""
                            <div class="incident-panel">
                                <div class="inc-title">⚠ Active Incident #{len(incs)}</div>
                                <div class="inc-detail">
                                    Tier: <b>{lat.get('risk_tier','—')}</b><br>
                                    Severity: <b>{lat.get('severity_score',0):.1f}</b><br>
                                    MSI at trigger: <b>{lat.get('msi',0):.1f}</b><br>
                                    Action: {lat.get('recommended_action','—').replace('_',' ').title()}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            alert_ph.markdown("""
                            <div class="g-card" style="text-align:center;padding:1.3rem;">
                                <div style="color:#1e8e3e;font-weight:500;font-size:0.85rem;">✓ No Active Incidents</div>
                                <div style="color:#80868b;font-size:0.75rem;margin-top:0.3rem;">System nominal</div>
                            </div>
                            """, unsafe_allow_html=True)

                        bar.progress(pct, text=f"Tick {t+1}/{n_ticks} · {sym}")
                        time.sleep(delay)

        st.session_state.results = all_res
        bar.progress(1.0, text="✓  Pipeline complete")

        # Summary
        st.markdown('<div class="section-label">Run Summary</div>', unsafe_allow_html=True)
        state = engine.get_system_state()
        sc = st.columns(5)
        sc[0].metric("Total Ticks", state['tick_count'])
        sc[1].metric("Anomalies", state['total_anomalies'])
        sc[2].metric("Incidents", state['total_incidents'])
        sc[3].metric("Final MSI", f"{msi_h[-1]:.1f}" if msi_h else "—")
        sc[4].metric("Tier", state['current_risk_tier'].replace('_',' '))

        # Rankings
        st.markdown('<div class="section-label">Asset Systemic Impact Ranking</div>', unsafe_allow_html=True)
        rankings = engine.get_asset_rankings()
        if rankings:
            rank_df = pd.DataFrame(rankings)
            st.dataframe(
                rank_df[['rank','symbol','trust_score','risk_contribution','risk_level','explanation']],
                use_container_width=True, hide_index=True
            )

    elif not run_btn:
        st.markdown("")
        wc = st.columns([1, 2])
        with wc[0]:
            st.markdown("""
            <div class="welcome-card">
                <div class="wc-title">8-Module Pipeline</div>
                <div class="wc-body">
                    ① Feed Integrity Engine<br>
                    ② Anomaly Detection<br>
                    ③ Trust Scoring<br>
                    ④ Contagion Engine<br>
                    ⑤ Market Stability Index<br>
                    ⑥ Systemic Action Engine<br>
                    ⑦ Incident Intelligence<br>
                    ⑧ Explainability Engine
                </div>
            </div>
            """, unsafe_allow_html=True)
        with wc[1]:
            st.markdown("""
            <div class="welcome-card">
                <div class="wc-title">Getting Started</div>
                <div class="wc-body">
                    1. Select assets to monitor in the sidebar<br>
                    2. Configure data period and tick count<br>
                    3. Optionally adjust feed corruption settings<br>
                    4. Click <b>Start Monitoring</b> to begin<br>
                    5. Watch all 8 modules process in real time<br>
                    6. Use <b class="teal">Stress Lab</b> to run crisis scenarios<br>
                    7. Review <b class="purple">Explainability</b> for risk attribution<br>
                    8. Check <b class="red">Incidents</b> for the governance log
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — STRESS LAB
# ══════════════════════════════════════════════════════════════════

with tab_stress:
    st.markdown('<div class="section-label">Stress Simulation Laboratory</div>', unsafe_allow_html=True)

    if stress_btn or st.session_state.stress_results:
        if stress_btn:
            if st.session_state.engine:
                state = st.session_state.engine.get_system_state()
                ts = state.get('asset_trust_scores', {"AAPL": 85, "MSFT": 80, "GOOGL": 90})
            else:
                ts = {"AAPL": 85.0, "MSFT": 80.0, "GOOGL": 90.0}

            from systemic.market_stability_index import MarketStabilityIndex
            mc = MarketStabilityIndex()
            avg = sum(ts.values()) / len(ts)
            msi_r = mc.compute_msi(avg, 0.02, 5, 0.01, 15.0)

            se = StressSimulationEngine(
                baseline_msi=msi_r['msi_score'], baseline_trust_scores=ts,
                baseline_contagion_risk_score=15.0, baseline_feed_mismatch_rate=0.01,
                baseline_market_anomaly_rate=0.02, baseline_total_anomalies=5
            )
            with st.spinner("Running stress battery…"):
                st.session_state.stress_results = se.run_standard_battery()

        battery = st.session_state.stress_results
        if battery:
            scenarios = [r['scenario_type'].replace('_',' ') for r in battery]
            deltas = [r['delta_msi'] for r in battery]
            frags = [r['system_fragility_level'] for r in battery]
            colors = [frag_color(f) for f in frags]

            fig_s = go.Figure(go.Bar(
                x=scenarios, y=deltas, marker_color=colors,
                text=[f"Δ{d:.1f}" for d in deltas],
                textposition='outside', textfont=dict(color="#5f6368", size=10),
                hovertemplate='%{x}<br>MSI Drop: %{y:.1f}<extra></extra>'
            ))
            fig_s.update_layout(**g_layout("MSI Impact by Scenario", height=340, mb=100))
            fig_s.update_layout(xaxis=dict(tickangle=-25, tickfont=dict(color="#3c4043", size=9)))
            st.plotly_chart(fig_s, use_container_width=True)

            st.markdown('<div class="section-label">Scenario Details</div>', unsafe_allow_html=True)
            for rr in battery:
                fc = frag_color(rr['system_fragility_level'])
                tc_lbl = "⚠ CHANGED" if rr['tier_changed'] else "✓ Same"
                st.markdown(f"""
                <div class="stress-row">
                    <div>
                        <div class="sr-name">{rr['scenario_type'].replace('_',' ')}</div>
                        <div class="sr-detail">MSI {rr['baseline_msi']:.1f} → {rr['post_shock_msi']:.1f} · Δ {rr['delta_msi']:.1f} · {tc_lbl}</div>
                    </div>
                    <div style="color:{fc};font-weight:500;font-size:0.78rem;">{rr['system_fragility_level'].replace('_',' ')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Click **Stress Testing** in the sidebar to run the standard crisis simulation battery.")


# ══════════════════════════════════════════════════════════════════
# TAB 3 — EXPLAINABILITY
# ══════════════════════════════════════════════════════════════════

with tab_explain:
    st.markdown('<div class="section-label">Risk Attribution & Explainability</div>', unsafe_allow_html=True)

    results = st.session_state.results
    if results:
        latest = results[-1]
        exp = latest.msi_explanation

        if exp and 'component_contributions' in exp:
            ec = st.columns(3)
            ec[0].metric("Final MSI", f"{exp.get('msi_final_score', 0):.2f}")
            ec[1].metric("Dominant Factor", exp.get('dominant_risk_factor', '—').replace('_',' ').title())
            ec[2].metric("Formula", "MSI V2 Composite")

            st.markdown("---")

            comps = exp['component_contributions']
            pcts = exp.get('component_percentages', {})
            df = pd.DataFrame([
                {"Component": k.replace('_',' ').title(),
                 "Contribution": f"{v:+.2f}",
                 "Share": f"{pcts.get(k, 0):.1f}%"}
                for k, v in comps.items()
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

            if st.session_state.engine:
                from governance.explainability_engine import ExplainabilityEngine
                ee = ExplainabilityEngine()
                sev = ee.explain_severity(
                    msi=latest.msi_score, contagion_risk_score=latest.contagion_risk_score,
                    feed_mismatch_rate=latest.feed_mismatch_rate, average_trust_score=latest.trust_score
                )
                narrative = ee.generate_narrative(exp, sev)
                st.markdown("---")
                st.markdown('<div class="section-label">Narrative Summary</div>', unsafe_allow_html=True)
                st.code(narrative, language=None)
    else:
        st.info("Run the monitor first to see risk attribution analysis.")


# ══════════════════════════════════════════════════════════════════
# TAB 4 — INCIDENTS
# ══════════════════════════════════════════════════════════════════

with tab_incidents:
    st.markdown('<div class="section-label">Governance & Incident Log</div>', unsafe_allow_html=True)

    if st.session_state.engine:
        incidents = st.session_state.engine.get_incidents()
        if incidents:
            st.metric("Total Incidents", len(incidents))
            for i, inc in enumerate(reversed(incidents[-20:])):
                with st.expander(
                    f"#{len(incidents)-i}  ·  {inc.get('risk_tier','—').replace('_',' ')}  ·  Severity {inc.get('severity_score',0):.1f}"
                ):
                    ic = st.columns(3)
                    ic[0].metric("MSI", f"{inc.get('msi',0):.1f}")
                    ic[1].metric("Severity", f"{inc.get('severity_score',0):.1f}")
                    ic[2].metric("Tier", inc.get('risk_tier','—').replace('_',' '))
                    st.json({
                        "incident_id": inc.get('incident_id',''),
                        "timestamp": inc.get('timestamp',''),
                        "risk_tier": inc.get('risk_tier',''),
                        "recommended_action": inc.get('recommended_action',''),
                        "severity_score": inc.get('severity_score', 0),
                        "msi": inc.get('msi', 0)
                    })
        else:
            st.success("✓ No incidents recorded. System operating within normal parameters.")
    else:
        st.info("Run the monitor first to see incident logs.")
