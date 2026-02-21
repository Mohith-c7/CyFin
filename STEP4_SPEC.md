# Step 4 - Real-Time Market Data Anomaly Detection

## Objective

Build a module that:
- ✅ Continuously monitors incoming market prices
- ✅ Detects abnormal price behavior
- ✅ Flags suspicious data in real time
- ✅ Outputs anomaly signal

This sits between:
```
Market Data → Detection → Trading
```

## Why Step 4 is Most Important

This is the **actual protection layer**.

**Before Step 4:** System blindly trusts data  
**After Step 4:** System verifies data integrity

This is your project's central idea.

## New System Architecture

```
Market Data Stream
        ↓
Attack Injection
        ↓
ANOMALY DETECTION (NEW)
        ↓
Trading Engine
```

Later we add trust scoring and blocking.

## What We're Building

A real-time statistical monitoring engine that:
1. Observes recent price window
2. Computes expected distribution
3. Checks if new price deviates strongly
4. Flags anomaly if deviation large

## Detection Method

**Z-score Deviation Detection**

Why?
- ✅ Simple
- ✅ Explainable
- ✅ Fast
- ✅ Effective for spikes
- ✅ Judges understand

### Z-score Concept

Measures how far value is from average.
If price is extremely far → suspicious.

**Rule:** |z| > 3 → anomaly

## File Structure

```
market_integrity_project/
├── detection/
│   ├── __init__.py
│   ├── anomaly_config.py      # Detection parameters
│   └── anomaly_engine.py       # Detection logic
└── integration_detection_test.py # Full pipeline test
```

## Detection Parameters

Must be configurable:

```python
WINDOW_SIZE = 20  # Number of recent prices
Z_THRESHOLD = 3   # Anomaly cutoff
```

## Implementation

### anomaly_config.py

```python
WINDOW_SIZE = 20
Z_THRESHOLD = 3
```

### anomaly_engine.py

```python
import numpy as np
from detection.anomaly_config import WINDOW_SIZE, Z_THRESHOLD

class AnomalyDetector:
    def __init__(self):
        self.price_window = []
    
    def process_tick(self, tick):
        price = tick["price"]
        
        anomaly = False
        z_score = 0
        
        if len(self.price_window) >= WINDOW_SIZE:
            mean = np.mean(self.price_window)
            std = np.std(self.price_window)
            
            if std > 0:
                z_score = abs((price - mean) / std)
                
                if z_score > Z_THRESHOLD:
                    anomaly = True
                    print("⚠ ANOMALY DETECTED | Z =", round(z_score, 2))
        
        self.price_window.append(price)
        
        if len(self.price_window) > WINDOW_SIZE:
            self.price_window.pop(0)
        
        tick["anomaly"] = anomaly
        tick["z_score"] = z_score
        
        return tick
```

## Full Pipeline Integration

Pipeline now becomes:

```
Market Stream
    ↓
Attack Engine
    ↓
Anomaly Detector
    ↓
Trading Engine
```

## Full Integration Test

```python
from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
from detection.anomaly_engine import AnomalyDetector
from trading.trading_engine import TradingEngine

data = load_market_data()

attacker = AttackEngine()
detector = AnomalyDetector()
trader = TradingEngine()

for tick in stream_market_data(data):
    tick = attacker.process_tick(tick)
    tick = detector.process_tick(tick)
    trader.process_tick(tick)
```

## How to Run

```cmd
python integration_detection_test.py
```

## Expected Output

Normal ticks:
```
PRICE 189 HOLD
```

Attack moment:
```
🚨 ATTACK INJECTED
⚠ ANOMALY DETECTED | Z = 5.4
PRICE 220 BUY
```

Detection works but trade still happens (for now).
Next step blocks it.

## Testing Requirements

Step 4 complete only if:
- ✅ Anomaly detected during attack
- ✅ No false alerts during normal data
- ✅ Z-score printed
- ✅ Rolling window works
- ✅ Pipeline stable

## Definition of Step 4 Complete

You now have:
- ✅ Real-time monitoring
- ✅ Automatic anomaly detection
- ✅ Cyber attack identified
- ✅ Measurable abnormality

This is core cybersecurity layer.
**Huge milestone.**

## What You Have Built So Far

Realistic financial pipeline:

**MARKET → ATTACK → DETECTION → TRADING**

System now knows something is wrong.
Next we make it act.
