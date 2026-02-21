# Complete System Testing Guide

## Prerequisites

### 1. Install Dependencies

The installation command is running. Once complete, verify with:

```cmd
python check_setup.py
```

All packages should show ✓:
- ✓ pandas
- ✓ numpy
- ✓ yfinance
- ✓ sklearn
- ✓ streamlit
- ✓ plotly

If any show ✗, run:
```cmd
pip install -r requirements.txt
```

---

## Testing Sequence

### Test 1: Market Data Stream (Step 1)

**Command:**
```cmd
python main_stream_test.py
```

**Expected Output:**
```
Loading market data for AAPL...
Loaded 390 data points
Starting market stream for AAPL with 1s delay...
STREAM: {'timestamp': '2026-02-20 14:30:00+00:00', 'symbol': 'AAPL', 'price': 258.75}
STREAM: {'timestamp': '2026-02-20 14:31:00+00:00', 'symbol': 'AAPL', 'price': 258.67}
...
✓ STEP 1 COMPLETE
```

**Success Criteria:**
- ✅ 390 data points loaded
- ✅ Prices streaming sequentially
- ✅ No errors

---

### Test 2: Trading Algorithm (Steps 1+2)

**Command:**
```cmd
python integration_test.py
```

**Expected Output:**
```
PRICE: 258.75 | DECISION: HOLD | CASH: 10000 | SHARES: 0 | VALUE: 10000.0
PRICE: 258.67 | DECISION: HOLD | CASH: 10000 | SHARES: 0 | VALUE: 10000.0
...
✓ INTEGRATION TEST COMPLETE
```

**Success Criteria:**
- ✅ Trading decisions generated
- ✅ Portfolio updates correctly
- ✅ No errors

---

### Test 3: Attack Injection (Steps 1+2+3)

**Command:**
```cmd
python integration_attack_test.py
```

**Expected Output:**
```
Normal ticks (1-29):
PRICE: 258.75 | DECISION: HOLD | CASH: 10000 | SHARES: 0

Attack moment (step 30):
🚨 ATTACK INJECTED AT STEP 30
PRICE: 298.54 | DECISION: BUY | CASH: 9701.46 | SHARES: 1

After attack (step 31):
PRICE: 259.84 | DECISION: SELL | CASH: 9961.3 | SHARES: 0

Final Portfolio Value: $9961.30
LOSS: $38.70
```

**Success Criteria:**
- ✅ Attack injected at step 30
- ✅ Price manipulated: $259.60 → $298.54
- ✅ Trading bot made wrong decision (BUY)
- ✅ Financial loss demonstrated: $38.70

---

### Test 4: Anomaly Detection (Steps 1+2+3+4)

**Command:**
```cmd
python integration_detection_test.py
```

**Expected Output:**
```
Normal ticks (1-29):
PRICE: 258.75 | DECISION: HOLD

Attack moment (step 30):
🚨 ATTACK INJECTED AT STEP 30
⚠ ANOMALY DETECTED | Z = 5.4
PRICE: 298.54 | DECISION: BUY

DETECTION TEST COMPLETE
Total Ticks Processed: 50
Anomalies Detected: 1
Attack Injected: YES at step 30
Attack Detected: YES
```

**Success Criteria:**
- ✅ Anomaly detected at step 30
- ✅ Z-score calculated: 5.4
- ✅ Alert logged
- ✅ Trade still executes (no protection yet)

---

### Test 5: Trust Score Engine (Steps 1+2+3+4+5)

**Command:**
```cmd
python integration_trust_test.py
```

**Expected Output:**
```
Initial Trust: 100 (SAFE)

Normal ticks (1-29):
Step 10 | Trust: 100 (SAFE)
Step 20 | Trust: 100 (SAFE)

Attack moment (step 30):
🚨 ATTACK INJECTED AT STEP 30
⚠ ANOMALY DETECTED | Z = 5.4
⚠ TRUST REDUCED → 60
Step 30 | Trust: 60 (CAUTION)

TRUST EVALUATION TEST COMPLETE
Initial Trust: 100 (SAFE)
Final Trust: 60 (CAUTION)
Trust Reduction: 40 points
```

**Success Criteria:**
- ✅ Trust starts at 100 (SAFE)
- ✅ Trust drops to 60 after anomaly (CAUTION)
- ✅ Reduction matches Z-score severity (5.4 → -40 points)
- ✅ Classification correct

---

### Test 6: Trading Protection (Steps 1+2+3+4+5+6) - COMPLETE SYSTEM

**Command:**
```cmd
python integration_protection_test.py
```

