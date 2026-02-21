"""
Protection Engine Module
Evaluates trust level and blocks risky trades
"""

from protection.protection_config import BLOCK_THRESHOLD


class ProtectionEngine:
    """
    Trading protection layer that blocks decisions when data is unreliable.
    Acts as a data integrity firewall.
    """
    
    def __init__(self):
        """Initialize protection engine."""
        self.blocked_count = 0
        self.allowed_count = 0
    
    def process_tick(self, tick, trade_decision):
        """
        Evaluate trust level and decide if trade should be allowed.
        
        Args:
            tick: Market data dictionary with trust_level
            trade_decision: Trading decision from strategy (BUY/SELL/HOLD)
            
        Returns:
            Final decision (possibly BLOCKED)
        """
        trust_level = tick["trust_level"]
        
        # Block trades when data is dangerous
        if trust_level == BLOCK_THRESHOLD:
            if trade_decision in ["BUY", "SELL"]:
                print("🛑 TRADE BLOCKED — DATA UNRELIABLE")
                self.blocked_count += 1
                return "BLOCKED"
        
        # Warn on caution but allow trade
        if trust_level == "CAUTION":
            if trade_decision in ["BUY", "SELL"]:
                print("⚠ CAUTION — TRADE ALLOWED WITH RISK")
        
        self.allowed_count += 1
        return trade_decision
    
    def get_stats(self):
        """Get protection statistics."""
        return {
            "blocked": self.blocked_count,
            "allowed": self.allowed_count
        }
