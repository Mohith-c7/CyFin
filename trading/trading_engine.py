"""
Trading Engine Module
Connects market stream to trading strategy and portfolio
"""

from trading.strategy import TradingStrategy
from trading.portfolio import Portfolio


class TradingEngine:
    """
    Main trading engine that processes market ticks
    and executes trading decisions.
    """
    
    def __init__(self):
        """Initialize trading engine with strategy and portfolio."""
        self.strategy = TradingStrategy()
        self.portfolio = Portfolio()
    
    def process_tick(self, tick):
        """
        Process market data tick and execute trading decision.
        
        Args:
            tick: Market data dictionary with price
        """
        price = tick["price"]
        
        # Get trading decision
        decision = self.strategy.decide(price)
        
        # Execute decision
        if decision == "BUY":
            self.portfolio.buy(price)
        elif decision == "SELL":
            self.portfolio.sell(price)
        
        # Log trading activity
        print(
            "PRICE:", round(price, 2),
            "| DECISION:", decision,
            "| CASH:", round(self.portfolio.cash, 2),
            "| SHARES:", self.portfolio.shares,
            "| VALUE:", round(self.portfolio.value(price), 2)
        )
