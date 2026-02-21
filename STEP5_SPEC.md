# Step 5 - Market Data Trust Score Engine

## Objective

Build a system that:
- ✅ Evaluates how trustworthy the market data is
- ✅ Converts anomaly signals into reliability score
- ✅ Outputs a numeric trust score (0–100)
- ✅ Classifies risk level
- ✅ Provides decision input for trading protection

This makes detection actionable.

## Why Trust Score is Important

Real financial systems don't just detect anomalies — they evaluate risk level.

Regulators, exchanges, and trading systems operate on graded trust:
- High confidence
- Medium confidence
- Low confidence

Binary anomaly flag is not enough.

Trust score provides:
- ✅ Severity
- ✅ Trend
- ✅ Decision threshold

## Updated System Architecture

```
Market Stream
    ↓
Attack Engine
    ↓
Anomaly Detector
    ↓
TRUST SCORE ENGINE (NEW)
    ↓
Trading Engine
```

## What We're Building

A scoring system that:
1. Receives anomaly result + z-score
2. Evaluates severity
3. Reduces trust score
4. Outputs reliability metric

**Score range:**
- 0 → Completely unreliable
- 100 → Fully trusted

## Trust Scoring Model

Simple but realistic.

**Base trust score = 100**

If anomaly occurs, score decreases based on severity:

| Z-score | Trust Reduction |
|---------|----------------|
| < 3     | No change      |
| 3–5     | -20            |
| 5–8     | -40            |
| > 8     | -60            |

**Trust classification:**

| Score   | Status     |
|---------|------------|
| 80–100  | SAFE       |
| 50–79   | CAUTION    |
| < 50    | DANGEROUS  |

## File Structure

```
market_integrity_project/
├── trust/
│   ├── __init__.py
│   ├── trust_config.py      # Trust thresholds
│   └── trust_engine.py       # Trust scoring logic
└── integration_trust_test.py # Full pipeline test
```

## Configuration Parameters

```python
SAFE_THRESHOLD = 80
CAUTION_THRESHOLD = 50
```

## Implementation

### trust_config.py

```python
SAFE_THRESHOLD = 80
CAUTION_THRESHOLD = 50
```

### trust_engine.py

```python
from trust.trust_config import SAFE_THRESHOLD, CAUTION_THRESHOLD

class TrustScoreEngine:
    def __init__(self):
        self.trust_score = 100
    
    def update_score(self, z_score):
        if z_score > 8:
            self.trust_score -= 60
        elif z_score > 5:
            self.trust_score -= 40
        elif z_score > 3:
            self.trust_score -= 20
        
        self.trust_score = max(0, self.trust_score)
    
    def classify(self):
        if self.trust_score >= SAFE_THRESHOLD:
            return "SAFE"
        elif self.trust_score >= CAUTION_THRESHOLD:
            return "CAUTION"
        else:
            return "DANGEROUS"
    
    def process_tick(self, tick):
        if tick["anomaly"]:
            self.update_score(tick["z_score"])
            print("⚠ TRUST REDUCED →", self.trust_score)
        
        tick["trust_score"] = self.trust_score
        tick["trust_level"] = self.classify()
        
        return tick
```

## Full Pipeline Integration

Pipeline now:

```
Market Stream
    ↓
Attack Engine
    ↓
Anomaly Detector
    ↓
Trust Score Engine
    ↓
Trading Engine
```

## Full Integration Test

```python
from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
from detection.anomaly_engine import AnomalyDetector
from trust.trust_engine import TrustScoreEngine
from trading.trading_engine import TradingEngine

data = load_market_data()

attacker = AttackEngine()
detector = AnomalyDetector()
trust = TrustScoreEngine()
trader = TradingEngine()

for tick in stream_market_data(data):
    tick = attacker.process_tick(tick)
    tick = detector.process_tick(tick)
    tick = trust.process_tick(tick)
    trader.process_tick(tick)
```

## How to Run

```cmd
python integration_trust_test.py
```

## Expected Output

Normal:
```
TRUST 100 SAFE
```

Attack moment:
```
🚨 ATTACK INJECTED
⚠ ANOMALY DETECTED
⚠ TRUST REDUCED → 60
TRUST LEVEL CAUTION
```

Trust now reflects system risk.

## Testing Requirements

Step 5 complete only if:
- ✅ Trust decreases after anomaly
- ✅ Severity affects reduction
- ✅ Classification correct
- ✅ Trust never below 0
- ✅ Pipeline stable

## Definition of Step 5 Complete

You now have:
- ✅ Anomaly detection
- ✅ Risk severity measurement
- ✅ Reliability scoring
- ✅ Data trust classification

Your system can now decide whether to trust data.
**Major milestone.**

## What You Have Built So Far

Complete cyber risk monitoring pipeline:

**MARKET → ATTACK → DETECTION → TRUST EVALUATION → TRADING**

Next we make system ACT.
