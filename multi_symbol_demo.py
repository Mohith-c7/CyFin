"""
Multi-Symbol Monitoring Demo
Demonstrates monitoring multiple stocks simultaneously
"""

from multi_market.multi_symbol_monitor import MultiSymbolMonitor
from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from attack.attack_engine import AttackEngine
import time


def run_multi_symbol_demo():
    """Run multi-symbol monitoring demonstration."""
    print("=" * 80)
    print("MULTI-SYMBOL MARKET MONITORING DEMO")
    print("=" * 80)
    
    # Symbols to monitor
    symbols = ["AAPL", "MSFT", "GOOGL"]
    print(f"\nMonitoring {len(symbols)} symbols: {', '.join(symbols)}")
    
    # Initialize multi-symbol monitor
    print("\n[1/4] Initializing Multi-Symbol Monitor...")
    monitor = MultiSymbolMonitor(symbols, use_database=True)
    print("✓ Monitor initialized with database logging")
    
    # Load data for each symbol
    print("\n[2/4] Loading Market Data...")
    data_streams = {}
    for symbol in symbols:
        try:
            data = load_market_data(symbol, period="1d", interval="1m")
            data_streams[symbol] = data
            print(f"  ✓ {symbol}: {len(data)} data points")
        except Exception as e:
            print(f"  ✗ {symbol}: Failed to load ({e})")
    
    if not data_streams:
        print("\n❌ No data loaded. Check internet connection.")
        return
    
    # Process data for each symbol
    print("\n[3/4] Processing Market Data...")
    print("-" * 80)
    
    # Use shortest dataset length
    min_length = min(len(data) for data in data_streams.values())
    
    # Create attack engine for AAPL only
    attacker = AttackEngine(attack_step=30, spike_percentage=15)
    
    for step in range(min(min_length, 100)):  # Process first 100 steps
        for symbol in symbols:
            data = data_streams[symbol]
            if step < len(data):
                row = data.iloc[step]
                price = float(row['Close'])
                timestamp = str(row['Datetime'])
                
                # Apply attack only to AAPL
                if symbol == "AAPL":
                    price, is_attacked = attacker.apply_attack(price, step + 1)
                    if is_attacked:
                        print(f"\n🚨 ATTACK on {symbol} at step {step + 1}: ${price:.2f}")
                
                # Add price to monitor
                monitor.add_price(symbol, price, timestamp)
                
                # Detect anomaly
                anomaly_result = monitor.detect_anomaly(symbol, price, timestamp)
                
                # Calculate trust
                trust_result = monitor.calculate_trust(symbol, anomaly_result)
                
                # Report anomalies
                if anomaly_result.get('is_anomaly'):
                    print(f"⚠️  {symbol}: Anomaly detected at ${price:.2f}, "
                          f"Trust={trust_result['trust_score']:.0f}")
        
        # Progress
        if (step + 1) % 25 == 0:
            print(f"  Processed {step + 1} steps across {len(symbols)} symbols...")
    
    print("-" * 80)
    
    # Results
    print("\n[4/4] Multi-Symbol Analysis Results")
    print("=" * 80)
    
    # Market summary
    print("\n📊 Market Summary:")
    summary = monitor.get_market_summary()
    print(f"  Symbols Monitored:    {summary['symbols_monitored']}")
    print(f"  Total Data Points:    {summary['total_data_points']}")
    print(f"  Total Anomalies:      {summary['total_anomalies']}")
    print(f"  Market Anomaly Rate:  {summary['market_anomaly_rate']*100:.2f}%")
    print(f"  Avg Trust Score:      {summary['average_trust_score']:.1f}")
    
    # Individual symbol stats
    print("\n📈 Individual Symbol Statistics:")
    all_stats = monitor.get_all_stats()
    for symbol, stats in all_stats.items():
        print(f"\n  {symbol}:")
        print(f"    Data Points:     {stats['total_prices']}")
        print(f"    Anomalies:       {stats['anomalies_detected']}")
        print(f"    Anomaly Rate:    {stats['anomaly_rate']*100:.2f}%")
        print(f"    Last Trust:      {stats['last_trust_score']:.1f}")
    
    # Database stats
    print("\n💾 Database Statistics:")
    db_stats = monitor.db.get_statistics()
    print(f"  Market Data:      {db_stats['market_data_count']} records")
    print(f"  Anomalies:        {db_stats['anomalies_count']} records")
    print(f"  Trust Scores:     {db_stats['trust_scores_count']} records")
    
    print("\n" + "=" * 80)
    print("✅ Multi-Symbol Demo Complete!")
    print("\n💡 Key Insights:")
    print("  • System can monitor multiple stocks simultaneously")
    print("  • Each symbol has independent detection and trust scoring")
    print("  • Database logs all events across all symbols")
    print("  • Scalable architecture for market-wide monitoring")
    print("\n" + "=" * 80)
    
    # Cleanup
    monitor.close()


if __name__ == "__main__":
    run_multi_symbol_demo()
