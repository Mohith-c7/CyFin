"""
Setup verification script
Checks if all dependencies are installed correctly
"""

import sys

print("=" * 70)
print("SETUP VERIFICATION")
print("=" * 70)

# Check Python version
print(f"\nPython Version: {sys.version}")
if sys.version_info < (3, 9):
    print("⚠️  Warning: Python 3.9+ recommended")
else:
    print("✓ Python version OK")

# Check required packages
required_packages = [
    'pandas',
    'numpy',
    'yfinance',
    'sklearn',
    'streamlit',
    'plotly'
]

print("\nChecking required packages...")
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} - NOT INSTALLED")
        missing_packages.append(package)

print("\n" + "=" * 70)

if missing_packages:
    print("❌ SETUP INCOMPLETE")
    print("\nMissing packages:", ", ".join(missing_packages))
    print("\nTo install all dependencies, run:")
    print("  pip install -r requirements.txt")
else:
    print("✅ ALL DEPENDENCIES INSTALLED")
    print("\nYou can now run:")
    print("  python main_system_demo.py")
    print("  or")
    print("  streamlit run dashboard/dashboard_app.py")

print("=" * 70)
