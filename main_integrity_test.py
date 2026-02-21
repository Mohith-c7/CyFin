"""
Main test file for Step 3 - Integrity Monitoring System
Tests anomaly detection and trust scoring with simulated attacks
"""

import sys
sys.path.append('data_stream')
sys.path.append('integrity_monitor')

from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from integrity_monitor.integrity_monitor import IntegrityMonitor
from integrity_monitor.data_manipulator import DataManipulator


def run_integrity_test(inject_attacks=True):
    """
    Run integrity monitoring test.
    
    Args:
        inject_attacks: Whether to inject simulated attacks
    """
    print("=" * 80)
    print("INTEGRITY MONITORING SYSTEM - STEP 3")
    print("=" * 80)
    
    # Configuration
    SYMBOL = "AAPL"
    PERIOD = "1d"
    INTERVAL = "1m"
    DELAY = 0.3
    
    # Initialize components
    monitor = IntegrityMonitor(
        window_size=20,
        contamination=0.1,
        initial_trust=100.0,
        decay_rate=15.0,
        recovery_rate=3.0
    )
    
    manipulator = None
    if inject_attacks:
        manipulator = DataManipulator(
            attack_probability=0.15,  # 15% chance of attack per tick
            attack_type="spike"
        )
        print("⚠️  ATTACK MODE ENABLED - Injecting manipulated data")
    else:
        print("✓ NORMAL MODE - Clean data only")
    
    print(f"Symbol: {SYMBOL}")
    print(f"Monitoring Window: {monitor.anomaly_detector.window_size} ticks")
    print("-" * 80)
    
    try:
        # Load market data
        data = load_market_data(SYMBOL, PERIOD, INTERVAL)
        
        tick_count = 0
        for tick in stream_market_data(data, SYMBOL, DELAY):
            tick_count += 1
            
            # Potentially manipulate data
            if manipulator:
                tick, was_attacked = manipulator.manipulate(tick)
            else:
                was_attacked = False
            
            # Validate through integrity monitor
            validation = monitor.validate_tick(tick)
            
            # Display results
            _display_validation(validation, tick_count, was_attacked)
            
            # Alert on critical trust
            if validation["trust_level"] == "CRITICAL":
                print("\n" + "!" * 80)
                print("🚨 CRITICAL ALERT: Trust score critically low - HALT TRADING")
                print("!" * 80 + "\n")
        
        # Final summary
        _display_summary(monitor, manipulator)
        
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
        _display_summary(monitor, manipulator)
    except Exception as e:
        print(f"\nError: {e}")
        raise


def _display_validation(validation, tick_count, was_attacked):
    """Display validation results."""
    # Status indicator
    if validation["is_anomaly"]:
        status = "🔴 ANOMALY"
    else:
        status = "🟢 NORMAL "
    
    # Trust indicator
    trust_level = validation["trust_level"]
    trust_icons = {
        "HIGH": "🟢",
        "MEDIUM": "🟡",
        "LOW": "🟠",
        "CRITICAL": "🔴"
    }
    trust_icon = trust_icons.get(trust_level, "⚪")
    
    # Attack indicator
    attack_marker = " [INJECTED ATTACK]" if was_attacked else ""
    
    print(f"\nTick #{tick_count}{attack_marker}")
    print(f"  {status} | Price: ${validation['price']:.2f} | Z-Score: {validation['z_score']}")
    print(f"  {trust_icon} Trust: {validation['trust_score']:.1f} ({trust_level}) | {validation['recommendation']}")
    
    if validation["is_anomaly"]:
        print(f"  ⚠️  Anomaly detected! Confidence: {validation['anomaly_confidence']:.2%}")


def _display_summary(monitor, manipulator):
    """Display final summary."""
    summary = monitor.get_summary()
    
    print("\n" + "=" * 80)
    print("INTEGRITY MONITORING SUMMARY")
    print("=" * 80)
    print(f"Final Trust Score: {summary['trust_score']:.2f}/100")
    print(f"Total Ticks Processed: {summary['total_ticks']}")
    print(f"Anomalies Detected: {summary['total_anomalies']}")
    print(f"Anomaly Rate: {summary['anomaly_rate']:.2f}%")
    
    if manipulator:
        attack_stats = manipulator.get_stats()
        print(f"\nAttack Statistics:")
        print(f"  Attacks Injected: {attack_stats['attack_count']}")
        print(f"  Attack Type: {attack_stats['attack_type']}")
        print(f"  Attack Probability: {attack_stats['attack_probability']:.1%}")
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    # Check command line argument
    inject_attacks = True
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        inject_attacks = False
    
    print("Testing Integrity Monitoring System...")
    print("Use --clean flag to test without attacks\n")
    
    try:
        run_integrity_test(inject_attacks)
        print("\n✓ STEP 3 COMPLETE - Integrity monitoring working successfully")
    except Exception as e:
        print(f"\n✗ Error: {e}")
