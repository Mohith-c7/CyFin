"""
Anomaly Detection Configuration Module
Defines parameters for real-time anomaly detection
"""

# Rolling window size for statistical analysis
WINDOW_SIZE = 20

# Z-score threshold for anomaly detection
# |z| > 3 indicates anomaly (99.7% confidence)
Z_THRESHOLD = 3
