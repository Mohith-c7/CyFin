"""
Ensemble Anomaly Detector
Combines multiple detection methods for improved accuracy
"""

from detection.anomaly_engine import AnomalyDetector
from ml_models.isolation_forest_detector import IsolationForestDetector


class EnsembleDetector:
    """
    Combines statistical and ML methods for robust anomaly detection.
    
    Uses voting mechanism:
    - Z-score (statistical)
    - Isolation Forest (ML)
    
    Anomaly declared if majority agree.
    """
    
    def __init__(self):
        """Initialize ensemble with multiple detectors."""
        self.zscore_detector = AnomalyDetector()
        self.ml_detector = IsolationForestDetector(contamination=0.1)
        self.detection_history = []
        
    def add_price(self, price):
        """Add price to all detectors."""
        # Add to Z-score detector's window
        self.zscore_detector.price_window.append(price)
        if len(self.zscore_detector.price_window) > 20:  # WINDOW_SIZE
            self.zscore_detector.price_window.pop(0)
        
        # Add to ML detector
        self.ml_detector.add_training_data(price)
        
        # Train ML model when enough data
        if not self.ml_detector.trained:
            self.ml_detector.train(min_samples=20)
            
    def detect(self, price):
        """
        Detect anomaly using ensemble voting.
        
        Args:
            price: Current price to evaluate
            
        Returns:
            dict: {
                'is_anomaly': bool,
                'confidence': float,
                'methods': dict of individual results,
                'votes': dict
            }
        """
        # Get Z-score detection
        tick = {'price': price}
        zscore_tick = self.zscore_detector.process_tick(tick)
        zscore_result = {
            'is_anomaly': zscore_tick.get('anomaly', False),
            'z_score': zscore_tick.get('z_score', 0),
            'severity': zscore_tick.get('z_score', 0)
        }
        
        # Get ML detection
        ml_result = self.ml_detector.predict(price)
        
        # Voting
        votes = {
            'zscore': zscore_result['is_anomaly'],
            'ml': ml_result['is_anomaly']
        }
        
        # Count votes
        anomaly_votes = sum(votes.values())
        total_votes = len(votes)
        
        # Majority decision
        is_anomaly = anomaly_votes > (total_votes / 2)
        
        # Calculate ensemble confidence
        confidences = []
        if zscore_result.get('severity'):
            confidences.append(abs(zscore_result['severity']) * 20)
        if ml_result.get('confidence'):
            confidences.append(ml_result['confidence'])
            
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        result = {
            'is_anomaly': is_anomaly,
            'confidence': avg_confidence,
            'votes': votes,
            'anomaly_votes': anomaly_votes,
            'total_votes': total_votes,
            'methods': {
                'zscore': zscore_result,
                'ml': ml_result
            }
        }
        
        self.detection_history.append(result)
        return result
        
    def get_stats(self):
        """Get ensemble statistics."""
        total_detections = len(self.detection_history)
        anomalies = sum(1 for d in self.detection_history if d['is_anomaly'])
        
        return {
            'total_detections': total_detections,
            'anomalies_detected': anomalies,
            'anomaly_rate': anomalies / total_detections if total_detections > 0 else 0,
            'zscore_window_size': len(self.zscore_detector.price_window),
            'ml_stats': self.ml_detector.get_stats()
        }
