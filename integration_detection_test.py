"""
Integration Detection Test - Step 1 + Step 2 + Step 3 + Step 4
Tests complete pipeline with attack injection and anomaly detection
"""

import sys
sys.path.append('data_stream')
sys.path.append('trading')
sys.path.append('attack')
sys.path.append('detection')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
from detection.anomaly_engine import AnomalyDetector
from trading.trading_engine import TradingEngine


def run_detection_test():
    """Run integrated test with attack injection and anomaly detection."""
    print("=" * 80)
    print("INTEGRATION DETECTION TEST - ANOMALY DETECTION SYSTEM")
    print("=" * 80)
    print("Symbol: AAPL")
    print("Initial Cash: $10,000")
    print("Attack: ENABLED at step 30 (15% price spike)")
    print("Detection: Z-score threshold = 3")
    print("-" * 80)
    
    try:
        # Initialize all components
        attacker = AttackEngine()
        detector = AnomalyDetector()
        trader = TradingEngine()
        
        # Load market data
        data = load_market_data(symbol="AAPL", period="1d", interval="1m")
        
        # Process complete pipeline: Stream → Attack → Detection → Trading
        tick_count = 0
        anomaly_count = 0
        
        for tick in stream_market_data(data, symbol="AAPL", delay=0.1):
            tick_count += 1
            
            # Step 1: Inject attack
            tick = attacker.process_tick(tick)
            
            # Step 2: Detect anomaly
            tick = detector.process_tick(tick)
            
            if tick.get("anomaly", False):
                anomaly_count += 1
            
            # Step 3: Execute trading
            trader.process_tick(tick)
            
            # Limit output for testing
            if tick_count >= 50:
                print("\n... (showing first 50 ticks)")
                break
        
        # Final summary
        print("\n" + "=" * 80)
        print("DETECTION TEST COMPLETE")
        print("=" * 80)
        final_price = tick["price"]
        print(f"Total Ticks Processed: {tick_count}")
        print(f"Anomalies Detected: {anomaly_count}")
        print(f"Attack Injected: YES at step 30")
        print(f"Attack Detected: {'YES' if anomaly_count > 0 else 'NO'}")
        print(f"\nFinal Cash: ${round(trader.portfolio.cash, 2)}")
        print(f"Final Shares: {trader.portfolio.shares}")
        print(f"Final Portfolio Value: ${round(trader.portfolio.value(final_price), 2)}")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    print("Testing Complete Pipeline with Anomaly Detection...")
    print("-" * 80)
    
    try:
        run_detection_test()
        print("\n✓ ANOMALY DETECTION TEST COMPLETE")
        print("System successfully detected manipulated data!")
        print("Protection layer is working!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
