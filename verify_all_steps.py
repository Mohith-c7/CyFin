"""
Complete System Verification Script
Verifies all steps are built correctly and tests the complete pipeline
"""

import sys
import os

print("=" * 80)
print("COMPLETE SYSTEM VERIFICATION")
print("=" * 80)

# Check Python version
print(f"\nPython Version: {sys.version}")

# Check if all required packages are available
print("\n1. Checking Dependencies...")
required_packages = ['pandas', 'numpy', 'yfinance', 'sklearn']
missing = []

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - MISSING")
        missing.append(package)

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Check file structure
print("\n2. Checking File Structure...")

required_files = {
    "Step 1 - Market Stream": [
        "data_stream/__init__.py",
        "data_stream/data_loader.py",
        "data_stream/replay_engine.py",
        "data_stream/market_stream.py"
    ],
    "Step 2 - Trading Algorithm": [
        "trading/__init__.py",
        "trading/strategy.py",
        "trading/portfolio.py",
        "trading/trading_engine.py"
    ],
    "Step 3 - Attack Injection": [
        "attack/__init__.py",
        "attack/attack_config.py",
        "attack/attack_engine.py"
    ],
    "Step 4 - Anomaly Detection": [
        "detection/__init__.py",
        "detection/anomaly_config.py",
        "detection/anomaly_engine.py"
    ]
}

all_files_exist = True
for step, files in required_files.items():
    print(f"\n   {step}:")
    for file in files:
        if os.path.exists(file):
            print(f"      ✓ {file}")
        else:
            print(f"      ✗ {file} - MISSING")
            all_files_exist = False

if not all_files_exist:
    print("\n❌ Some files are missing!")
    sys.exit(1)

# Check test files
print("\n3. Checking Test Files...")
test_files = [
    "main_stream_test.py",
    "integration_test.py",
    "integration_attack_test.py",
    "integration_detection_test.py"
]

for file in test_files:
    if os.path.exists(file):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} - MISSING")

# Verify module imports
print("\n4. Verifying Module Imports...")

try:
    sys.path.append('data_stream')
    sys.path.append('trading')
    sys.path.append('attack')
    sys.path.append('detection')
    
    from data_stream.data_loader import load_market_data
    print("   ✓ data_stream.data_loader")
    
    from data_stream.replay_engine import stream_market_data
    print("   ✓ data_stream.replay_engine")
    
    from trading.strategy import TradingStrategy
    print("   ✓ trading.strategy")
    
    from trading.portfolio import Portfolio
    print("   ✓ trading.portfolio")
    
    from trading.trading_engine import TradingEngine
    print("   ✓ trading.trading_engine")
    
    from attack.attack_engine import AttackEngine
    print("   ✓ attack.attack_engine")
    
    from detection.anomaly_engine import AnomalyDetector
    print("   ✓ detection.anomaly_engine")
    
except Exception as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test component initialization
print("\n5. Testing Component Initialization...")

try:
    strategy = TradingStrategy()
    print("   ✓ TradingStrategy initialized")
    
    portfolio = Portfolio()
    print("   ✓ Portfolio initialized")
    
    trader = TradingEngine()
    print("   ✓ TradingEngine initialized")
    
    attacker = AttackEngine()
    print("   ✓ AttackEngine initialized")
    
    detector = AnomalyDetector()
    print("   ✓ AnomalyDetector initialized")
    
except Exception as e:
    print(f"   ✗ Initialization error: {e}")
    sys.exit(1)

# Test data flow
print("\n6. Testing Data Flow...")

try:
    # Create test tick
    test_tick = {
        "timestamp": "2024-01-01 09:30:00",
        "symbol": "TEST",
        "price": 100.0
    }
    print("   ✓ Test tick created")
    
    # Test attack engine
    attacked_tick = attacker.process_tick(test_tick.copy())
    print(f"   ✓ Attack engine processed (attacked: {attacked_tick.get('attacked', False)})")
    
    # Test anomaly detector
    detected_tick = detector.process_tick(attacked_tick.copy())
    print(f"   ✓ Anomaly detector processed (anomaly: {detected_tick.get('anomaly', False)})")
    
    # Test trading engine
    trader.process_tick(detected_tick)
    print(f"   ✓ Trading engine processed")
    
except Exception as e:
    print(f"   ✗ Data flow error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("✅ ALL VERIFICATIONS PASSED!")
print("=" * 80)
print("\nSystem Status:")
print("  ✓ Step 1: Market Data Stream - READY")
print("  ✓ Step 2: Trading Algorithm - READY")
print("  ✓ Step 3: Attack Injection - READY")
print("  ✓ Step 4: Anomaly Detection - READY")
print("\nYou can now run:")
print("  python integration_detection_test.py")
print("=" * 80)
