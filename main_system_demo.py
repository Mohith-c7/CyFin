"""
Main System Demonstration
Complete end-to-end demonstration of the Market Data Integrity System
"""

import sys
sys.path.append('integrated_system')

from integrated_system.system_runner import SystemRunner


def main():
    """Run the complete system demonstration."""
    print("\n" + "=" * 90)
    print("MARKET DATA INTEGRITY MONITORING & PROTECTION SYSTEM")
    print("Complete System Demonstration")
    print("=" * 90)
    print("\nThis demonstration will:")
    print("  1. Stream real market data (AAPL)")
    print("  2. Inject simulated data manipulation attacks")
    print("  3. Detect anomalies in real-time")
    print("  4. Calculate trust scores")
    print("  5. Execute or block trades based on data integrity")
    print("  6. Show complete performance summary")
    print("\nPress Ctrl+C to stop at any time\n")
    
    try:
        # Run with attacks (default demonstration mode)
        runner = SystemRunner(
            symbol="AAPL",
            period="1d",
            interval="1m",
            delay=0.3,
            inject_attacks=True,
            attack_probability=0.15,
            attack_type="spike"
        )
        
        runner.run()
        
        print("\n✓ COMPLETE SYSTEM DEMONSTRATION SUCCESSFUL")
        print("\nThe system successfully:")
        print("  ✓ Monitored market data in real-time")
        print("  ✓ Detected manipulated data")
        print("  ✓ Protected trading decisions")
        print("  ✓ Maintained system integrity")
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure:")
        print("  - All dependencies are installed (pip install -r requirements.txt)")
        print("  - Internet connection is available")
        print("  - Market data is accessible")


if __name__ == "__main__":
    main()
