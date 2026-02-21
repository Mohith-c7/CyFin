"""
Trading Strategy Module
Implements percentage change-based trading decisions
"""


class TradingStrategy:
    """
    Simple percentage change trading strategy.
    BUY if price increases > threshold%
    SELL if price decreases > threshold%
    HOLD otherwise
    """
    
    def __init__(self, threshold=2):
        """
        Initialize trading strategy.
        
        Args:
            threshold: Percentage change threshold for trading decisions
        """
        self.last_price = None
        self.threshold = threshold
    
    def decide(self, price):
        """
        Make trading decision based on price change.
        
        Args:
            price: Current market price
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        if self.last_price is None:
            self.last_price = price
            return "HOLD"
        
        # Calculate percentage change
        change = (price - self.last_price) / self.last_price * 100
        
        # Update last price
        self.last_price = price
        
        # Make decision
        if change > self.threshold:
            return "BUY"
        elif change < -self.threshold:
            return "SELL"
        else:
            return "HOLD"
