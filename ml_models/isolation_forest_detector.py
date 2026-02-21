"""
Isolation Forest ML Model for Anomaly Detection
Uses unsupervised machine learning to detect outliers
"""

from sklearn.ensemble import IsolationForest
import numpy as np


class IsolationForestDetector:
    """
    Machine learning-based anomaly detector using Isolation Forest algorithm.
    
    Isolation Forest is effective for detecting anomalies in financial data
    by isolating observations through random partitioning.
    """
    
    def __init__(self, contamination=0.1, random_state=42):
        """
        Initialize Isolation Forest detector.
        
        Args:
            contamination: Expected proportion of outliers (default: 0.1 = 10%)
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.trained = False
        self.training_data = []
        
    def add_training_data(self, price):
        """Add price to training dataset."""
        self.training_data.append(price)
        
    def train(self, min_samples=20):
        """
        Train the model on collected data.
        
        Args:
            min_samples: Minimum samples required for training
            
        Returns:
            bool: True if training successful
        """
        if len(self.training_data) < min_samples:
            return False
            
        # Reshape data for sklearn
        X = np.array(self.training_data).reshape(-1, 1)
        self.model.fit(X)
        self.trained = True
        return True
        
    def predict(self, price):
        """
        Predict if price is anomalous.
        
        Args:
            price: Current price to evaluate
            
        Returns:
            dict: {
                'is_anomaly': bool,
                'anomaly_score': float,
                'confidence': float
            }
        """
        if not self.trained:
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'confidence': 0.0,
                'status': 'not_trained'
            }
            
        # Predict (-1 = anomaly, 1 = normal)
        X = np.array([[price]])
        prediction = self.model.predict(X)[0]
        
        # Get anomaly score (lower = more anomalous)
        score = self.model.score_samples(X)[0]
        
        # Convert to 0-1 confidence scale
        confidence = abs(score) * 100
        
        return {
            'is_anomaly': prediction == -1,
            'anomaly_score': float(score),
            'confidence': min(confidence, 100.0),
            'status': 'trained'
        }
        
    def get_stats(self):
        """Get detector statistics."""
        return {
            'trained': self.trained,
            'training_samples': len(self.training_data),
            'contamination': self.model.contamination,
            'n_estimators': self.model.n_estimators
        }
