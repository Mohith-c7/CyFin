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
# Innovative Dark Theme CSS (Black & Blue)
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

    /* ── Reset & Base ─────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: #E2E8F0;
    }
    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 1440px;
    }
    .stApp {
        background: radial-gradient(circle at top right, #0F172A, #020617);
        background-attachment: fixed;
    }

    /* ── Sidebar ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h5 {
        color: #94A3B8;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1);
    }

    /* ── Header ───────────────────────────────────────── */
    .app-header {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.25rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .app-header .logo {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
    }
    .app-header .title-block h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .app-header .title-block .tagline {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 0.25rem;
        font-weight: 400;
    }

    /* ── Metric Cards (KPI) ───────────────────────────── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.25rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
        color: #F8FAFC;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 0.4rem;
        font-weight: 400;
    }

    /* ── Colors ───────────────────────────────────────── */
    .g-blue    { color: #60A5FA; }
    .g-green   { color: #34D399; }
    .g-yellow  { color: #FBBF24; }
    .g-orange  { color: #FB923C; }
    .g-red     { color: #F87171; }
    .g-teal    { color: #2DD4BF; }
    .g-gray    { color: #94A3B8; }

    /* ── Tier Chips ───────────────────────────────────── */
    .tier-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    .chip-normal   { background: rgba(16, 185, 129, 0.1); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.2); }
    .chip-elevated { background: rgba(245, 158, 11, 0.1); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.2); }
    .chip-high     { background: rgba(239, 68, 68, 0.1); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.2); }
    .chip-crisis   { background: #EF4444; color: #FFFFFF; box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }

    /* ── Section Label ────────────────────────────────── */
    .section-label {
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .section-label::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, rgba(255, 255, 255, 0.1), transparent);
    }

    /* ── Glass Cards ──────────────────────────────────── */
    .g-card {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* ── Pipeline Grid ────────────────────────────────── */
    .pipe-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
    }
    .pipe-item {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: #CBD5E1;
    }
    .pipe-item b { color: #FFFFFF; }

    /* ── Incident Panel ───────────────────────────────── */
    .incident-panel {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        position: relative;
        overflow: hidden;
    }
    .incident-panel::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: #F87171;
    }
    .incident-panel .inc-title {
        font-family: 'Outfit', sans-serif;
        color: #F87171;
        font-weight: 600;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .incident-panel .inc-detail {
        color: #94A3B8;
        font-size: 0.8rem;
        margin-top: 0.5rem;
        line-height: 1.6;
    }

    /* ── Buttons ──────────────────────────────────────── */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(30, 64, 175, 0.2);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(30, 64, 175, 0.4);
        background: linear-gradient(135deg, #60A5FA, #2563EB);
    }
    div.stButton > button:first-child:active {
        transform: translateY(0);
    }

    /* ── Custom Select/Inputs ─────────────────────────── */
    .stSelectbox, .stMultiSelect {
        border-radius: 12px;
    }

    /* ── Tabs ─────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        color: #64748B;
        padding: 0.5rem 0.25rem;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom: 2px solid #3B82F6 !important;
    }

    /* ── Welcome Cards ────────────────────────────────── */
    .welcome-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 2rem;
        height: 100%;
    }
    .welcome-card .wc-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .welcome-card .wc-body {
        font-size: 0.9rem;
        color: #94A3B8;
        line-height: 1.8;
    }
    .welcome-card .wc-body b { color: #FFFFFF; }

    /* ── Metrics Overrides ───────────────────────────── */
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 12px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# Design Helpers
# ══════════════════════════════════════════════════════════════════

# Chart palette (Vibrant, dark-themed)
G_BLUE   = "#3B82F6"
G_GREEN  = "#10B981"
G_YELLOW = "#F59E0B"
G_ORANGE = "#F97316"
G_RED    = "#EF4444"
G_TEAL   = "#14B8A6"
G_PURPLE = "#8B5CF6"
SERIES   = [G_BLUE, G_TEAL, G_ORANGE, G_RED, G_PURPLE, G_GREEN, G_YELLOW]


def g_layout(title="", height=280, ml=50, mr=20, mt=40, mb=30, yrange=None):
    """Innovative Dark Style chart layout."""
    layout = dict(
        title=dict(
            text=title,
            font=dict(size=14, color="#F8FAFC", family="Outfit, Inter, sans-serif"),
            x=0.01, y=0.98
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=ml, r=mr, t=mt, b=mb),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(color="#64748B", size=10),
            title_font=dict(color="#94A3B8", size=11),
            zeroline=False, showline=True, linecolor="rgba(255,255,255,0.1)", linewidth=1,
            mirror=False
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(color="#64748B", size=10),
            title_font=dict(color="#94A3B8", size=11),
            zeroline=False, showline=False
        ),
        legend=dict(
            font=dict(color="#94A3B8", size=11, family="Inter, sans-serif"),
            bgcolor="rgba(15,23,42,0.8)", borderwidth=0
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#1E293B", font_color="#F8FAFC",
            bordercolor="rgba(255,255,255,0.1)", font_size=12,
            font_family="Inter, sans-serif"
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
    return {"NORMAL":"󰄬","ELEVATED_RISK":"󰀪","HIGH_VOLATILITY":"󱈸","SYSTEMIC_CRISIS":"󰀦"}.get(tier, "●")

def frag_color(f):
    return {"ROBUST": G_GREEN, "MODERATE_SENSITIVITY": G_YELLOW,
            "FRAGILE": G_ORANGE, "CRISIS_PRONE": G_RED}.get(f, "#64748B")


def make_gauge(value):
    """Innovative Dark Style gauge."""
    color = msi_color(value)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(
            font=dict(size=48, color=color, family="Outfit, Inter"),
            valueformat=".1f"
        ),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=0, visible=False),
            bar=dict(color=color, thickness=0.4),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=0,
            pointer=dict(color=color, length=0.6),
            steps=[
                dict(range=[0, 40], color="rgba(248,113,113,0.1)"),
                dict(range=[40, 60], color="rgba(251,191,36,0.1)"),
                dict(range=[60, 100], color="rgba(52,211,153,0.1)"),
            ],
            threshold=dict(
                line=dict(color=color, width=2),
                thickness=0.8, value=value
            )
        )
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=200, margin=dict(l=30, r=30, t=10, b=10),
        annotations=[dict(
            text="Market Stability Index",
            x=0.5, y=-0.1, showarrow=False,
            font=dict(size=11, color="#94A3B8", family="Inter"),
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
