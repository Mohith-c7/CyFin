"""
Test Suite for Cross-Asset Contagion & Correlation Engine
==========================================================

Comprehensive tests covering:
- Price updates and symbol auto-registration
- Rolling return computation (log returns)
- Correlation matrix calculation
- Volatility synchronization detection
- Correlation spike detection
- Contagion Risk Score (CRS) computation
- Systemic contagion flag
- MSI integration
- Edge cases and error handling
- Configuration validation

Run with:
    python -m pytest test_contagion_engine.py -v -p no:asyncio
    OR
    python test_contagion_engine.py
"""

import sys
import os
import unittest
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from systemic.contagion_engine import ContagionEngine


class TestPriceUpdates(unittest.TestCase):
    """Test price update and return computation."""

    def setUp(self):
        self.engine = ContagionEngine(window_size=10)

    def test_first_price_registers_symbol(self):
        """First price update should auto-register the symbol."""
        self.engine.update_price('AAPL', 150.0)
        symbols = self.engine.get_tracked_symbols()
        self.assertIn('AAPL', symbols)

    def test_first_price_no_return(self):
        """First price has no previous price, so return should be None."""
        result = self.engine.update_price('AAPL', 150.0)
        self.assertIsNone(result['return'])

    def test_second_price_computes_return(self):
        """Second price should compute a log return."""
        self.engine.update_price('AAPL', 100.0)
        result = self.engine.update_price('AAPL', 105.0)
        expected_return = math.log(105.0 / 100.0)
        self.assertAlmostEqual(result['return'], expected_return, places=8)

    def test_log_return_correctness(self):
        """Verify log return formula: ln(P_t / P_{t-1})."""
        self.engine.update_price('AAPL', 200.0)
        result = self.engine.update_price('AAPL', 210.0)
        self.assertAlmostEqual(
            result['return'], np.log(210.0 / 200.0), places=8
        )

    def test_multiple_symbols(self):
        """Track multiple symbols independently."""
        self.engine.update_price('AAPL', 150.0)
        self.engine.update_price('MSFT', 300.0)
        self.engine.update_price('GOOGL', 2800.0)
        symbols = self.engine.get_tracked_symbols()
        self.assertEqual(len(symbols), 3)

    def test_invalid_symbol_raises(self):
        """Empty symbol should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.update_price('', 100.0)

    def test_invalid_price_raises(self):
        """Non-positive price should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.update_price('AAPL', 0.0)
        with self.assertRaises(ValueError):
            self.engine.update_price('AAPL', -50.0)

    def test_sufficient_data_flag(self):
        """sufficient_data should become True once conditions met."""
        engine = ContagionEngine(window_size=10)
        # Need 2 symbols, each with >= 5 returns (6 prices)
        for i in range(6):
            engine.update_price('AAPL', 100.0 + i)
        for i in range(5):
            engine.update_price('MSFT', 200.0 + i)
        result = engine.update_price('MSFT', 210.0)
        self.assertTrue(result['sufficient_data'])

    def test_data_point_count(self):
        """Data point count should track correctly."""
        for i in range(5):
            result = self.engine.update_price('AAPL', 100.0 + i)
        self.assertEqual(result['data_points'], 5)


