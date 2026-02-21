"""
Attack Engine Module
Simulates cyber attack on market data feed
"""

from attack.attack_config import (
    ATTACK_ENABLED,
    ATTACK_STEP,
    ATTACK_MULTIPLIER
)


class AttackEngine:
    """
    Simulates cyber attack by manipulating market data.
    Injects price manipulation at configured step.
    """
    
    def __init__(self):
        """Initialize attack engine with step counter."""
        self.step_counter = 0
    
    def process_tick(self, tick):
        """
        Process market tick and potentially inject attack.
        
        Args:
            tick: Market data dictionary from stream
            
        Returns:
            Modified tick dictionary with attack flag
        """
        self.step_counter += 1
        
        price = tick["price"]
        attacked = False
        
        # Check if attack should be injected
        if ATTACK_ENABLED and self.step_counter == ATTACK_STEP:
            price = price * ATTACK_MULTIPLIER
            attacked = True
            print("🚨 ATTACK INJECTED AT STEP", self.step_counter)
        
        return {
            "timestamp": tick["timestamp"],
            "symbol": tick["symbol"],
            "price": price,
            "attacked": attacked
        }
