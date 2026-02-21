"""
Integrity Monitor - Main orchestrator
Combines anomaly detection and trust scoring
"""

from integrity_monitor.anomaly_detector import AnomalyDetector
from integrity_monitor.trust_scorer import TrustScorer


class IntegrityMonitor:
    """
    Main integrity monitoring system.
    Validates market data and provides trust scores.
    """
    
    def __init__(self, window_size=20, contamination=0.1, 
                 initial_trust=100.0, decay_rate=10.0, recovery_rate=2.0):
        """
        Initialize integrity monitor.
        
        Args:
            window_size: Anomaly detection window
            contamination: Expected anomaly rate
            initial_trust: Starting trust score
            decay_rate: Trust decrease per anomaly
            recovery_rate: Trust increase per normal tick
        """
        self.anomaly_detector = AnomalyDetector(window_size, contamination)
        self.trust_scorer = TrustScorer(initial_trust, decay_rate, recovery_rate)
        
    def validate_tick(self, tick_data):
        """
        Validate market data tick.
        
        Args:
            tick_data: Market data dictionary
            
        Returns:
            Dictionary with validation results
        """
        price = tick_data["price"]
        
        # Detect anomaly
        anomaly_result = self.anomaly_detector.detect_anomaly(price)
        
        # Update trust score
        trust_result = self.trust_scorer.update_trust(anomaly_result)
        
        # Combine results
        validation = {
            "timestamp": tick_data["timestamp"],
            "symbol": tick_data["symbol"],
            "price": price,
            "is_anomaly": anomaly_result["is_anomaly"],
            "anomaly_confidence": anomaly_result["confidence"],
            "z_score": anomaly_result["z_score"],
            "percent_change": anomaly_result["percent_change"],
            "trust_score": trust_result["trust_score"],
            "trust_level": trust_result["trust_level"],
            "recommendation": trust_result["recommendation"],
            "safe_to_trade": trust_result["trust_level"] in ["HIGH", "MEDIUM"]
        }
        
        return validation
    
    def get_summary(self):
        """Get monitoring summary."""
        trust_summary = self.trust_scorer.get_summary()
        
        return {
            "trust_score": trust_summary["current_trust"],
            "total_anomalies": trust_summary["total_anomalies"],
            "total_ticks": trust_summary["total_ticks"],
            "anomaly_rate": trust_summary["anomaly_rate"]
        }
