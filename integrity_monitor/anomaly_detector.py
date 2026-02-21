"""
Anomaly Detection Module
Detects abnormal price movements in market data stream
"""

import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Detects anomalies in market data using statistical methods
    and Isolation Forest algorithm.
    """
    
    def __init__(self, window_size=20, contamination=0.1):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Number of prices to analyze
            contamination: Expected proportion of anomalies (0.1 = 10%)
        """
        self.window_size = window_size
        self.contamination = contamination
        self.price_history = []
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_trained = False
        
    def add_price(self, price):
        """Add price to history."""
        self.price_history.append(price)
        
        # Keep only recent window
        if len(self.price_history) > self.window_size * 2:
            self.price_history = self.price_history[-self.window_size * 2:]
    
    def detect_anomaly(self, current_price):
        """
        Detect if current price is anomalous.
        
        Args:
            current_price: Current market price
            
        Returns:
            Dictionary with anomaly detection results
        """
        self.add_price(current_price)
        
        # Need sufficient data
        if len(self.price_history) < self.window_size:
            return {
                "is_anomaly": False,
                "confidence": 0.0,
                "method": "insufficient_data",
                "z_score": None,
                "percent_change": None
            }
        
        # Calculate statistical metrics
        recent_prices = self.price_history[-self.window_size:]
        mean_price = np.mean(recent_prices)
        std_price = np.std(recent_prices)
        
        # Z-score (statistical deviation)
        z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
        
        # Percent change from mean
        percent_change = ((current_price - mean_price) / mean_price) * 100
        
        # Statistical anomaly: Z-score > 3 (99.7% confidence)
        statistical_anomaly = abs(z_score) > 3
        
        # Machine learning anomaly detection
        ml_anomaly = False
        ml_score = 0.0
        
        if len(self.price_history) >= self.window_size:
            # Prepare features for ML model
            features = self._extract_features(current_price)
            
            # Train model if not trained
            if not self.is_trained and len(self.price_history) >= self.window_size:
                training_data = []
                for i in range(self.window_size, len(self.price_history)):
                    training_data.append(self._extract_features(self.price_history[i]))
                
                if len(training_data) >= 10:
                    self.model.fit(training_data)
                    self.is_trained = True
            
            # Predict if trained
            if self.is_trained:
                prediction = self.model.predict([features])[0]
                ml_anomaly = prediction == -1  # -1 indicates anomaly
                ml_score = self.model.score_samples([features])[0]
        
        # Combined decision
        is_anomaly = statistical_anomaly or ml_anomaly
        confidence = abs(z_score) / 3.0  # Normalize to 0-1 range
        
        return {
            "is_anomaly": is_anomaly,
            "confidence": min(confidence, 1.0),
            "method": "statistical+ml" if self.is_trained else "statistical",
            "z_score": round(z_score, 2),
            "percent_change": round(percent_change, 2),
            "ml_score": round(ml_score, 4) if self.is_trained else None
        }
    
    def _extract_features(self, current_price):
        """Extract features for ML model."""
        recent = self.price_history[-self.window_size:]
        
        return [
            current_price,
            np.mean(recent),
            np.std(recent),
            np.max(recent),
            np.min(recent),
            current_price - recent[-1] if len(recent) > 0 else 0,  # Price change
            (current_price - np.mean(recent)) / np.std(recent) if np.std(recent) > 0 else 0  # Z-score
        ]
