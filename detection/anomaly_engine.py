"""
Anomaly Detection Engine Module
Real-time statistical monitoring using Z-score deviation
"""

import numpy as np
from detection.anomaly_config import WINDOW_SIZE, Z_THRESHOLD


class AnomalyDetector:
    """
    Real-time anomaly detector using Z-score statistical analysis.
    Detects abnormal price deviations from recent history.
    """
    
    def __init__(self):
        """Initialize anomaly detector with empty price window."""
        self.price_window = []
    
    def process_tick(self, tick):
        """
        Process market tick and detect anomalies.
        
        Args:
            tick: Market data dictionary with price
            
        Returns:
            Tick dictionary with anomaly flag and z-score added
        """
        price = tick["price"]
        
        anomaly = False
        z_score = 0
        
        # Only detect after collecting sufficient data
        if len(self.price_window) >= WINDOW_SIZE:
            mean = np.mean(self.price_window)
            std = np.std(self.price_window)
            
            if std > 0:
                z_score = abs((price - mean) / std)
                
                if z_score > Z_THRESHOLD:
                    anomaly = True
                    print("⚠ ANOMALY DETECTED | Z =", round(z_score, 2))
        
        # Update rolling window
        self.price_window.append(price)
        
        if len(self.price_window) > WINDOW_SIZE:
            self.price_window.pop(0)
        
        # Add detection results to tick
        tick["anomaly"] = anomaly
        tick["z_score"] = z_score
        
        return tick
