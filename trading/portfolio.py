"""
Portfolio Management Module
Tracks cash, shares, and portfolio value
"""


class Portfolio:
    """
    Manages virtual trading portfolio.
    Tracks cash balance and share holdings.
    """
    
    def __init__(self, cash=10000):
        """
        Initialize portfolio.
        
        Args:
            cash: Initial cash balance
        """
        self.cash = cash
        self.shares = 0
    
    def buy(self, price):
        """
        Buy one share if sufficient cash available.
        
        Args:
            price: Current share price
        """
        if self.cash >= price:
            self.shares += 1
            self.cash -= price
    
    def sell(self, price):
        """
        Sell one share if shares available.
        
        Args:
            price: Current share price
        """
        if self.shares > 0:
            self.shares -= 1
            self.cash += price
    
    def value(self, current_price):
        """
        Calculate total portfolio value.
        
        Args:
            current_price: Current share price
            
        Returns:
            Total portfolio value (cash + shares value)
        """
        return self.cash + self.shares * current_price
