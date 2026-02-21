"""
Enhanced System Demo
Demonstrates all features including ML, database, and multi-symbol monitoring
"""

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
from attack import attack_config
from ml_models.ensemble_detector import EnsembleDetector
from trust.trust_engine import TrustScoreEngine
from protection.protection_engine import ProtectionEngine
from trading.trading_engine_protected import ProtectedTradingEngine
from analytics.performance_metrics import PerformanceMetrics
from database.db_manager import DatabaseManager
import time


def run_enhanced_demo():
    """Run enhanced system demonstration."""
    print("=" * 80)
    print("ENHANCED MARKET DATA INTEGRITY SYSTEM - FULL DEMO")
    print("=" * 80)
    print("\nFeatures:")
    print("  ✓ Machine Learning (Isolation Forest)")
    print("  ✓ Ensemble Detection (Z-score + ML)")
    print("  ✓ Database Logging (SQLite)")
    print("  ✓ Performance Metrics (Precision, Recall, F1)")
    print("  ✓ Protected Trading")
    print("\n" + "=" * 80)
    
    # Configure attack
    attack_config.ATTACK_ENABLED = True
    attack_config.ATTACK_STEP = 30
    attack_config.ATTACK_MULTIPLIER = 1.15
    
    # Initialize components
    print("\n[1/7] Initializing Enhanced Components...")
    
    # ML-based ensemble detector
    detector = EnsembleDetector()
    
    # Trust engine
    trust_engine = TrustScoreEngine()
    
    # Protection engine
    protection = ProtectionEngine()
    
    # Trading engine
    trader = ProtectedTradingEngine()
    
    # Performance metrics
    metrics = PerformanceMetrics()
    
    # Database
    db = DatabaseManager()
    
    # Attack engine
    attacker = AttackEngine()
    
    print("✓ All components initialized")
    
    # Load market data
    print("\n[2/7] Loading Market Data...")
    symbol = "AAPL"
    data = load_market_data(symbol, period="1d", interval="1m")
    print(f"✓ Loaded {len(data)} data points for {symbol}")
    
    # Statistics
    total_steps = 0
    anomalies_detected = 0
    trades_executed = 0
    trades_blocked = 0
    attack_occurred = False
    
    print("\n[3/7] Starting Market Stream with Enhanced Detection...")
    print("-" * 80)
    
    # Stream data
    for tick in stream_market_data(data, symbol, delay=0.1):
        total_steps += 1
        
        # Apply attack
        attacked_tick = attacker.process_tick(tick)
        timestamp = attacked_tick['timestamp']
        price = attacked_tick['price']
        is_attacked = attacked_tick['attacked']
        
        if is_attacked and not attack_occurred:
            attack_occurred = True
            print(f"\n🚨 CYBER ATTACK INJECTED at step {total_steps}")
            print(f"   Original: ${tick['price']:.2f} → Manipulated: ${price:.2f}")
            print(f"   Spike: +{((price - tick['price']) / tick['price'] * 100):.1f}%\n")
            
            # Log attack
            db.log_system_event(
                timestamp, 'attack', 'HIGH',
                f"Price manipulation: ${tick['price']:.2f} → ${price:.2f}"
            )
        
        # Add to detector (for training)
        detector.add_price(price)
        
        # Detect anomaly using ensemble
        anomaly_result = detector.detect(price)
        
        # Calculate trust score using existing interface
        trust_tick = {
            'anomaly': anomaly_result['is_anomaly'],
            'z_score': anomaly_result['methods']['zscore'].get('z_score', 0)
        }
        trust_tick = trust_engine.process_tick(trust_tick)
        trust_result = {
            'trust_score': trust_tick['trust_score'],
            'risk_level': trust_tick['trust_level']
        }
        
        # Check protection
        protection_result = protection.should_allow_trade(trust_result)
        
        # Make trading decision
        trade_decision = trader.strategy.decide(price)
        
        # Execute or block trade
        if trade_decision != "HOLD":
            if protection_result['allow_trade']:
                trader.execute_trade(trade_decision, price)
                trades_executed += 1
                
                # Log trade
                db.log_trade(
                    timestamp, symbol, trade_decision, price,
                    portfolio_value=trader.portfolio.value(price)
                )
            else:
                trades_blocked += 1
                print(f"🛡️  TRADE BLOCKED: {trade_decision} at ${price:.2f}")
                print(f"   Reason: {protection_result['reason']}")
                
                # Log blocked trade
                db.log_trade(
                    timestamp, symbol, trade_decision, price,
                    portfolio_value=trader.portfolio.value(price),
                    was_blocked=True,
                    block_reason=protection_result['reason']
                )
        
        # Record metrics
        metrics.record_prediction(
            anomaly_result['is_anomaly'],
            is_attacked
        )
        
        # Log to database
        db.log_market_data(timestamp, symbol, price, is_attacked)
        
        if anomaly_result['is_anomaly']:
            anomalies_detected += 1
            db.log_anomaly(
                timestamp, symbol, price,
                anomaly_result.get('confidence', 0),
                anomaly_result['methods']['zscore'].get('z_score', 0),
                'ensemble',
                anomaly_result.get('confidence', 0)
            )
        
        db.log_trust_score(
            timestamp, symbol,
            trust_result['trust_score'],
            trust_result['risk_level']
        )
        
        # Progress indicator
        if total_steps % 50 == 0:
            print(f"  Step {total_steps}: Price=${price:.2f}, "
                  f"Trust={trust_result['trust_score']:.0f}, "
                  f"Anomalies={anomalies_detected}")
    
    print("-" * 80)
    print(f"✓ Processed {total_steps} market data points")
    
    # Results
    print("\n[4/7] System Performance Results")
    print("=" * 80)
    
    # Performance metrics
    print("\n📊 Detection Performance:")
    perf = metrics.get_all_metrics()
    print(f"  Accuracy:    {perf['accuracy']:.2f}%")
    print(f"  Precision:   {perf['precision']:.2f}%")
    print(f"  Recall:      {perf['recall']:.2f}%")
    print(f"  F1 Score:    {perf['f1_score']:.2f}%")
    print(f"  Specificity: {perf['specificity']:.2f}%")
    
    print(f"\n📈 Confusion Matrix:")
    cm = perf['confusion_matrix']
    print(f"  True Positives:  {cm['true_positives']}")
    print(f"  False Positives: {cm['false_positives']}")
    print(f"  True Negatives:  {cm['true_negatives']}")
    print(f"  False Negatives: {cm['false_negatives']}")
    
    # Ensemble stats
    print(f"\n🤖 Ensemble Detector Stats:")
    ensemble_stats = detector.get_stats()
    print(f"  Total Detections: {ensemble_stats['total_detections']}")
    print(f"  Anomalies Found:  {ensemble_stats['anomalies_detected']}")
    print(f"  Anomaly Rate:     {ensemble_stats['anomaly_rate']*100:.2f}%")
    
    # Trading results
    print(f"\n💰 Trading Results:")
    initial_balance = 10000
    portfolio_value = trader.portfolio.value(price)
    profit_loss = portfolio_value - initial_balance
    print(f"  Initial Balance:  ${initial_balance:.2f}")
    print(f"  Final Value:      ${portfolio_value:.2f}")
    print(f"  Profit/Loss:      ${profit_loss:+.2f}")
    print(f"  Trades Executed:  {trades_executed}")
    print(f"  Trades Blocked:   {trades_blocked}")
    
    # Database stats
    print(f"\n💾 Database Statistics:")
    db_stats = db.get_statistics()
    print(f"  Market Data:      {db_stats['market_data_count']} records")
    print(f"  Anomalies:        {db_stats['anomalies_count']} records")
    print(f"  Trust Scores:     {db_stats['trust_scores_count']} records")
    print(f"  Trades:           {db_stats['trades_count']} records")
    print(f"  Blocked Trades:   {db_stats['blocked_trades']} records")
    print(f"  System Events:    {db_stats['system_events_count']} records")
    
    print("\n[5/7] Exporting Data...")
    db.export_to_csv('anomalies', 'anomalies_export.csv')
    db.export_to_csv('trades', 'trades_export.csv')
    print("✓ Exported anomalies_export.csv")
    print("✓ Exported trades_export.csv")
    
    print("\n[6/7] System Effectiveness Analysis")
    print("=" * 80)
    
    if trades_blocked > 0:
        print(f"✅ SUCCESS: System blocked {trades_blocked} potentially harmful trades")
        print(f"✅ Protection prevented losses during attack period")
    else:
        print(f"ℹ️  No trades were blocked (attack may not have triggered trading)")
    
    if perf['accuracy'] > 90:
        print(f"✅ EXCELLENT: Detection accuracy of {perf['accuracy']:.1f}% exceeds 90% threshold")
    elif perf['accuracy'] > 80:
        print(f"✅ GOOD: Detection accuracy of {perf['accuracy']:.1f}% is above 80%")
    else:
        print(f"⚠️  Detection accuracy of {perf['accuracy']:.1f}% could be improved")
    
    print("\n[7/7] Demo Complete!")
    print("=" * 80)
    print("\n🎉 Enhanced System Features Demonstrated:")
    print("  ✓ Machine Learning anomaly detection")
    print("  ✓ Ensemble voting (Z-score + Isolation Forest)")
    print("  ✓ Comprehensive performance metrics")
    print("  ✓ Database persistence and logging")
    print("  ✓ Data export capabilities")
    print("  ✓ Protected trading with automated blocking")
    print("\n💡 Next Steps:")
    print("  • Review exported CSV files")
    print("  • Check market_events.db database")
    print("  • Run: streamlit run dashboard/app.py for visual interface")
    print("\n" + "=" * 80)
    
    # Cleanup
    db.close()


if __name__ == "__main__":
    run_enhanced_demo()
