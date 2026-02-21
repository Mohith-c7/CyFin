"""
Integration Attack Test - Step 1 + Step 2 + Step 3
Tests complete pipeline with simulated cyber attack
"""

import sys
sys.path.append('data_stream')
sys.path.append('trading')
sys.path.append('attack')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from trading.trading_engine import TradingEngine
from attack.attack_engine import AttackEngine


def run_attack_test():
    """Run integrated test with attack injection."""
    print("=" * 80)
    print("INTEGRATION ATTACK TEST - SIMULATED CYBER ATTACK")
    print("=" * 80)
    print("Symbol: AAPL")
    print("Initial Cash: $10,000")
    print("Attack: ENABLED at step 30 (15% price spike)")
    print("-" * 80)
    
    try:
        # Initialize components
        engine = TradingEngine()
        attacker = AttackEngine()
        
        # Load market data
        data = load_market_data(symbol="AAPL", period="1d", interval="1m")
        
        # Process pipeline: Stream → Attack → Trading
        tick_count = 0
        for tick in stream_market_data(data, symbol="AAPL", delay=0.1):
            tick_count += 1
            
            # Inject attack
            attacked_tick = attacker.process_tick(tick)
            
            # Process through trading engine
            engine.process_tick(attacked_tick)
            
            # Limit output for testing
            if tick_count >= 50:
                print("\n... (showing first 50 ticks)")
                break
        
        # Final summary
        print("\n" + "=" * 80)
        print("ATTACK TEST COMPLETE")
        print("=" * 80)
        final_price = attacked_tick["price"]
        print(f"Final Cash: ${round(engine.portfolio.cash, 2)}")
        print(f"Final Shares: {engine.portfolio.shares}")
        print(f"Final Portfolio Value: ${round(engine.portfolio.value(final_price), 2)}")
        print(f"Total Ticks Processed: {tick_count}")
        print(f"Attack Injected: YES at step 30")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    print("Testing Market Stream + Attack Injection + Trading Engine...")
    print("-" * 80)
    
    try:
        run_attack_test()
        print("\n✓ ATTACK INJECTION TEST COMPLETE")
        print("Cyber attack successfully simulated!")
        print("Trading engine reacted to manipulated data!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