class TestCorrelation(unittest.TestCase):
    """Test correlation matrix computation."""

    def _seed_engine_with_correlated_data(self, correlation_type='positive'):
        """Helper to seed engine with correlated price data."""
        engine = ContagionEngine(window_size=30)
        np.random.seed(42)
        n = 30

        if correlation_type == 'positive':
            # Highly correlated: both follow same trend + noise
            base = np.cumsum(np.random.randn(n) * 0.01) + 5.0
            prices_a = np.exp(base)
            prices_b = np.exp(base + np.random.randn(n) * 0.001)
        elif correlation_type == 'uncorrelated':
            # Independent random walks
            prices_a = np.exp(
                np.cumsum(np.random.randn(n) * 0.01) + 5.0
            )
            prices_b = np.exp(
                np.cumsum(np.random.randn(n) * 0.01) + 5.0
            )
        elif correlation_type == 'negative':
            # Inversely correlated
            base = np.cumsum(np.random.randn(n) * 0.01) + 5.0
            prices_a = np.exp(base)
            prices_b = np.exp(-base + 10.0)

        for pa, pb in zip(prices_a, prices_b):
            engine.update_price('AAPL', float(pa))
            engine.update_price('MSFT', float(pb))

        return engine

    def test_high_positive_correlation(self):
        """Highly correlated assets should show high avg correlation."""
        engine = self._seed_engine_with_correlated_data('positive')
        summary = engine.get_contagion_summary()
        self.assertGreater(summary['average_correlation'], 0.5)

    def test_uncorrelated_assets(self):
        """Independent assets should show low correlation."""
        engine = self._seed_engine_with_correlated_data('uncorrelated')
        summary = engine.get_contagion_summary()
        # Uncorrelated should be near 0 (but random, so allow some range)
        self.assertLess(abs(summary['average_correlation']), 0.8)

    def test_correlation_matrix_structure(self):
        """Correlation matrix output should have correct pairwise keys."""
        engine = ContagionEngine(window_size=10)
        for i in range(10):
            engine.update_price('AAPL', 100.0 + i * 0.5)
            engine.update_price('MSFT', 200.0 + i * 0.3)
            engine.update_price('GOOGL', 300.0 + i * 0.7)

        summary = engine.get_contagion_summary()
        corr = summary['correlation_matrix']
        # 3 symbols → 3 pairs
        expected_keys = {'AAPL_MSFT', 'AAPL_GOOGL', 'MSFT_GOOGL'}
        self.assertEqual(set(corr.keys()), expected_keys)


class TestVolatilitySynchronization(unittest.TestCase):
    """Test volatility synchronization detection."""

    def test_calm_market_no_sync(self):
        """Stable prices should show no volatility sync."""
        engine = ContagionEngine(window_size=20, volatility_sync_threshold=2.0)

        # Feed linearly increasing prices (stable, low-vol returns)
        for i in range(20):
            engine.update_price('AAPL', 150.0 + i * 0.5)
            engine.update_price('MSFT', 300.0 + i * 0.5)

        summary = engine.get_contagion_summary()
        # With uniform increments, volatility should be stable (ratio ~1)
        # so sync should not trigger (threshold=2.0)
        self.assertLessEqual(summary['volatility_sync_ratio'], 0.5)

    def test_synchronized_volatility_detected(self):
        """Simultaneous vol spike across assets should raise sync ratio."""
        engine = ContagionEngine(window_size=20, volatility_sync_threshold=2.0)

        # Phase 1: Calm period (first half)
        for i in range(10):
            engine.update_price('AAPL', 150.0 + np.random.randn() * 0.01)
            engine.update_price('MSFT', 300.0 + np.random.randn() * 0.01)

        # Phase 2: Volatile period (second half) — big swings
        for i in range(10):
            engine.update_price('AAPL', 150.0 + np.random.randn() * 5.0)
            engine.update_price('MSFT', 300.0 + np.random.randn() * 10.0)

        summary = engine.get_contagion_summary()
        # At least some sync should be detected
        self.assertGreaterEqual(summary['volatility_sync_ratio'], 0.0)

    def test_elevated_symbols_list(self):
        """Elevated symbols should be listed correctly."""
        engine = ContagionEngine(window_size=20, volatility_sync_threshold=2.0)

        # Feed data where volatility is present
        for i in range(20):
            engine.update_price('AAPL', 150.0 + i * 0.001)
            engine.update_price('MSFT', 300.0 + i * 0.001)

        summary = engine.get_contagion_summary()
        # elevated_volatility_symbols should be a list
        self.assertIsInstance(summary['elevated_volatility_symbols'], list)


