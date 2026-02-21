# Step 2 - Trading Algorithm Documentation

## Overview

Step 2 builds a simple trading algorithm that consumes the market data stream from Step 1 and makes automated buy/sell decisions based on a Simple Moving Average (SMA) strategy.

## Architecture

```
Market Data Stream (Step 1)
        ↓
Trading Algorithm (SMA Logic)
        ↓
Buy/Sell Decisions
        ↓
Portfolio Management
```

## Components

### 1. TradingAlgorithm Class
- Implements Simple Moving Average (SMA) strategy
- Tracks price history and calculates moving average
- Makes buy/sell decisions based on price vs SMA
- Manages portfolio (balance + position)

### 2. TradingBotRunner Class
- Orchestrates market stream and trading algorithm
- Processes each market tick through trading logic
- Displays real-time trading decisions
- Shows performance summary

## Trading Strategy

### Simple Moving Average (SMA) Strategy

**Buy Signal:**
- Price crosses ABOVE SMA
- No current position held
- Sufficient balance available
- Action: Buy maximum shares affordable

**Sell Signal:**
- Price crosses BELOW SMA
- Position held
- Action: Sell all shares

**Hold:**
- No clear signal
- Maintain current position

## Configuration

Edit `trading_bot/bot_runner.py` or `main_trading_test.py`:

```python
bot = TradingBotRunner(
    symbol="AAPL",           # Stock ticker
    period="1d",             # Historical period
    interval="1m",           # Data resolution
    delay=0.5,               # Seconds between ticks
    window_size=5,           # SMA calculation window
    initial_balance=10000    # Starting cash
)
```

## Running Step 2

### Option 1: Run bot directly
```cmd
cd trading_bot
python bot_runner.py
```

### Option 2: Run test file
```cmd
python main_trading_test.py
```

## Expected Output

```
TRADING BOT - STEP 2
======================================================================
Symbol: AAPL
Initial Balance: $10000
SMA Window: 5
----------------------------------------------------------------------

Tick #1
  ⏳ WAIT | Price: $189.42 | SMA: None
  Reason: Insufficient data for SMA
  Balance: $10000 | Position: 0 shares
  Portfolio Value: $10000

Tick #6
  🟢 BUY  | Price: $189.50 | SMA: 189.35
  Reason: Price 189.50 > SMA 189.35
  Balance: $523.50 | Position: 50 shares
  Portfolio Value: $10000

Tick #15
  🔴 SELL | Price: $188.20 | SMA: 189.10
  Reason: Price 188.20 < SMA 189.10
  Balance: $9933.50 | Position: 0 shares
  Portfolio Value: $9933.50
```

## Key Features

✓ Real-time decision making
✓ Portfolio tracking (cash + position)
✓ Trade history logging
✓ Performance summary
✓ Visual indicators for actions
✓ Configurable strategy parameters

## Testing Checklist

- [ ] Bot connects to market stream
- [ ] SMA calculates correctly
- [ ] Buy signals trigger purchases
- [ ] Sell signals trigger sales
- [ ] Balance updates correctly
- [ ] Position tracking accurate
- [ ] Performance summary displays

## Next Steps

Step 3 will add:
- Data manipulation injection
- Anomaly detection
- Trust scoring
- Trading safeguards

## Troubleshooting

**No trades executing:**
- Adjust window_size (try 3-10)
- Use longer period ("5d")
- Check if market data has sufficient volatility

**Errors connecting to stream:**
- Ensure Step 1 works independently
- Verify data_stream module is accessible
- Check Python path configuration
