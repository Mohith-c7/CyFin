"""
Performance Metrics Calculator
Tracks detection accuracy, precision, recall, F1 score
"""


class PerformanceMetrics:
    """
    Calculates performance metrics for anomaly detection system.
    
    Tracks:
    - True Positives: Correctly detected attacks
    - False Positives: Normal data flagged as attack
    - True Negatives: Normal data correctly identified
    - False Negatives: Missed attacks
    """
    
    def __init__(self):
        """Initialize metrics counters."""
        self.true_positives = 0
        self.false_positives = 0
        self.true_negatives = 0
        self.false_negatives = 0
        self.total_predictions = 0
        
    def record_prediction(self, predicted_anomaly, actual_anomaly):
        """
        Record a prediction result.
        
        Args:
            predicted_anomaly: bool - System detected anomaly
            actual_anomaly: bool - Actual attack occurred
        """
        self.total_predictions += 1
        
        if predicted_anomaly and actual_anomaly:
            self.true_positives += 1
        elif predicted_anomaly and not actual_anomaly:
            self.false_positives += 1
        elif not predicted_anomaly and not actual_anomaly:
            self.true_negatives += 1
        elif not predicted_anomaly and actual_anomaly:
            self.false_negatives += 1
            
    def calculate_accuracy(self):
        """
        Calculate overall accuracy.
        
        Returns:
            float: Accuracy percentage (0-100)
        """
        if self.total_predictions == 0:
            return 0.0
            
        correct = self.true_positives + self.true_negatives
        return (correct / self.total_predictions) * 100
        
    def calculate_precision(self):
        """
        Calculate precision (positive predictive value).
        
        Precision = TP / (TP + FP)
        
        Returns:
            float: Precision percentage (0-100)
        """
        denominator = self.true_positives + self.false_positives
        if denominator == 0:
            return 0.0
            
        return (self.true_positives / denominator) * 100
        
    def calculate_recall(self):
        """
        Calculate recall (sensitivity, true positive rate).
        
        Recall = TP / (TP + FN)
        
        Returns:
            float: Recall percentage (0-100)
        """
        denominator = self.true_positives + self.false_negatives
        if denominator == 0:
            return 0.0
            
        return (self.true_positives / denominator) * 100
        
    def calculate_f1_score(self):
        """
        Calculate F1 score (harmonic mean of precision and recall).
        
        F1 = 2 * (Precision * Recall) / (Precision + Recall)
        
        Returns:
            float: F1 score (0-100)
        """
        precision = self.calculate_precision()
        recall = self.calculate_recall()
        
        if precision + recall == 0:
            return 0.0
            
        return 2 * (precision * recall) / (precision + recall)
        
    def calculate_specificity(self):
        """
        Calculate specificity (true negative rate).
        
        Specificity = TN / (TN + FP)
        
        Returns:
            float: Specificity percentage (0-100)
        """
        denominator = self.true_negatives + self.false_positives
        if denominator == 0:
            return 0.0
            
        return (self.true_negatives / denominator) * 100
        
    def get_confusion_matrix(self):
        """
        Get confusion matrix.
        
        Returns:
            dict: Confusion matrix values
        """
        return {
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'true_negatives': self.true_negatives,
            'false_negatives': self.false_negatives
        }
        
    def get_all_metrics(self):
        """
        Get all performance metrics.
        
        Returns:
            dict: All calculated metrics
        """
        return {
            'accuracy': self.calculate_accuracy(),
            'precision': self.calculate_precision(),
            'recall': self.calculate_recall(),
            'f1_score': self.calculate_f1_score(),
            'specificity': self.calculate_specificity(),
            'confusion_matrix': self.get_confusion_matrix(),
            'total_predictions': self.total_predictions
        }
        
    def get_summary(self):
        """Get formatted summary string."""
        metrics = self.get_all_metrics()
        
        summary = f"""
Performance Metrics Summary:
============================
Total Predictions: {metrics['total_predictions']}

Confusion Matrix:
  True Positives:  {metrics['confusion_matrix']['true_positives']}
  False Positives: {metrics['confusion_matrix']['false_positives']}
  True Negatives:  {metrics['confusion_matrix']['true_negatives']}
  False Negatives: {metrics['confusion_matrix']['false_negatives']}

Metrics:
  Accuracy:    {metrics['accuracy']:.2f}%
  Precision:   {metrics['precision']:.2f}%
  Recall:      {metrics['recall']:.2f}%
  F1 Score:    {metrics['f1_score']:.2f}%
  Specificity: {metrics['specificity']:.2f}%
"""
        return summary
        
    def reset(self):
        """Reset all counters."""
        self.true_positives = 0
        self.false_positives = 0
        self.true_negatives = 0
        self.false_negatives = 0
        self.total_predictions = 0
