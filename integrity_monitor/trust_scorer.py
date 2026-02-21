"""
Trust Scoring Module
Calculates reliability score for market data
"""


class TrustScorer:
    """
    Calculates trust score for market data based on anomaly detection
    and historical reliability.
    """
    
    def __init__(self, initial_trust=100.0, decay_rate=10.0, recovery_rate=2.0):
        """
        Initialize trust scorer.
        
        Args:
            initial_trust: Starting trust score (0-100)
            decay_rate: How much trust drops per anomaly
            recovery_rate: How much trust recovers per normal tick
        """
        self.trust_score = initial_trust
        self.initial_trust = initial_trust
        self.decay_rate = decay_rate
        self.recovery_rate = recovery_rate
        self.anomaly_count = 0
        self.total_ticks = 0
        self.trust_history = []
        
    def update_trust(self, anomaly_result):
        """
        Update trust score based on anomaly detection result.
        
        Args:
            anomaly_result: Dictionary from anomaly detector
            
        Returns:
            Dictionary with trust score and status
        """
        self.total_ticks += 1
        
        if anomaly_result["is_anomaly"]:
            self.anomaly_count += 1
            # Decrease trust based on confidence
            confidence = anomaly_result["confidence"]
            decrease = self.decay_rate * confidence
            self.trust_score = max(0, self.trust_score - decrease)
        else:
            # Gradually recover trust
            self.trust_score = min(self.initial_trust, self.trust_score + self.recovery_rate)
        
        self.trust_history.append(self.trust_score)
        
        # Determine trust level
        trust_level = self._get_trust_level(self.trust_score)
        
        return {
            "trust_score": round(self.trust_score, 2),
            "trust_level": trust_level,
            "anomaly_rate": round((self.anomaly_count / self.total_ticks) * 100, 2),
            "total_anomalies": self.anomaly_count,
            "total_ticks": self.total_ticks,
            "recommendation": self._get_recommendation(trust_level)
        }
    
    def _get_trust_level(self, score):
        """Categorize trust score into levels."""
        if score >= 80:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "LOW"
        else:
            return "CRITICAL"
    
    def _get_recommendation(self, trust_level):
        """Get trading recommendation based on trust level."""
        recommendations = {
            "HIGH": "SAFE_TO_TRADE",
            "MEDIUM": "TRADE_WITH_CAUTION",
            "LOW": "REDUCE_EXPOSURE",
            "CRITICAL": "HALT_TRADING"
        }
        return recommendations.get(trust_level, "UNKNOWN")
    
    def get_summary(self):
        """Get trust scoring summary."""
        return {
            "current_trust": round(self.trust_score, 2),
            "initial_trust": self.initial_trust,
            "total_anomalies": self.anomaly_count,
            "total_ticks": self.total_ticks,
            "anomaly_rate": round((self.anomaly_count / self.total_ticks) * 100, 2) if self.total_ticks > 0 else 0,
            "trust_history": self.trust_history
        }
