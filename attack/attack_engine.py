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
    
    def __init__(self, attack_enabled=ATTACK_ENABLED, attack_step=ATTACK_STEP, attack_multiplier=ATTACK_MULTIPLIER):
        """Initialize attack engine with step counter and optional configuration overrides."""
        self.step_counter = 0
        self.attack_enabled = attack_enabled
        
        # Handle string inputs (from UI like "10,25,50") or single values
        if isinstance(attack_step, str):
            self.attack_steps = [int(x.strip()) for x in attack_step.split(",") if x.strip()]
        else:
            self.attack_steps = [attack_step] if isinstance(attack_step, int) else attack_step
            
        if isinstance(attack_multiplier, str):
            self.attack_multipliers = [float(x.strip()) for x in attack_multiplier.split(",") if x.strip()]
        else:
            self.attack_multipliers = [attack_multiplier] if isinstance(attack_multiplier, (int, float)) else attack_multiplier
            
        # Ensure lists are of same length (pad multipliers if needed)
        if len(self.attack_multipliers) < len(self.attack_steps):
            last_mult = self.attack_multipliers[-1] if self.attack_multipliers else 1.15
            self.attack_multipliers.extend([last_mult] * (len(self.attack_steps) - len(self.attack_multipliers)))
    
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
        if self.attack_enabled and self.step_counter in self.attack_steps:
            idx = self.attack_steps.index(self.step_counter)
            multiplier = self.attack_multipliers[idx]
            price = price * multiplier
            attacked = True
            print(f"🚨 ATTACK INJECTED AT STEP {self.step_counter} (Multiplier: {multiplier})")
        
        return {
            "timestamp": tick["timestamp"],
            "symbol": tick["symbol"],
            "price": price,
            "attacked": attacked
        }
