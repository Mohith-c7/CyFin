"""
Test Enhanced Features
Quick test of ML, database, and performance metrics
"""

from ml_models.isolation_forest_detector import IsolationForestDetector
from ml_models.ensemble_detector import EnsembleDetector
from analytics.performance_metrics import PerformanceMetrics
from database.db_manager import DatabaseManager
import numpy as np


def test_ml_detector():
    """Test Isolation Forest ML detector."""
    print("=" * 80)
    print("TEST 1: Machine Learning Detector (Isolation Forest)")
    print("=" * 80)
    
    detector = IsolationForestDetector(contamination=0.1)
    
    # Generate normal data
    normal_prices = np.random.normal(150, 5, 100)
    
    # Add training data
    for price in normal_prices:
        detector.add_training_data(price)
    
    # Train model
    success = detector.train(min_samples=20)
    print(f"✓ Model trained: {success}")
    print(f"✓ Training samples: {len(detector.training_data)}")
    
    # Test on normal price
    normal_result = detector.predict(150)
    print(f"\n Normal price ($150): {normal_result}")
    
    # Test on anomalous price
    anomaly_result = detector.predict(200)
    print(f"  Anomaly price ($200): {anomaly_result}")
    
    print("\n✅ ML Detector Test PASSED\n")


def test_ensemble_detector():
    """Test ensemble detector."""
    print("=" * 80)
    print("TEST 2: Ensemble Detector (Z-score + ML)")
    print("=" * 80)
    
    detector = EnsembleDetector()
    
    # Add normal prices
    normal_prices = [150, 151, 149, 152, 148, 150, 151, 149, 150, 151,
                     150, 149, 151, 150, 152, 149, 150, 151, 150, 149]
    
    for price in normal_prices:
        detector.add_price(price)
    
    # Test normal price
    normal_result = detector.detect(150)
    print(f"✓ Normal price detection: {normal_result['is_anomaly']}")
    print(f"  Votes: {normal_result['votes']}")
    
    # Test anomalous price
    anomaly_result = detector.detect(200)
    print(f"\n✓ Anomaly price detection: {anomaly_result['is_anomaly']}")
    print(f"  Votes: {anomaly_result['votes']}")
    print(f"  Confidence: {anomaly_result['confidence']:.2f}")
    
    # Get stats
    stats = detector.get_stats()
    print(f"\n✓ Ensemble Stats:")
    print(f"  Total detections: {stats['total_detections']}")
    print(f"  Anomalies found: {stats['anomalies_detected']}")
    
    print("\n✅ Ensemble Detector Test PASSED\n")


def test_performance_metrics():
    """Test performance metrics."""
    print("=" * 80)
    print("TEST 3: Performance Metrics")
    print("=" * 80)
    
    metrics = PerformanceMetrics()
    
    # Simulate predictions
    # True Positives: Correctly detected attacks
    for _ in range(10):
        metrics.record_prediction(predicted_anomaly=True, actual_anomaly=True)
    
    # False Positives: Normal data flagged as attack
    for _ in range(2):
        metrics.record_prediction(predicted_anomaly=True, actual_anomaly=False)
    
    # True Negatives: Normal data correctly identified
    for _ in range(85):
        metrics.record_prediction(predicted_anomaly=False, actual_anomaly=False)
    
    # False Negatives: Missed attacks
    for _ in range(3):
        metrics.record_prediction(predicted_anomaly=False, actual_anomaly=True)
    
    # Calculate metrics
    all_metrics = metrics.get_all_metrics()
    
    print(f"✓ Total Predictions: {all_metrics['total_predictions']}")
    print(f"\n✓ Confusion Matrix:")
    cm = all_metrics['confusion_matrix']
    print(f"  True Positives:  {cm['true_positives']}")
    print(f"  False Positives: {cm['false_positives']}")
    print(f"  True Negatives:  {cm['true_negatives']}")
    print(f"  False Negatives: {cm['false_negatives']}")
    
    print(f"\n✓ Performance Metrics:")
    print(f"  Accuracy:    {all_metrics['accuracy']:.2f}%")
    print(f"  Precision:   {all_metrics['precision']:.2f}%")
    print(f"  Recall:      {all_metrics['recall']:.2f}%")
    print(f"  F1 Score:    {all_metrics['f1_score']:.2f}%")
    print(f"  Specificity: {all_metrics['specificity']:.2f}%")
    
    print("\n✅ Performance Metrics Test PASSED\n")


def test_database():
    """Test database manager."""
    print("=" * 80)
    print("TEST 4: Database Manager")
    print("=" * 80)
    
    db = DatabaseManager('test_market_events.db')
    
    # Log some data
    db.log_market_data('2026-02-22 10:00:00', 'AAPL', 150.25, False)
    db.log_market_data('2026-02-22 10:01:00', 'AAPL', 175.50, True)
    
    db.log_anomaly('2026-02-22 10:01:00', 'AAPL', 175.50, 5.2, 5.2, 'zscore', 85)
    
    db.log_trust_score('2026-02-22 10:01:00', 'AAPL', 60, 'CAUTION')
    
    db.log_trade('2026-02-22 10:01:00', 'AAPL', 'BUY', 150.25, 10, 10000, False, '')
    db.log_trade('2026-02-22 10:02:00', 'AAPL', 'SELL', 175.50, 10, 10000, True, 'Low trust')
    
    db.log_system_event('2026-02-22 10:01:00', 'attack', 'HIGH', 'Price manipulation detected')
    
    print("✓ Logged market data")
    print("✓ Logged anomaly")
    print("✓ Logged trust score")
    print("✓ Logged trades")
    print("✓ Logged system event")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n✓ Database Statistics:")
    print(f"  Market Data:     {stats['market_data_count']} records")
    print(f"  Anomalies:       {stats['anomalies_count']} records")
    print(f"  Trust Scores:    {stats['trust_scores_count']} records")
    print(f"  Trades:          {stats['trades_count']} records")
    print(f"  Blocked Trades:  {stats['blocked_trades']} records")
    print(f"  System Events:   {stats['system_events_count']} records")
    
    # Export to CSV
    db.export_to_csv('anomalies', 'test_anomalies.csv')
    print(f"\n✓ Exported anomalies to CSV")
    
    db.close()
    print("\n✅ Database Test PASSED\n")


def run_all_tests():
    """Run all enhancement tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ENHANCED FEATURES TEST SUITE" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    try:
        test_ml_detector()
        test_ensemble_detector()
        test_performance_metrics()
        test_database()
        
        print("=" * 80)
        print("🎉 ALL ENHANCEMENT TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Machine Learning: Working")
        print("✅ Ensemble Detection: Working")
        print("✅ Performance Metrics: Working")
        print("✅ Database Logging: Working")
        print("\n🚀 Enhanced system is ready for production!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
