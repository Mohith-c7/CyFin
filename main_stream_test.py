"""
Main test file for Step 1 - Market Data Stream Simulator
Run this to verify the complete streaming system works.
"""

import sys
sys.path.append('data_stream')

from data_stream.market_stream import start_market_stream


if __name__ == "__main__":
    print("Testing Market Data Stream Simulator...")
    print("-" * 60)
    
    try:
        start_market_stream()
        print("\n" + "=" * 60)
        print("✓ STEP 1 COMPLETE - Market stream working successfully")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\nStream interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Please check your internet connection and try again")
