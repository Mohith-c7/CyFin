"""
Main test file for Step 2 - Trading Algorithm
Run this to verify the trading bot works with market stream
"""

import sys
sys.path.append('trading_bot')

from trading_bot.bot_runner import TradingBotRunner


if __name__ == "__main__":
    print("Testing Trading Bot with Market Data Stream...")
    print("-" * 70)
    
    try:
        # Initialize and run trading bot
        bot = TradingBotRunner(
            symbol="AAPL",
            period="1d",
            interval="1m",
            delay=0.5,  # Faster for demo
            window_size=5,
            initial_balance=10000
        )
        
        bot.run()
        
        print("\n✓ STEP 2 COMPLETE - Trading bot working successfully")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Please ensure Step 1 is working and dependencies are installed")
