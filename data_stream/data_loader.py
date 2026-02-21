import yfinance as yf
import pandas as pd


def load_market_data(symbol="AAPL", period="1d", interval="1m"):
    """
    Load historical market data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        period: Historical window (e.g., "1d", "5d", "1mo")
        interval: Data resolution (e.g., "1m", "5m", "1h")
    
    Returns:
        pandas DataFrame with Datetime and Close columns
    
    Raises:
        ValueError: If no data is retrieved
    """
    print(f"Loading market data for {symbol}...")
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    
    if data.empty:
        raise ValueError(f"No market data retrieved for {symbol}")
    
    # Handle multi-level columns (yfinance sometimes returns these)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    data = data.dropna()
    data.reset_index(inplace=True)
    
    # Handle different datetime column names
    datetime_col = None
    for col in ['Datetime', 'Date', 'datetime', 'date']:
        if col in data.columns:
            datetime_col = col
            break
    
    if datetime_col is None:
        # If no datetime column found, use index
        datetime_col = data.columns[0]
    
    # Ensure Close column exists
    if 'Close' not in data.columns:
        raise ValueError(f"Close price data not found for {symbol}")
    
    # Create clean dataframe with consistent column names
    result = pd.DataFrame({
        'Datetime': data[datetime_col],
        'Close': data['Close']
    })
    
    print(f"Loaded {len(result)} data points")
    return result
