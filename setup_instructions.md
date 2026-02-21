# Step 1 Setup Instructions

## Environment Setup

### 1. Create Virtual Environment

```cmd
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (CMD):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```cmd
pip install -r requirements.txt
```

## Running Step 1

### Option 1: Run from data_stream directory
```cmd
cd data_stream
python market_stream.py
```

### Option 2: Run main test file
```cmd
python main_stream_test.py
```

## Expected Output

You should see output like:
```
STREAM: {'timestamp': '2024-01-01 09:30:00', 'symbol': 'AAPL', 'price': 189.42}
STREAM: {'timestamp': '2024-01-01 09:31:00', 'symbol': 'AAPL', 'price': 189.50}
STREAM: {'timestamp': '2024-01-01 09:32:00', 'symbol': 'AAPL', 'price': 189.35}
```

## Configuration

Edit `data_stream/market_stream.py` to change:
- `SYMBOL`: Stock ticker (default: "AAPL")
- `PERIOD`: Historical window (default: "1d")
- `INTERVAL`: Data resolution (default: "1m")
- `DELAY`: Seconds between emissions (default: 1)

## Troubleshooting

### No data returned
- Market may be closed
- Try different symbols: "MSFT", "GOOGL", "TSLA"
- Use longer period: "5d" instead of "1d"

### SSL/Connection errors
- Check internet connection
- Verify firewall settings

### Time delay inconsistent
- Increase delay to ≥ 1 second
- Check system performance