**Expected Output:**
```
COMPLETE SYSTEM TEST - TRADING PROTECTION LAYER
Initial Cash: $10,000
Initial Trust: 100 (SAFE)
Protection: Block trades when DANGEROUS

Normal ticks (1-29):
PRICE: 258.75 | DECISION: HOLD | CASH: 10000 | SHARES: 0
Step 10 | Trust: 100 (SAFE)

Attack moment (step 30):
🚨 ATTACK INJECTED AT STEP 30
⚠ ANOMALY DETECTED | Z = 5.4
⚠ TRUST REDUCED → 60
Step 30 | Trust: 60 (CAUTION)
⚠ CAUTION — TRADE ALLOWED WITH RISK
PRICE: 298.54 | DECISION: BUY | CASH: 9701.46 | SHARES: 1

(If trust drops to DANGEROUS <50):
🛑 TRADE BLOCKED — DATA UNRELIABLE
PRICE: 298.54 | DECISION: BLOCKED | CASH: 10000 | SHARES: 0

COMPLETE SYSTEM TEST RESULTS
Data Integrity:
  Total Ticks Processed: 50
  Anomalies Detected: 1
  Attack Injected: YES at step 30

Trust Evaluation:
  Initial Trust: 100 (SAFE)
  Final Trust: 60 (CAUTION)
  Trust Reduction: 40 points

Protection Layer:
  Trades Blocked: 0 (or more if trust drops further)
  Trades Allowed: 50

Trading Performance:
  Final Portfolio Value: $9961.30 (or $10000 if blocked)

✅ COMPLETE SYSTEM TEST SUCCESSFUL!
🎉 ALL 6 STEPS WORKING TOGETHER!
```

**Success Criteria:**
- ✅ All 6 steps integrated
- ✅ Attack detected
- ✅ Trust evaluated
- ✅ Protection applied
- ✅ Trades blocked when DANGEROUS
- ✅ Warnings shown when CAUTION
- ✅ System stable

---

## Verification Checklist

Before demonstration, verify:

- [ ] Dependencies installed (`python check_setup.py`)
- [ ] Test 1 passed (Market stream working)
- [ ] Test 2 passed (Trading working)
- [ ] Test 3 passed (Attack demonstrated)
- [ ] Test 4 passed (Detection working)
- [ ] Test 5 passed (Trust scoring working)
- [ ] Test 6 passed (Protection working)

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Install dependencies
```cmd
pip install -r requirements.txt
```

### Issue: "No data retrieved"
**Solution:** Market may be closed, try:
```cmd
# Edit files to use longer period
period="5d" instead of "1d"
```

### Issue: "No anomalies detected"
**Solution:** Adjust attack parameters in `attack/attack_config.py`:
```python
ATTACK_STEP = 30
ATTACK_MULTIPLIER = 1.20  # Increase to 20%
```

### Issue: "Trust not dropping"
**Solution:** Check Z-score threshold in `detection/anomaly_config.py`:
```python
Z_THRESHOLD = 2.5  # Lower threshold
```

---

## Quick Test (Without Full Run)

If you want to quickly verify the system works:

```cmd
# Test just the first 10 ticks
python -c "
import sys
sys.path.append('data_stream')
from data_stream.data_loader import load_market_data
data = load_market_data('AAPL', '1d', '1m')
print(f'✓ Loaded {len(data)} data points')
print(f'✓ First price: ${data.iloc[0][\"Close\"]:.2f}')
print(f'✓ Last price: ${data.iloc[-1][\"Close\"]:.2f}')
"
```

---

## Performance Expectations

**Test Duration:**
- Test 1: ~10 seconds (limited to 50 ticks)
- Test 2: ~10 seconds (limited to 50 ticks)
- Test 3: ~10 seconds (limited to 50 ticks)
- Test 4: ~10 seconds (limited to 50 ticks)
- Test 5: ~10 seconds (limited to 50 ticks)
- Test 6: ~10 seconds (limited to 50 ticks)

**Full Run (390 ticks):**
- With 0.1s delay: ~40 seconds
- With 1s delay: ~6.5 minutes

---

## Expected Results Summary

| Test | Attack | Detection | Trust | Protection | Loss |
|------|--------|-----------|-------|------------|------|
| 1 | N/A | N/A | N/A | N/A | N/A |
| 2 | N/A | N/A | N/A | N/A | $0 |
| 3 | ✅ Yes | ❌ No | ❌ No | ❌ No | $38.70 |
| 4 | ✅ Yes | ✅ Yes | ❌ No | ❌ No | $38.70 |
| 5 | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | $38.70 |
| 6 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | $0-38.70* |

*Depends on trust level and protection policy

---

## Success Indicators

**System is working correctly if:**

1. ✅ Market data loads (390 points)
2. ✅ Trading decisions generated
3. ✅ Attack injected at step 30
4. ✅ Anomaly detected (Z-score = 5.4)
5. ✅ Trust drops (100 → 60)
6. ✅ Protection applied (warning or block)
7. ✅ No crashes or errors

---

## Next Steps After Testing

Once all tests pass:

1. ✅ Review test outputs
2. ✅ Verify all 6 steps working
3. ✅ Prepare demonstration
4. ✅ Practice presentation
5. ✅ Document results
6. ✅ Ready for hackathon!

---

**Your system is complete and ready for demonstration!**
