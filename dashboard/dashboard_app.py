"""
Streamlit Dashboard for Market Data Integrity System
Real-time visualization of monitoring and trading
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import time

sys.path.append('..')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from integrity_monitor.data_manipulator import DataManipulator
from integrated_system.protected_trading_bot import ProtectedTradingBot


# Page configuration
st.set_page_config(
    page_title="Market Data Integrity Monitor",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("🛡️ National Market Data Integrity Monitoring System")
st.markdown("---")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

symbol = st.sidebar.text_input("Stock Symbol", "AAPL")
period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo"], index=0)
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("Attack Simulation")
inject_attacks = st.sidebar.checkbox("Enable Attack Injection", value=True)
attack_probability = st.sidebar.slider("Attack Probability", 0.0, 0.5, 0.15)
attack_type = st.sidebar.selectbox("Attack Type", ["spike", "drift", "noise", "flash_crash"])

st.sidebar.markdown("---")
st.sidebar.subheader("Trading Configuration")
initial_balance = st.sidebar.number_input("Initial Balance ($)", value=10000, step=1000)
sma_window = st.sidebar.slider("SMA Window", 3, 20, 5)

# Start button
if st.sidebar.button("🚀 Start Monitoring", type="primary"):
    st.session_state.running = True
    st.session_state.data_history = []
    st.session_state.tick_count = 0

if st.sidebar.button("⏹️ Stop"):
    st.session_state.running = False

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'data_history' not in st.session_state:
    st.session_state.data_history = []
if 'tick_count' not in st.session_state:
    st.session_state.tick_count = 0

# Main dashboard
if st.session_state.running:
    # Create placeholders
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trust_metric = st.empty()
    with col2:
        anomaly_metric = st.empty()
    with col3:
        balance_metric = st.empty()
    with col4:
        trades_metric = st.empty()
    
    chart_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Initialize system
    bot = ProtectedTradingBot(
        window_size=sma_window,
        initial_balance=initial_balance,
        monitor_window=20,
        contamination=0.1,
        initial_trust=100.0,
        decay_rate=15.0,
        recovery_rate=3.0
    )
    
    manipulator = None
    if inject_attacks:
        manipulator = DataManipulator(attack_probability, attack_type)
    
    # Load data
    try:
        data = load_market_data(symbol, period, interval)
        
        # Process stream
        for tick in stream_market_data(data, symbol, 0.5):
            if not st.session_state.running:
                break
            
            st.session_state.tick_count += 1
            
            # Inject attack if enabled
            was_attacked = False
            if manipulator:
                tick, was_attacked = manipulator.manipulate(tick)
            
            # Process tick
            result = bot.process_tick(tick)
            result['was_attacked'] = was_attacked
            st.session_state.data_history.append(result)
            
            # Update metrics
            trust_metric.metric(
                "Trust Score",
                f"{result['trust_score']:.1f}/100",
                delta=None,
                delta_color="normal"
            )
            
            anomaly_metric.metric(
                "Anomalies Detected",
                bot.integrity_monitor.trust_scorer.anomaly_count,
                delta="+1" if result['is_anomaly'] else None,
                delta_color="inverse"
            )
            
            balance_metric.metric(
                "Portfolio Value",
                f"${result['portfolio_value']:.2f}",
                delta=None
            )
            
            trades_metric.metric(
                "Trades (Executed/Blocked)",
                f"{bot.executed_trades}/{bot.blocked_trades}",
                delta=None
            )
            
            # Create chart
            if len(st.session_state.data_history) > 1:
                df = pd.DataFrame(st.session_state.data_history)
                
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Price & Trust Score', 'Portfolio Value'),
                    vertical_spacing=0.15,
                    row_heights=[0.6, 0.4]
                )
                
                # Price chart
                fig.add_trace(
                    go.Scatter(
                        y=df['price'],
                        mode='lines',
                        name='Price',
                        line=dict(color='blue', width=2)
                    ),
                    row=1, col=1
                )
                
                # Mark anomalies
                anomalies = df[df['is_anomaly']]
                if not anomalies.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=anomalies.index,
                            y=anomalies['price'],
                            mode='markers',
                            name='Anomaly',
                            marker=dict(color='red', size=10, symbol='x')
                        ),
                        row=1, col=1
                    )
                
                # Trust score (secondary y-axis)
                fig.add_trace(
                    go.Scatter(
                        y=df['trust_score'],
                        mode='lines',
                        name='Trust Score',
                        line=dict(color='green', width=2, dash='dash'),
                        yaxis='y2'
                    ),
                    row=1, col=1
                )
                
                # Portfolio value
                fig.add_trace(
                    go.Scatter(
                        y=df['portfolio_value'],
                        mode='lines',
                        name='Portfolio',
                        line=dict(color='purple', width=2),
                        fill='tozeroy'
                    ),
                    row=2, col=1
                )
                
                fig.update_xaxes(title_text="Tick", row=2, col=1)
                fig.update_yaxes(title_text="Price ($)", row=1, col=1)
                fig.update_yaxes(title_text="Trust Score", row=1, col=1, secondary_y=True)
                fig.update_yaxes(title_text="Value ($)", row=2, col=1)
                
                fig.update_layout(height=600, showlegend=True)
                
                chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Status message
            status_color = "🟢" if result['trust_level'] == "HIGH" else "🟡" if result['trust_level'] == "MEDIUM" else "🟠" if result['trust_level'] == "LOW" else "🔴"
            attack_msg = " ⚠️ ATTACK DETECTED" if was_attacked else ""
            
            status_placeholder.info(
                f"{status_color} Tick #{st.session_state.tick_count} | "
                f"Price: ${result['price']:.2f} | "
                f"Trust: {result['trust_level']} | "
                f"Action: {result['final_action']}"
                f"{attack_msg}"
            )
            
            time.sleep(0.1)
        
        st.session_state.running = False
        st.success("✓ Monitoring complete!")
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.running = False

else:
    st.info("👈 Configure settings and click 'Start Monitoring' to begin")
    
    # Show instructions
    st.markdown("""
    ### 📋 Instructions
    
    1. **Configure** the stock symbol and time period in the sidebar
    2. **Enable attack simulation** to test the integrity monitoring system
    3. **Adjust trading parameters** like initial balance and SMA window
    4. **Click Start Monitoring** to begin the demonstration
    5. **Watch** as the system detects anomalies and protects trading decisions
    
    ### 🎯 Features
    
    - **Real-time anomaly detection** using statistical and ML methods
    - **Dynamic trust scoring** based on data reliability
    - **Automated trading safeguards** that block trades on suspicious data
    - **Attack simulation** to demonstrate system effectiveness
    - **Live visualization** of prices, trust scores, and portfolio value
    
    ### 🛡️ Trust Levels
    
    - 🟢 **HIGH (80-100)**: Safe to trade normally
    - 🟡 **MEDIUM (60-79)**: Trade with caution
    - 🟠 **LOW (40-59)**: Reduce exposure
    - 🔴 **CRITICAL (<40)**: Halt all trading
    """)
