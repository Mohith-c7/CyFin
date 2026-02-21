"""
Protected Trading Engine Module
Trading engine with integrated protection layer
"""

from trading.strategy import TradingStrategy
from trading.portfolio import Portfolio


class ProtectedTradingEngine:
    """
    Trading engine with built-in protection mechanism.
    Integrates with protection layer to block risky trades.
    """
    
    def __init__(self):
        """Initialize protected trading engine."""
        self.strategy = TradingStrategy()
        self.portfolio = Portfolio()
    
    def execute_trade(self, decision, price):
        """
        Execute trading decision.
        
        Args:
            decision: Trading decision (BUY/SELL)
            price: Current price
        """
        if decision == "BUY":
            self.portfolio.buy(price)
        elif decision == "SELL":
            self.portfolio.sell(price)
    
    def log_status(self, price, decision):
        """
        Log current trading status.
        
        Args:
            price: Current price
            decision: Final decision
        """
        print(
            "PRICE:", round(price, 2),
            "| DECISION:", decision,
            "| CASH:", round(self.portfolio.cash, 2),
            "| SHARES:", self.portfolio.shares,
            "| VALUE:", round(self.portfolio.value(price), 2)
        )
    
    def process_tick(self, tick, protection_engine):
        """
        Process market tick with protection layer.
        
        Args:
            tick: Market data dictionary
            protection_engine: Protection engine instance
        """
        price = tick["price"]
        
        # Get strategy decision
        strategy_decision = self.strategy.decide(price)
        
        # Apply protection layer
        final_decision = protection_engine.process_tick(tick, strategy_decision)
        
        # Execute only if not blocked
        if final_decision not in ["BLOCKED", "HOLD"]:
            self.execute_trade(final_decision, price)
        
        # Log status
        self.log_status(price, final_decision)
