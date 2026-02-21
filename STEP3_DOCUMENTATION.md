# Step 3 - Integrity Monitoring System Documentation

## Overview

Step 3 implements the core security layer: real-time anomaly detection, trust scoring, and data manipulation simulation for testing.

## Architecture

```
Market Data Stream
        ↓
Data Manipulator (optional - for testing)
        ↓
Anomaly Detector (Statistical + ML)
        ↓
Trust Scorer
        ↓
Validation Result + Trading Recommendation
```

## Components

### 1. Anomaly Detector
- **Statistical Detection**: Z-score analysis (3-sigma rule)
- **Machine Learning**: Isolation Forest algorithm
- **Features**: Price, mean, std, min, max, changes
- **Output**: Anomaly flag, confidence, metrics

### 2. Trust Scorer
- **Dynamic Scoring**: 0-100 scale
- **Trust Levels**: HIGH (80+), MEDIUM (60-79), LOW (40-59), CRITICAL (<40)
- **Decay**: Trust drops on anomalies
- **Recovery**: Trust recovers on normal data
- **Recommendations**: SAFE_TO_TRADE, TRADE_WITH_CAUTION, REDUCE_EXPOSURE, HALT_TRADING

### 3. Data Manipulator (Testing)
- **Attack Types**: spike, drift, noise, flash_crash
- **Configurable**: Attack probability and severity
- **Tracking**: Records all injected attacks

### 4. Integrity Monitor (Orchestrator)
- Combines anomaly detection and trust scoring
- Provides unified validation interface
- Generates trading recommendations

## Running Step 3

### Test with simulated attacks (default):
```cmd
python main_integrity_test.py
```

### Test with clean data:
```cmd
python main_integrity_test.py --clean
```

## Expected Output

```
INTEGRITY MONITORING SYSTEM - STEP 3
================================================================================
⚠️  ATTACK MODE ENABLED - Injecting manipulated data
Symbol: AAPL
Monitoring Window: 20 ticks
--------------------------------------------------------------------------------

Tick #1
  🟢 NORMAL  | Price: $189.42 | Z-Score: None
  🟢 Trust: 100.0 (HIGH) | SAFE_TO_TRADE

Tick #15 [INJECTED ATTACK]
  🔴 ANOMALY | Price: $245.50 | Z-Score: 4.2
  🟡 Trust: 72.5 (MEDIUM) | TRADE_WITH_CAUTION
  ⚠️  Anomaly detected! Confidence: 95%

Tick #30
  🔴 ANOMALY | Price: $98.20 | Z-Score: -5.1
  🔴 Trust: 28.3 (CRITICAL) | HALT_TRADING
  ⚠️  Anomaly detected! Confidence: 98%

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
🚨 CRITICAL ALERT: Trust score critically low - HALT TRADING
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

## Configuration

Edit `main_integrity_test.py`:

```python
monitor = IntegrityMonitor(
    window_size=20,          # Analysis window
    contamination=0.1,       # Expected anomaly rate
    initial_trust=100.0,     # Starting trust
    decay_rate=15.0,         # Trust drop per anomaly
    recovery_rate=3.0        # Trust recovery rate
)

manipulator = DataManipulator(
    attack_probability=0.15,  # 15% attack chance
    attack_type="spike"       # spike, drift, noise, flash_crash
)
```

## Attack Types

### Spike
- Sudden price jump (±20-50%)
- Simulates pump-and-dump

### Drift
- Gradual manipulation (±5-15%)
- Harder to detect

### Noise
- Random fluctuations (±10-30%)
- Simulates data corruption

### Flash Crash
- Extreme drop (50-80%)
- Simulates market crash

## Trust Score Mechanics

### Decay (on anomaly):
```
trust_score -= decay_rate * anomaly_confidence
```

### Recovery (on normal data):
```
trust_score += recovery_rate
trust_score = min(trust_score, initial_trust)
```

## Key Features

✓ Real-time anomaly detection
✓ Statistical + ML hybrid approach
✓ Dynamic trust scoring
✓ Attack simulation for testing
✓ Trading recommendations
✓ Visual alerts and indicators
✓ Comprehensive monitoring summary

## Testing Checklist

- [ ] Anomaly detector identifies spikes
- [ ] Trust score decreases on anomalies
- [ ] Trust score recovers on normal data
- [ ] Critical alerts trigger correctly
- [ ] ML model trains and predicts
- [ ] Attack injection works
- [ ] Summary statistics accurate

## Next Steps

Step 4 will integrate:
- Trading bot with integrity monitor
- Automated trading safeguards
- Dashboard visualization
- Complete end-to-end system

## Troubleshooting

**No anomalies detected:**
- Increase attack_probability
- Try different attack types
- Check window_size (try 10-30)

**Too many false positives:**
- Increase contamination parameter
- Adjust decay_rate
- Use longer window_size

**ML model not training:**
- Ensure sufficient data (20+ ticks)
- Check scikit-learn installation
