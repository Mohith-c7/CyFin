"""
Trust Score Engine Module
Evaluates market data reliability and converts anomalies into trust scores
"""

from trust.trust_config import SAFE_THRESHOLD, CAUTION_THRESHOLD


class TrustScoreEngine:
    """
    Evaluates data trustworthiness and maintains reliability score.
    Converts anomaly severity into actionable trust metrics.
    """
    
    def __init__(self):
        """Initialize trust score engine with maximum trust."""
        self.trust_score = 100
    
    def update_score(self, z_score):
        """
        Update trust score based on anomaly severity.
        
        Args:
            z_score: Z-score from anomaly detection
        """
        if z_score > 8:
            self.trust_score -= 60
        elif z_score > 5:
            self.trust_score -= 40
        elif z_score > 3:
            self.trust_score -= 20
        
        # Ensure trust score never goes below 0
        self.trust_score = max(0, self.trust_score)
    
    def classify(self):
        """
        Classify current trust level.
        
        Returns:
            Trust level: "SAFE", "CAUTION", or "DANGEROUS"
        """
        if self.trust_score >= SAFE_THRESHOLD:
            return "SAFE"
        elif self.trust_score >= CAUTION_THRESHOLD:
            return "CAUTION"
        else:
            return "DANGEROUS"
    
    def process_tick(self, tick):
        """
        Process market tick and evaluate trust.
        
        Args:
            tick: Market data dictionary with anomaly and z_score
            
        Returns:
            Tick dictionary with trust_score and trust_level added
        """
        if tick.get("anomaly", False):
            self.update_score(tick["z_score"])
            print("⚠ TRUST REDUCED →", self.trust_score)
        
        tick["trust_score"] = self.trust_score
        tick["trust_level"] = self.classify()
        
        return tick
