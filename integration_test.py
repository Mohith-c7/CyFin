"""
Integration Test - Step 1 + Step 2
Connects market data stream to trading engine
"""

import sys
sys.path.append('data_stream')
sys.path.append('trading')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from trading.trading_engine import TradingEngine


def run_integration_test():
    """Run integrated market stream + trading engine test."""
    print("=" * 80)
    print("INTEGRATION TEST - MARKET STREAM + TRADING ENGINE")
    print("=" * 80)
    print("Symbol: AAPL")
    print("Initial Cash: $10,000")
    print("Strategy: ±2% threshold")
    print("-" * 80)
    
    try:
        # Initialize trading engine
        engine = TradingEngine()
        
        # Load market data
        data = load_market_data(symbol="AAPL", period="1d", interval="1m")
        
        # Process each tick through trading engine
        tick_count = 0
        for tick in stream_market_data(data, symbol="AAPL", delay=0.1):
            tick_count += 1
            engine.process_tick(tick)
            
            # Limit output for testing (remove this for full run)
            if tick_count >= 50:
                print("\n... (showing first 50 ticks)")
                break
        
        # Final summary
        print("\n" + "=" * 80)
        print("TRADING SESSION COMPLETE")
        print("=" * 80)
        final_price = tick["price"]
        print(f"Final Cash: ${round(engine.portfolio.cash, 2)}")
        print(f"Final Shares: {engine.portfolio.shares}")
        print(f"Final Portfolio Value: ${round(engine.portfolio.value(final_price), 2)}")
        print(f"Total Ticks Processed: {tick_count}")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    print("Testing Step 1 + Step 2 Integration...")
    print("-" * 80)
    
    try:
        run_integration_test()
        print("\n✓ INTEGRATION TEST COMPLETE")
        print("Step 1 (Market Stream) + Step 2 (Trading Engine) working together!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
