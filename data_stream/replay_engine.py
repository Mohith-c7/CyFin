import time


def stream_market_data(data, symbol="AAPL", delay=1):
    """
    Simulate live market data streaming by replaying historical data.
    
    Args:
        data: pandas DataFrame with Datetime and Close columns
        symbol: Stock ticker symbol
        delay: Seconds between each data emission
    
    Yields:
        Dictionary with timestamp, symbol, and price
    """
    print(f"Starting market stream for {symbol} with {delay}s delay...")
    
    for idx, row in data.iterrows():
        # Safely extract values
        timestamp = str(row["Datetime"])
        
        # Handle Close price - ensure it's a scalar value
        close_price = row["Close"]
        if hasattr(close_price, 'iloc'):
            # If it's a Series, get the first value
            close_price = close_price.iloc[0]
        
        output = {
            "timestamp": timestamp,
            "symbol": symbol,
            "price": float(close_price)
        }
        
        print("STREAM:", output)
        
        yield output
        time.sleep(delay)
    
    print("Stream completed.")
