"""
Quick test to verify the data loading fix
"""

import sys
import pandas as pd

# Mock data for testing without yfinance
def create_test_data():
    """Create sample market data for testing."""
    import datetime
    
    dates = pd.date_range(start='2024-01-01 09:30:00', periods=10, freq='1min')
    prices = [189.42, 189.50, 189.35, 189.60, 189.45, 189.55, 189.40, 189.65, 189.50, 189.58]
    
    data = pd.DataFrame({
        'Datetime': dates,
        'Close': prices
    })
    
    return data


def test_stream():
    """Test the streaming functionality."""
    sys.path.append('data_stream')
    from replay_engine import stream_market_data
    
    print("Creating test data...")
    data = create_test_data()
    print(f"Created {len(data)} test data points")
    
    print("\nTesting stream...")
    count = 0
    for tick in stream_market_data(data, "TEST", delay=0.1):
        count += 1
        if count >= 5:  # Only test first 5
            print("...")
            break
    
    print(f"\n✓ Stream test passed! Processed {count} ticks successfully")


if __name__ == "__main__":
    try:
        test_stream()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
