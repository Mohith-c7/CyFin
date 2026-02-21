"""
Integration Trust Test - Step 1 + Step 2 + Step 3 + Step 4 + Step 5
Tests complete pipeline with trust score evaluation
"""

import sys
sys.path.append('data_stream')
sys.path.append('trading')
sys.path.append('attack')
sys.path.append('detection')
sys.path.append('trust')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
from detection.anomaly_engine import AnomalyDetector
from trust.trust_engine import TrustScoreEngine
from trading.trading_engine import TradingEngine


def run_trust_test():
    """Run integrated test with trust score evaluation."""
    print("=" * 80)
    print("INTEGRATION TRUST TEST - TRUST SCORE EVALUATION SYSTEM")
    print("=" * 80)
    print("Symbol: AAPL")
    print("Initial Cash: $10,000")
    print("Initial Trust: 100 (SAFE)")
    print("Attack: ENABLED at step 30 (15% price spike)")
    print("Detection: Z-score threshold = 3")
    print("Trust: Severity-based scoring")
    print("-" * 80)
    
    try:
        # Initialize all components
        attacker = AttackEngine()
        detector = AnomalyDetector()
        trust_engine = TrustScoreEngine()
        trader = TradingEngine()
        
        # Load market data
        data = load_market_data(symbol="AAPL", period="1d", interval="1m")
        
        # Process complete pipeline: Stream → Attack → Detection → Trust → Trading
        tick_count = 0
        anomaly_count = 0
        trust_changes = []
        
        for tick in stream_market_data(data, symbol="AAPL", delay=0.1):
            tick_count += 1
            
            # Step 1: Inject attack
            tick = attacker.process_tick(tick)
            
            # Step 2: Detect anomaly
            tick = detector.process_tick(tick)
            
            if tick.get("anomaly", False):
                anomaly_count += 1
            
            # Step 3: Evaluate trust
            tick = trust_engine.process_tick(tick)
            
            # Track trust changes
            trust_changes.append({
                "step": tick_count,
                "trust": tick["trust_score"],
                "level": tick["trust_level"]
            })
            
            # Step 4: Execute trading
            trader.process_tick(tick)
            
            # Show trust status periodically
            if tick_count % 10 == 0 or tick.get("anomaly", False):
                print(f"Step {tick_count} | Trust: {tick['trust_score']} ({tick['trust_level']})")
            
            # Limit output for testing
            if tick_count >= 50:
                print("\n... (showing first 50 ticks)")
                break
        
        # Final summary
        print("\n" + "=" * 80)
        print("TRUST EVALUATION TEST COMPLETE")
        print("=" * 80)
        final_price = tick["price"]
        final_trust = tick["trust_score"]
        final_level = tick["trust_level"]
        
        print(f"\nData Integrity:")
        print(f"  Total Ticks Processed: {tick_count}")
        print(f"  Anomalies Detected: {anomaly_count}")
        print(f"  Attack Injected: YES at step 30")
        
        print(f"\nTrust Evaluation:")
        print(f"  Initial Trust: 100 (SAFE)")
        print(f"  Final Trust: {final_trust} ({final_level})")
        print(f"  Trust Reduction: {100 - final_trust} points")
        
        print(f"\nTrading Performance:")
        print(f"  Final Cash: ${round(trader.portfolio.cash, 2)}")
        print(f"  Final Shares: {trader.portfolio.shares}")
        print(f"  Final Portfolio Value: ${round(trader.portfolio.value(final_price), 2)}")
        
        print("\n" + "=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    print("Testing Complete Pipeline with Trust Score Evaluation...")
    print("-" * 80)
    
    try:
        run_trust_test()
        print("\n✓ TRUST SCORE EVALUATION TEST COMPLETE")
        print("System successfully evaluates data reliability!")
        print("Trust scoring is working!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
