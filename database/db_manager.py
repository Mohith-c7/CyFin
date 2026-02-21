"""
Database Manager for Event Persistence
Stores all system events in SQLite database
"""

import sqlite3
import json
from datetime import datetime
import os


class DatabaseManager:
    """
    Manages SQLite database for storing market events, anomalies, and trades.
    """
    
    def __init__(self, db_path='market_events.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
    def create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                is_attacked INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Anomaly detection table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                severity REAL,
                z_score REAL,
                detection_method TEXT,
                confidence REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trust scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trust_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                trust_score REAL NOT NULL,
                risk_level TEXT,
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trading activity table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER,
                portfolio_value REAL,
                was_blocked INTEGER DEFAULT 0,
                block_reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT,
                message TEXT,
                data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def log_market_data(self, timestamp, symbol, price, is_attacked=False):
        """Log market data point."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO market_data (timestamp, symbol, price, is_attacked)
            VALUES (?, ?, ?, ?)
        ''', (str(timestamp), symbol, price, 1 if is_attacked else 0))
        self.conn.commit()
        return cursor.lastrowid
        
    def log_anomaly(self, timestamp, symbol, price, severity, z_score, 
                    detection_method='zscore', confidence=0):
        """Log detected anomaly."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO anomalies (timestamp, symbol, price, severity, z_score, 
                                 detection_method, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(timestamp), symbol, price, severity, z_score, 
              detection_method, confidence))
        self.conn.commit()
        return cursor.lastrowid
        
    def log_trust_score(self, timestamp, symbol, trust_score, risk_level, reason=''):
        """Log trust score evaluation."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trust_scores (timestamp, symbol, trust_score, risk_level, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(timestamp), symbol, trust_score, risk_level, reason))
        self.conn.commit()
        return cursor.lastrowid
        
    def log_trade(self, timestamp, symbol, action, price, quantity=0, 
                  portfolio_value=0, was_blocked=False, block_reason=''):
        """Log trading activity."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (timestamp, symbol, action, price, quantity, 
                              portfolio_value, was_blocked, block_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (str(timestamp), symbol, action, price, quantity, portfolio_value,
              1 if was_blocked else 0, block_reason))
        self.conn.commit()
        return cursor.lastrowid
        
    def log_system_event(self, timestamp, event_type, severity, message, data=None):
        """Log general system event."""
        cursor = self.conn.cursor()
        data_json = json.dumps(data) if data else None
        cursor.execute('''
            INSERT INTO system_events (timestamp, event_type, severity, message, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(timestamp), event_type, severity, message, data_json))
        self.conn.commit()
        return cursor.lastrowid
        
    def get_anomaly_count(self):
        """Get total anomaly count."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM anomalies')
        return cursor.fetchone()['count']
        
    def get_trade_count(self):
        """Get total trade count."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM trades')
        return cursor.fetchone()['count']
        
    def get_blocked_trade_count(self):
        """Get blocked trade count."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM trades WHERE was_blocked = 1')
        return cursor.fetchone()['count']
        
    def get_recent_anomalies(self, limit=10):
        """Get recent anomalies."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM anomalies 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
        
    def get_statistics(self):
        """Get comprehensive database statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Count records in each table
        for table in ['market_data', 'anomalies', 'trust_scores', 'trades', 'system_events']:
            cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
            stats[f'{table}_count'] = cursor.fetchone()['count']
            
        # Blocked trades
        cursor.execute('SELECT COUNT(*) as count FROM trades WHERE was_blocked = 1')
        stats['blocked_trades'] = cursor.fetchone()['count']
        
        # Average trust score
        cursor.execute('SELECT AVG(trust_score) as avg FROM trust_scores')
        result = cursor.fetchone()
        stats['avg_trust_score'] = result['avg'] if result['avg'] else 0
        
        return stats
        
    def export_to_csv(self, table_name, output_path):
        """Export table to CSV file."""
        import pandas as pd
        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(output_path, index=False)
        return output_path
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
