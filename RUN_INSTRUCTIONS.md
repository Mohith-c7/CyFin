# Quick Start Guide

## Setup (First Time Only)

### 1. Create Virtual Environment
```cmd
python -m venv venv
```

### 2. Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```

## Running the System

### Option 1: Complete System Demo (Recommended)
```cmd
python main_system_demo.py
```
This runs the full end-to-end demonstration with:
- Market data streaming
- Attack injection
- Anomaly detection
- Trust scoring
- Protected trading
- Performance summary

### Option 2: Interactive Dashboard
```cmd
streamlit run dashboard/dashboard_app.py
```
Opens a web browser with interactive dashboard featuring:
- Real-time charts
- Live metrics
- Configurable parameters
- Visual alerts

### Option 3: Test Individual Components

**Test Market Stream:**
```cmd
python main_stream_test.py
```

**Test Trading Bot:**
```cmd
python main_trading_test.py
```

**Test Integrity Monitor:**
```cmd
python main_integrity_test.py
```

**Test with Clean Data (No Attacks):**
```cmd
python main_integrity_test.py --clean
```

## What to Expect

### Console Output
You'll see real-time updates showing:
- Current price and SMA
- Anomaly detection status
- Trust score (0-100)
- Trading decisions (BUY/SELL/BLOCKED)
- Portfolio value
- Attack injection markers

### Dashboard
Interactive web interface with:
- Live price chart
- Trust score graph
- Portfolio value tracking
- Real-time metrics
- Configuration controls

## Stopping the System

Press `Ctrl+C` at any time to stop and see the final summary.

## Tips

1. **First run**: Start with `main_system_demo.py` to see everything working
2. **Visualization**: Use the dashboard for best visual experience
3. **Testing**: Try different attack types and probabilities
4. **Clean mode**: Run without attacks to see normal trading behavior
5. **Configuration**: Edit the main files to adjust parameters

## Troubleshooting

**"No module named..."**
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

**"No data retrieved"**
- Check internet connection
- Market may be closed (try "5d" period instead of "1d")
- Try different symbol (MSFT, GOOGL, TSLA)

**Dashboard won't start**
- Ensure streamlit is installed: `pip install streamlit`
- Try different port: `streamlit run dashboard/dashboard_app.py --server.port 8502`

## Next Steps

After running the demos:
1. Review the performance summary
2. Try different configurations
3. Test various attack types
4. Explore the code structure
5. Read FINAL_DOCUMENTATION.md for details
