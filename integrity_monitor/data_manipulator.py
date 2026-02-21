"""
Data Manipulation Module
Simulates attacks on market data for testing
"""

import random
import numpy as np


class DataManipulator:
    """
    Simulates various types of market data manipulation attacks.
    Used for testing the integrity monitoring system.
    """
    
    def __init__(self, attack_probability=0.0, attack_type="spike"):
        """
        Initialize data manipulator.
        
        Args:
            attack_probability: Probability of attack per tick (0.0-1.0)
            attack_type: Type of attack (spike, drift, noise, flash_crash)
        """
        self.attack_probability = attack_probability
        self.attack_type = attack_type
        self.attack_count = 0
        
    def manipulate(self, tick_data):
        """
        Potentially manipulate market data tick.
        
        Args:
            tick_data: Original market data dictionary
            
        Returns:
            Tuple of (manipulated_tick_data, was_manipulated)
        """
        # Decide if attack happens
        if random.random() > self.attack_probability:
            return tick_data, False
        
        # Perform attack
        self.attack_count += 1
        manipulated = tick_data.copy()
        original_price = tick_data["price"]
        
        if self.attack_type == "spike":
            # Sudden price spike (±20-50%)
            multiplier = random.uniform(1.2, 1.5) if random.random() > 0.5 else random.uniform(0.5, 0.8)
            manipulated["price"] = original_price * multiplier
            
        elif self.attack_type == "drift":
            # Gradual drift (±5-15%)
            multiplier = random.uniform(1.05, 1.15) if random.random() > 0.5 else random.uniform(0.85, 0.95)
            manipulated["price"] = original_price * multiplier
            
        elif self.attack_type == "noise":
            # Random noise (±10-30%)
            noise = random.uniform(-0.3, 0.3)
            manipulated["price"] = original_price * (1 + noise)
            
        elif self.attack_type == "flash_crash":
            # Extreme drop (50-80%)
            multiplier = random.uniform(0.2, 0.5)
            manipulated["price"] = original_price * multiplier
            
        else:
            # Default: random manipulation
            multiplier = random.uniform(0.7, 1.3)
            manipulated["price"] = original_price * multiplier
        
        manipulated["price"] = round(manipulated["price"], 2)
        manipulated["manipulated"] = True
        manipulated["original_price"] = original_price
        
        return manipulated, True
    
    def get_stats(self):
        """Get manipulation statistics."""
        return {
            "attack_count": self.attack_count,
            "attack_type": self.attack_type,
            "attack_probability": self.attack_probability
        }
