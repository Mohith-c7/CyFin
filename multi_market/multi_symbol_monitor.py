"""
Multi-Symbol Market Monitor
Monitors multiple stocks simultaneously
"""

from data_stream.data_loader import load_market_data
from ml_models.ensemble_detector import EnsembleDetector
from trust.trust_engine import TrustScoreEngine
from database.db_manager import DatabaseManager


class MultiSymbolMonitor:
    """
    Monitors multiple stock symbols simultaneously.
    
    Provides:
    - Individual symbol monitoring
    - Cross-symbol correlation
    - Market-wide anomaly detection
    """
    
    def __init__(self, symbols, use_database=True):
        """
        Initialize multi-symbol monitor.
        
        Args:
            symbols: List of stock symbols to monitor
            use_database: Whether to use database logging
        """
        self.symbols = symbols
        self.monitors = {}
        self.db = DatabaseManager() if use_database else None
        
        # Create detector and trust engine for each symbol
        for symbol in symbols:
            self.monitors[symbol] = {
                'detector': EnsembleDetector(),
                'trust_engine': TrustScoreEngine(),
                'prices': [],
                'anomalies': 0,
                'last_trust': 100
            }
            
    def add_price(self, symbol, price, timestamp=None):
        """
        Add price for a symbol.
        
        Args:
            symbol: Stock symbol
            price: Current price
            timestamp: Optional timestamp
        """
        if symbol not in self.monitors:
            return
            
        monitor = self.monitors[symbol]
        
        # Store price
        monitor['prices'].append(price)
        
        # Add to detector
        monitor['detector'].add_price(price)
        
        # Log to database
        if self.db:
            self.db.log_market_data(timestamp or 'now', symbol, price)
            
    def detect_anomaly(self, symbol, price, timestamp=None):
        """
        Detect anomaly for a symbol.
        
        Args:
            symbol: Stock symbol
            price: Current price
            timestamp: Optional timestamp
            
        Returns:
            dict: Detection result
        """
        if symbol not in self.monitors:
            return {'error': 'Symbol not monitored'}
            
        monitor = self.monitors[symbol]
        
        # Detect anomaly
        result = monitor['detector'].detect(price)
        
        if result['is_anomaly']:
            monitor['anomalies'] += 1
            
            # Log to database
            if self.db:
                self.db.log_anomaly(
                    timestamp or 'now',
                    symbol,
                    price,
                    result.get('confidence', 0),
                    result['methods']['zscore'].get('z_score', 0),
                    'ensemble',
                    result.get('confidence', 0)
                )
                
        return result
        
    def calculate_trust(self, symbol, anomaly_result):
        """
        Calculate trust score for a symbol.
        
        Args:
            symbol: Stock symbol
            anomaly_result: Result from detect_anomaly
            
        Returns:
            dict: Trust score result
        """
        if symbol not in self.monitors:
            return {'error': 'Symbol not monitored'}
            
        monitor = self.monitors[symbol]
        
        # Calculate trust
        trust_result = monitor['trust_engine'].calculate_trust_score(anomaly_result)
        monitor['last_trust'] = trust_result['trust_score']
        
        # Log to database
        if self.db:
            self.db.log_trust_score(
                'now',
                symbol,
                trust_result['trust_score'],
                trust_result['risk_level']
            )
            
        return trust_result
        
    def get_symbol_stats(self, symbol):
        """Get statistics for a symbol."""
        if symbol not in self.monitors:
            return {'error': 'Symbol not monitored'}
            
        monitor = self.monitors[symbol]
        
        return {
            'symbol': symbol,
            'total_prices': len(monitor['prices']),
            'anomalies_detected': monitor['anomalies'],
            'anomaly_rate': monitor['anomalies'] / len(monitor['prices']) if monitor['prices'] else 0,
            'last_trust_score': monitor['last_trust'],
            'detector_stats': monitor['detector'].get_stats()
        }
        
    def get_all_stats(self):
        """Get statistics for all symbols."""
        return {
            symbol: self.get_symbol_stats(symbol)
            for symbol in self.symbols
        }
        
    def get_market_summary(self):
        """Get overall market summary."""
        total_prices = sum(len(m['prices']) for m in self.monitors.values())
        total_anomalies = sum(m['anomalies'] for m in self.monitors.values())
        avg_trust = sum(m['last_trust'] for m in self.monitors.values()) / len(self.monitors)
        
        return {
            'symbols_monitored': len(self.symbols),
            'total_data_points': total_prices,
            'total_anomalies': total_anomalies,
            'market_anomaly_rate': total_anomalies / total_prices if total_prices > 0 else 0,
            'average_trust_score': avg_trust,
            'symbols': list(self.symbols)
        }
        
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