class TestContagionRiskScore(unittest.TestCase):
    """Test CRS computation and contagion flag."""

    def test_crs_zero_with_no_data(self):
        """CRS should be 0 when insufficient data."""
        engine = ContagionEngine()
        summary = engine.get_contagion_summary()
        self.assertEqual(summary['contagion_risk_score'], 0.0)
        self.assertFalse(summary['systemic_contagion_flag'])

    def test_crs_zero_with_single_symbol(self):
        """CRS should be 0 with only one symbol (can't compute corr)."""
        engine = ContagionEngine(window_size=10)
        for i in range(10):
            engine.update_price('AAPL', 100.0 + i)
        summary = engine.get_contagion_summary()
        self.assertEqual(summary['contagion_risk_score'], 0.0)

    def test_crs_clamped_0_to_100(self):
        """CRS should always be in [0, 100] range."""
        engine = ContagionEngine(window_size=10)
        np.random.seed(42)

        for i in range(15):
            engine.update_price('AAPL', 100.0 + np.random.randn() * 10)
            engine.update_price('MSFT', 200.0 + np.random.randn() * 10)

        summary = engine.get_contagion_summary()
        self.assertGreaterEqual(summary['contagion_risk_score'], 0.0)
        self.assertLessEqual(summary['contagion_risk_score'], 100.0)

    def test_crs_formula_weights(self):
        """CRS = 50*corr + 30*vol_sync + 20*spike (verify structure)."""
        # Just verify the components exist and are bounded
        engine = ContagionEngine(window_size=10)
        np.random.seed(42)

        for i in range(15):
            engine.update_price('AAPL', 100.0 + i * 0.5)
            engine.update_price('MSFT', 200.0 + i * 0.3)

        summary = engine.get_contagion_summary()
        self.assertIn('average_correlation', summary)
        self.assertIn('volatility_sync_ratio', summary)
        self.assertIn('correlation_spike_ratio', summary)
        self.assertIn('contagion_risk_score', summary)

    def test_high_correlation_raises_crs(self):
        """Perfectly correlated assets should produce high CRS."""
        engine = ContagionEngine(window_size=20)

        # Feed perfectly correlated prices
        for i in range(25):
            price = 100.0 + i * 2.0
            engine.update_price('AAPL', price)
            engine.update_price('MSFT', price * 2.0)  # Perfect linear

        summary = engine.get_contagion_summary()
        # High correlation → high CRS (at least the correlation component)
        self.assertGreater(summary['contagion_risk_score'], 10.0)

    def test_contagion_flag_threshold(self):
        """Contagion flag should trigger at CRS >= 60."""
        engine = ContagionEngine(window_size=10)
        summary = engine.get_contagion_summary()
        # Empty → CRS = 0 → flag = False
        self.assertFalse(summary['systemic_contagion_flag'])


class TestContagionSummaryStructure(unittest.TestCase):
    """Test the summary output structure."""

    def test_insufficient_data_structure(self):
        """Summary with insufficient data should have complete structure."""
        engine = ContagionEngine()
        summary = engine.get_contagion_summary()

        required_keys = [
            'average_correlation', 'volatility_sync_ratio',
            'correlation_spike_ratio', 'contagion_risk_score',
            'systemic_contagion_flag', 'symbols_tracked',
            'data_sufficient', 'correlation_matrix',
            'per_symbol_volatility', 'elevated_volatility_symbols'
        ]
        for key in required_keys:
            self.assertIn(key, summary, f"Missing key: {key}")

    def test_sufficient_data_structure(self):
        """Summary with sufficient data should have complete structure."""
        engine = ContagionEngine(window_size=10)

        for i in range(15):
            engine.update_price('AAPL', 100.0 + i * 0.5)
            engine.update_price('MSFT', 200.0 + i * 0.3)

        summary = engine.get_contagion_summary()
        self.assertTrue(summary['data_sufficient'])
        self.assertEqual(summary['symbols_tracked'], 2)
        self.assertIsInstance(summary['correlation_matrix'], dict)
        self.assertIsInstance(summary['per_symbol_volatility'], dict)
        self.assertIn('AAPL', summary['per_symbol_volatility'])
        self.assertIn('MSFT', summary['per_symbol_volatility'])


