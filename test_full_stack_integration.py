"""Full-stack integration test: Feed Integrity + Contagion Engine + MSI V2"""
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, '.')
from systemic.contagion_engine import ContagionEngine
from systemic.market_stability_index import MarketStabilityIndex
from feed_validation.feed_integrity_engine import FeedIntegrityEngine

# 1. Feed Integrity Engine
fe = FeedIntegrityEngine(deviation_threshold=0.01)
fe.register_feed('AAPL', 'yahoo')
fe.register_feed('AAPL', 'bloomberg')
now = datetime.utcnow()
fe.update_price('AAPL', 'yahoo', 178.50, now)
fe.update_price('AAPL', 'bloomberg', 178.55, now)
feed_health = fe.get_global_feed_health()

# 2. Contagion Engine
ce = ContagionEngine(window_size=15)
np.random.seed(42)
for i in range(20):
    ce.update_price('AAPL', 150.0 + i * 0.5 + np.random.randn() * 0.5)
    ce.update_price('MSFT', 300.0 + i * 0.3 + np.random.randn() * 0.5)
    ce.update_price('GOOGL', 2800 + i * 1.0 + np.random.randn() * 2.0)
contagion = ce.get_contagion_summary()

# 3. MSI V2 Integration
msi = MarketStabilityIndex()
result = msi.compute_msi(
    average_trust_score=85.0,
    market_anomaly_rate=0.02,
    total_anomalies=5,
    feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
    contagion_risk_score=contagion['contagion_risk_score']
)

print("=== FULL STACK INTEGRATION TEST ===")
print("Feed Mismatch Rate:", round(feed_health['global_feed_mismatch_rate'], 6))
print("Avg Feed Reliability:", round(feed_health['average_feed_reliability'], 2))
print("Contagion Risk Score:", round(contagion['contagion_risk_score'], 2))
print("Avg Correlation:", round(contagion['average_correlation'], 4))
print("Vol Sync Ratio:", round(contagion['volatility_sync_ratio'], 4))
print("Contagion Flag:", contagion['systemic_contagion_flag'])
print("MSI Score:", result['msi_score'])
print("Market State:", result['market_state'])
print("Risk Level:", result['risk_level'])
print()

# Assertions
assert 0 <= result['msi_score'] <= 100
assert result['market_state'] in ["STABLE", "ELEVATED RISK", "HIGH VOLATILITY", "SYSTEMIC RISK"]
assert 0 <= contagion['contagion_risk_score'] <= 100
assert 0 <= feed_health['global_feed_mismatch_rate'] <= 1

print("ALL INTEGRATION CHECKS PASSED")
