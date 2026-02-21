from data_loader import load_market_data
from replay_engine import stream_market_data

# Configuration
SYMBOL = "AAPL"
PERIOD = "1d"
INTERVAL = "1m"
DELAY = 1


def start_market_stream():
    """
    Start the market data stream simulator.
    Loads historical data and replays it as a live stream.
    """
    try:
        # Load historical market data
        data = load_market_data(SYMBOL, PERIOD, INTERVAL)
        
        # Stream data sequentially
        for tick in stream_market_data(data, SYMBOL, DELAY):
            # Data is yielded and printed by replay_engine
            pass
            
    except Exception as e:
        print(f"Error in market stream: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("MARKET DATA STREAM SIMULATOR - STEP 1")
    print("=" * 60)
    start_market_stream()