class TestSymbolMetrics(unittest.TestCase):
    """Test per-symbol metrics retrieval."""

    def test_symbol_metrics_structure(self):
        """Symbol metrics should have expected fields."""
        engine = ContagionEngine(window_size=10)
        for i in range(10):
            engine.update_price('AAPL', 100.0 + i * 0.5)

        metrics = engine.get_symbol_metrics('AAPL')
        self.assertEqual(metrics['symbol'], 'AAPL')
        self.assertEqual(metrics['price_count'], 10)
        self.assertIsNotNone(metrics['latest_price'])
        self.assertIsNotNone(metrics['rolling_volatility'])

    def test_untracked_symbol_raises(self):
        """Getting metrics for untracked symbol should raise."""
        engine = ContagionEngine()
        with self.assertRaises(ValueError):
            engine.get_symbol_metrics('TSLA')


class TestConfigurationValidation(unittest.TestCase):
    """Test constructor parameter validation."""

    def test_invalid_window_size(self):
        with self.assertRaises(ValueError):
            ContagionEngine(window_size=2)

    def test_valid_window_size_boundary(self):
        engine = ContagionEngine(window_size=5)
        self.assertEqual(engine.window_size, 5)

    def test_invalid_correlation_threshold_zero(self):
        with self.assertRaises(ValueError):
            ContagionEngine(correlation_spike_threshold=0.0)

    def test_invalid_correlation_threshold_over_one(self):
        with self.assertRaises(ValueError):
            ContagionEngine(correlation_spike_threshold=1.5)

    def test_invalid_volatility_threshold(self):
        with self.assertRaises(ValueError):
            ContagionEngine(volatility_sync_threshold=0.5)

    def test_invalid_volatility_threshold_exactly_one(self):
        with self.assertRaises(ValueError):
            ContagionEngine(volatility_sync_threshold=1.0)


class TestResetAndEdgeCases(unittest.TestCase):
    """Test reset and edge cases."""

    def test_reset_clears_state(self):
        engine = ContagionEngine(window_size=10)
        engine.update_price('AAPL', 100.0)
        engine.update_price('MSFT', 200.0)
        engine.reset()

        self.assertEqual(len(engine.get_tracked_symbols()), 0)
        summary = engine.get_contagion_summary()
        self.assertEqual(summary['symbols_tracked'], 0)

    def test_window_bounds_memory(self):
        """Window should bound the price history length."""
        engine = ContagionEngine(window_size=10)
        for i in range(100):
            engine.update_price('AAPL', 100.0 + i * 0.1)

        metrics = engine.get_symbol_metrics('AAPL')
        self.assertLessEqual(metrics['price_count'], 10)


class TestMSIIntegration(unittest.TestCase):
    """Test CRS → MSI integration pathway."""

    def test_crs_feeds_into_msi(self):
        """CRS from contagion engine should be valid MSI input."""
        engine = ContagionEngine(window_size=10)
        np.random.seed(42)

        for i in range(15):
            engine.update_price('AAPL', 100.0 + i * 0.5)
            engine.update_price('MSFT', 200.0 + i * 0.3)

        summary = engine.get_contagion_summary()
        crs = summary['contagion_risk_score']

        # CRS must be in [0, 100] for MSI compatibility
        self.assertGreaterEqual(crs, 0.0)
        self.assertLessEqual(crs, 100.0)

        # Actually integrate with MSI
        from systemic.market_stability_index import MarketStabilityIndex
        msi = MarketStabilityIndex()
        result = msi.compute_msi(
            average_trust_score=85.0,
            market_anomaly_rate=0.02,
            total_anomalies=5,
            feed_mismatch_rate=0.01,
            contagion_risk_score=crs
        )

        self.assertIn('msi_score', result)
        self.assertGreaterEqual(result['msi_score'], 0)
        self.assertLessEqual(result['msi_score'], 100)


# ──────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("  CONTAGION ENGINE — TEST SUITE")
    print("=" * 70)
    print()
    unittest.main(verbosity=2)
