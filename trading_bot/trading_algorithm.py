"""
Trading Algorithm - Simple Moving Average Strategy
Consumes market data stream and makes buy/sell decisions
"""


class TradingAlgorithm:
    """
    Simple Moving Average (SMA) trading strategy.
    Buys when price crosses above SMA, sells when crosses below.
    """
    
    def __init__(self, window_size=5, initial_balance=10000):
        """
        Initialize trading algorithm.
        
        Args:
            window_size: Number of prices for moving average calculation
            initial_balance: Starting cash balance
        """
        self.window_size = window_size
        self.price_history = []
        self.balance = initial_balance
        self.position = 0  # Number of shares held
        self.trades = []
        
    def calculate_sma(self):
        """Calculate Simple Moving Average from price history."""
        if len(self.price_history) < self.window_size:
            return None
        return sum(self.price_history[-self.window_size:]) / self.window_size
    
    def process_tick(self, tick_data):
        """
        Process incoming market data tick and make trading decision.
        
        Args:
            tick_data: Dictionary with timestamp, symbol, price
            
        Returns:
            Dictionary with trading decision and details
        """
        timestamp = tick_data["timestamp"]
        symbol = tick_data["symbol"]
        price = tick_data["price"]
        
        # Add price to history
        self.price_history.append(price)
        
        # Calculate SMA
        sma = self.calculate_sma()
        
        if sma is None:
            return {
                "timestamp": timestamp,
                "symbol": symbol,
                "price": price,
                "sma": None,
                "action": "WAIT",
                "reason": "Insufficient data for SMA",
                "balance": self.balance,
                "position": self.position
            }
        
        # Trading logic
        action = "HOLD"
        reason = "No signal"
        
        # Buy signal: price crosses above SMA and we have no position
        if price > sma and self.position == 0 and self.balance >= price:
            shares_to_buy = int(self.balance / price)
            if shares_to_buy > 0:
                cost = shares_to_buy * price
                self.balance -= cost
                self.position += shares_to_buy
                action = "BUY"
                reason = f"Price {price:.2f} > SMA {sma:.2f}"
                self.trades.append({
                    "timestamp": timestamp,
                    "action": "BUY",
                    "price": price,
                    "shares": shares_to_buy,
                    "cost": cost
                })
        
        # Sell signal: price crosses below SMA and we have position
        elif price < sma and self.position > 0:
            revenue = self.position * price
            self.balance += revenue
            shares_sold = self.position
            self.position = 0
            action = "SELL"
            reason = f"Price {price:.2f} < SMA {sma:.2f}"
            self.trades.append({
                "timestamp": timestamp,
                "action": "SELL",
                "price": price,
                "shares": shares_sold,
                "revenue": revenue
            })
        
        return {
            "timestamp": timestamp,
            "symbol": symbol,
            "price": price,
            "sma": round(sma, 2),
            "action": action,
            "reason": reason,
            "balance": round(self.balance, 2),
            "position": self.position,
            "portfolio_value": round(self.balance + (self.position * price), 2)
        }
    
    def get_performance_summary(self):
        """Get trading performance summary."""
        return {
            "total_trades": len(self.trades),
            "final_balance": round(self.balance, 2),
            "position": self.position,
            "trades": self.trades
        }
