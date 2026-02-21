"""
Protected Trading Bot - Integrates trading with integrity monitoring
"""

import sys
sys.path.append('..')

from trading_bot.trading_algorithm import TradingAlgorithm
from integrity_monitor.integrity_monitor import IntegrityMonitor


class ProtectedTradingBot:
    """
    Trading bot with built-in integrity monitoring and safeguards.
    Only trades when data is trusted.
    """
    
    def __init__(self, window_size=5, initial_balance=10000,
                 monitor_window=20, contamination=0.1,
                 initial_trust=100.0, decay_rate=15.0, recovery_rate=3.0):
        """
        Initialize protected trading bot.
        
        Args:
            window_size: SMA window for trading
            initial_balance: Starting cash
            monitor_window: Anomaly detection window
            contamination: Expected anomaly rate
            initial_trust: Starting trust score
            decay_rate: Trust decrease rate
            recovery_rate: Trust recovery rate
        """
        self.trading_algo = TradingAlgorithm(window_size, initial_balance)
        self.integrity_monitor = IntegrityMonitor(
            monitor_window, contamination, initial_trust, decay_rate, recovery_rate
        )
        self.blocked_trades = 0
        self.executed_trades = 0
        self.total_ticks = 0
        
    def process_tick(self, tick_data):
        """
        Process market tick with integrity validation.
        
        Args:
            tick_data: Market data dictionary
            
        Returns:
            Dictionary with validation and trading results
        """
        self.total_ticks += 1
        
        # Validate data integrity
        validation = self.integrity_monitor.validate_tick(tick_data)
        
        # Make trading decision
        trading_decision = self.trading_algo.process_tick(tick_data)
        
        # Apply safeguards
        final_action = trading_decision["action"]
        blocked = False
        
        if not validation["safe_to_trade"]:
            # Block trading if data not trusted
            if trading_decision["action"] in ["BUY", "SELL"]:
                final_action = "BLOCKED"
                blocked = True
                self.blocked_trades += 1
        else:
            if trading_decision["action"] in ["BUY", "SELL"]:
                self.executed_trades += 1
        
        return {
            # Validation info
            "timestamp": validation["timestamp"],
            "symbol": validation["symbol"],
            "price": validation["price"],
            "is_anomaly": validation["is_anomaly"],
            "trust_score": validation["trust_score"],
            "trust_level": validation["trust_level"],
            "safe_to_trade": validation["safe_to_trade"],
            
            # Trading info
            "sma": trading_decision["sma"],
            "intended_action": trading_decision["action"],
            "final_action": final_action,
            "blocked": blocked,
            "balance": trading_decision["balance"],
            "position": trading_decision["position"],
            "portfolio_value": trading_decision["portfolio_value"],
            
            # Recommendation
            "recommendation": validation["recommendation"]
        }
    
    def get_summary(self):
        """Get comprehensive system summary."""
        integrity_summary = self.integrity_monitor.get_summary()
        trading_summary = self.trading_algo.get_performance_summary()
        
        return {
            "total_ticks": self.total_ticks,
            "trust_score": integrity_summary["trust_score"],
            "total_anomalies": integrity_summary["total_anomalies"],
            "anomaly_rate": integrity_summary["anomaly_rate"],
            "executed_trades": self.executed_trades,
            "blocked_trades": self.blocked_trades,
            "final_balance": trading_summary["final_balance"],
            "final_position": trading_summary["position"],
            "trade_history": trading_summary["trades"]
        }
