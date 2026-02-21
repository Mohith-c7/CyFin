"""
Real-Time Market Data Integrity Monitoring Dashboard
Interactive Streamlit UI for system visualization
"""

import streamlit as st
import pandas as pd
import time
import sys

sys.path.append('..')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
from detection.anomaly_engine import AnomalyDetector
from trust.trust_engine import TrustScoreEngine
from protection.protection_engine import ProtectionEngine
from trading.trading_engine_protected import ProtectedTradingEngine


# Page configuration
st.set_page_config(
    page_title="Market Integrity Monitor",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Market Data Integrity Monitoring System")
st.markdown("### Real-Time Cybersecurity Protection for Financial Markets")
st.markdown("---")

# Sidebar controls
st.sidebar.header("⚙️ System Configuration")
symbol = st.sidebar.text_input("Stock Symbol", "AAPL")
delay = st.sidebar.slider("Update Speed (seconds)", 0.1, 2.0, 0.5)
max_ticks = st.sidebar.number_input("Max Ticks to Display", 10, 100, 50)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 System Status")
status_placeholder = st.sidebar.empty()

# Main dashboard layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    price_metric = st.empty()
with col2:
    trust_metric = st.empty()
with col3:
    decision_metric = st.empty()
with col4:
    portfolio_metric = st.empty()

st.markdown("---")

# Charts section
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📈 Price Movement")
    price_chart = st.empty()

with chart_col2:
    st.subheader("🛡️ Trust Score")
    trust_chart = st.empty()

st.markdown("---")

# Alerts section
st.subheader("🚨 System Alerts")
alert_box = st.empty()

st.markdown("---")

# Portfolio details
st.subheader("💰 Portfolio Status")
portfolio_details = st.empty()

st.markdown("---")

# Statistics
st.subheader("📊 System Statistics")
stats_box = st.empty()

# Start button
if st.sidebar.button("🚀 Start Monitoring", type="primary"):
    st.sidebar.success("System Running...")
    
    # Initialize history
    price_history = []
    trust_history = []
    tick_count = 0
    
    # Initialize components
    try:
        attacker = AttackEngine()
        detector = AnomalyDetector()
        trust_engine = TrustScoreEngine()
        protection = ProtectionEngine()
        trader = ProtectedTradingEngine()
        
        # Load data
        data = load_market_data(symbol=symbol, period="1d", interval="1m")
        
        # Process stream
        for tick in stream_market_data(data, symbol=symbol, delay=delay):
            tick_count += 1
            
            # Process pipeline
            tick = attacker.process_tick(tick)
            tick = detector.process_tick(tick)
            tick = trust_engine.process_tick(tick)
            
            # Protected trading
            trader.process_tick(tick, protection)
            
            # Update history
            price_history.append(tick["price"])
            trust_history.append(tick["trust_score"])
            
            # Keep only recent history
            if len(price_history) > max_ticks:
                price_history.pop(0)
                trust_history.pop(0)
            
            # Update metrics
            price_metric.metric(
                "💵 Current Price",
                f"${tick['price']:.2f}",
                delta=None
            )
            
            trust_color = "🟢" if tick['trust_level'] == "SAFE" else "🟡" if tick['trust_level'] == "CAUTION" else "🔴"
            trust_metric.metric(
                f"{trust_color} Trust Score",
                f"{tick['trust_score']:.0f}/100",
                delta=f"{tick['trust_level']}"
            )
            
            # Get final decision from trader's last action
            strategy_decision = trader.strategy.decide(tick["price"])
            final_decision = protection.process_tick(tick, strategy_decision)
            
            decision_icon = "🟢" if final_decision == "BUY" else "🔴" if final_decision == "SELL" else "🛑" if final_decision == "BLOCKED" else "⚪"
            decision_metric.metric(
                f"{decision_icon} Decision",
                final_decision
            )
            
            portfolio_value = trader.portfolio.value(tick["price"])
            portfolio_metric.metric(
                "💰 Portfolio Value",
                f"${portfolio_value:.2f}"
            )
            
            # Update charts
            price_df = pd.DataFrame({"Price": price_history})
            price_chart.line_chart(price_df)
            
            trust_df = pd.DataFrame({"Trust Score": trust_history})
            trust_chart.line_chart(trust_df)
            
            # Update alerts
            alerts = []
            if tick.get("attacked", False):
                alerts.append("🚨 **CYBER ATTACK DETECTED** - Market data manipulated!")
            if tick.get("anomaly", False):
                alerts.append(f"⚠️ **ANOMALY DETECTED** - Z-score: {tick['z_score']:.2f}")
            if final_decision == "BLOCKED":
                alerts.append("🛑 **TRADE BLOCKED** - Data unreliable, protection activated!")
            if tick['trust_level'] == "CAUTION":
                alerts.append("⚠️ **CAUTION** - Trust score reduced, monitoring closely")
            if tick['trust_level'] == "DANGEROUS":
                alerts.append("🔴 **DANGEROUS** - Critical trust level, trading halted")
            
            if alerts:
                alert_box.error("\n\n".join(alerts))
            else:
                alert_box.success("✅ System operating normally - All checks passed")
            
            # Update portfolio details
            portfolio_details.info(
                f"**Cash:** ${trader.portfolio.cash:.2f} | "
                f"**Shares:** {trader.portfolio.shares} | "
                f"**Total Value:** ${portfolio_value:.2f}"
            )
            
            # Update statistics
            protection_stats = protection.get_stats()
            anomaly_count = sum(1 for i in range(len(price_history)) if i < tick_count and tick.get("anomaly", False))
            stats_box.info(
                f"**Ticks Processed:** {tick_count} | "
                f"**Anomalies Detected:** {trust_engine.anomaly_count if hasattr(trust_engine, 'anomaly_count') else 0} | "
                f"**Trades Blocked:** {protection_stats['blocked']} | "
                f"**Trades Allowed:** {protection_stats['allowed']}"
            )
            
            # Update sidebar status
            status_placeholder.success(f"✅ Active - Tick #{tick_count}")
            
            # Limit for demo
            if tick_count >= max_ticks:
                st.sidebar.warning(f"Reached {max_ticks} ticks limit")
                break
            
            time.sleep(0.1)  # Small delay for UI updates
        
        st.sidebar.success("✅ Monitoring Complete!")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.sidebar.error("❌ System Error")

else:
    # Initial state
    st.info("👈 Click 'Start Monitoring' in the sidebar to begin the demonstration")
    
    st.markdown("""
    ### 🎯 System Overview
    
    This dashboard provides real-time monitoring of market data integrity and automated trading protection.
    
    **Features:**
    - 📊 Live price tracking
    - 🔍 Anomaly detection (Z-score analysis)
    - 🛡️ Trust score evaluation (0-100)
    - 🚫 Automated trade blocking
    - 💰 Portfolio management
    
    **How It Works:**
    1. System streams real market data
    2. Detects manipulation attacks
    3. Evaluates data trustworthiness
    4. Blocks risky trading decisions
    5. Protects your portfolio
    
    **Trust Levels:**
    - 🟢 **SAFE (80-100):** Normal trading
    - 🟡 **CAUTION (50-79):** Enhanced monitoring
    - 🔴 **DANGEROUS (0-49):** Trading blocked
    """)
