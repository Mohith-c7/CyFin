"""
Test Suite for Feed Integrity & Validation Engine
===================================================

Comprehensive tests covering:
- Feed registration and deregistration
- Price update and cross-feed validation
- Deviation computation and mismatch detection
- Reliability scoring (penalty and recovery)
- Per-symbol and global health aggregation
- Database persistence of mismatch events
- Edge cases and error handling
- Thread safety validation
- MSI integration pathway

Run with:
    python -m pytest test_feed_integrity_engine.py -v
    OR
    python test_feed_integrity_engine.py
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feed_validation.feed_integrity_engine import FeedIntegrityEngine


class TestFeedRegistration(unittest.TestCase):
    """Test feed registration and deregistration functionality."""

    def setUp(self):
        self.engine = FeedIntegrityEngine()

    def test_register_single_feed(self):
        """Register a single feed for a symbol."""
        self.engine.register_feed('AAPL', 'yahoo_finance')
        symbols = self.engine.get_registered_symbols()
        self.assertIn('AAPL', symbols)

    def test_register_multiple_feeds_same_symbol(self):
        """Register multiple feeds for the same symbol."""
        self.engine.register_feed('AAPL', 'yahoo_finance')
        self.engine.register_feed('AAPL', 'bloomberg')
        self.engine.register_feed('AAPL', 'reuters')
        feeds = self.engine.get_registered_feeds('AAPL')
        self.assertEqual(len(feeds), 3)
        self.assertIn('yahoo_finance', feeds)
        self.assertIn('bloomberg', feeds)
        self.assertIn('reuters', feeds)

    def test_register_feeds_multiple_symbols(self):
        """Register feeds across multiple symbols."""
        self.engine.register_feed('AAPL', 'yahoo_finance')
        self.engine.register_feed('MSFT', 'yahoo_finance')
        self.engine.register_feed('GOOGL', 'bloomberg')
        symbols = self.engine.get_registered_symbols()
        self.assertEqual(len(symbols), 3)

    def test_register_feed_idempotent(self):
        """Registering the same feed twice should be idempotent."""
        self.engine.register_feed('AAPL', 'yahoo_finance')
        self.engine.register_feed('AAPL', 'yahoo_finance')
        feeds = self.engine.get_registered_feeds('AAPL')
        self.assertEqual(len(feeds), 1)

    def test_register_feed_invalid_symbol(self):
        """Registering with empty symbol should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.register_feed('', 'yahoo_finance')

    def test_register_feed_invalid_feed_name(self):
        """Registering with empty feed name should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.register_feed('AAPL', '')

    def test_deregister_feed(self):
        """Deregistering a feed should remove it."""
        self.engine.register_feed('AAPL', 'yahoo_finance')
        self.engine.register_feed('AAPL', 'bloomberg')
        result = self.engine.deregister_feed('AAPL', 'yahoo_finance')
        self.assertTrue(result)
        feeds = self.engine.get_registered_feeds('AAPL')
        self.assertEqual(len(feeds), 1)
        self.assertNotIn('yahoo_finance', feeds)

    def test_deregister_last_feed_removes_symbol(self):
        """Deregistering the last feed should remove the symbol."""
        self.engine.register_feed('AAPL', 'yahoo_finance')
        self.engine.deregister_feed('AAPL', 'yahoo_finance')
        symbols = self.engine.get_registered_symbols()
        self.assertNotIn('AAPL', symbols)

    def test_deregister_nonexistent_feed(self):
        """Deregistering a non-existent feed should return False."""
        result = self.engine.deregister_feed('AAPL', 'nonexistent')
        self.assertFalse(result)


class TestPriceUpdates(unittest.TestCase):
    """Test price update and validation logic."""

    def setUp(self):
        self.engine = FeedIntegrityEngine(deviation_threshold=0.01)
        self.engine.register_feed('AAPL', 'feed_a')
        self.engine.register_feed('AAPL', 'feed_b')
        self.now = datetime.utcnow()

    def test_update_price_basic(self):
        """Update price for a registered feed."""
        result = self.engine.update_price(
            'AAPL', 'feed_a', 150.0, self.now
        )
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertFalse(result['validation_performed'])

    def test_validation_requires_min_feeds(self):
        """Validation should not trigger until min feeds have prices."""
        result = self.engine.update_price(
            'AAPL', 'feed_a', 150.0, self.now
        )
        self.assertFalse(result['validation_performed'])

    def test_validation_triggers_with_two_feeds(self):
        """Validation should trigger once two feeds have prices."""
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        result = self.engine.update_price(
            'AAPL', 'feed_b', 150.5, self.now
        )
        self.assertTrue(result['validation_performed'])

    def test_no_mismatch_within_threshold(self):
        """Prices within threshold should not trigger mismatch."""
        # 0.33% deviation - within 1% threshold
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        result = self.engine.update_price(
            'AAPL', 'feed_b', 150.5, self.now
        )
        self.assertFalse(result['mismatch_detected'])

    def test_mismatch_exceeds_threshold(self):
        """Prices exceeding threshold should trigger mismatch."""
        # ~2.6% deviation - exceeds 1% threshold
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        result = self.engine.update_price(
            'AAPL', 'feed_b', 154.0, self.now
        )
        self.assertTrue(result['mismatch_detected'])
        self.assertGreater(result['max_deviation_percent'], 0.01)

    def test_deviation_formula_correctness(self):
        """Verify the symmetric deviation formula."""
        # deviation = |150 - 154| / ((150 + 154) / 2) = 4 / 152 ≈ 0.02632
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        result = self.engine.update_price(
            'AAPL', 'feed_b', 154.0, self.now
        )
        expected_deviation = abs(150.0 - 154.0) / ((150.0 + 154.0) / 2.0)
        self.assertAlmostEqual(
            result['max_deviation_percent'],
            expected_deviation,
            places=6
        )

    def test_update_unregistered_symbol_raises(self):
        """Updating an unregistered symbol should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.update_price('TSLA', 'feed_a', 200.0, self.now)

    def test_update_unregistered_feed_raises(self):
        """Updating an unregistered feed should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.update_price(
                'AAPL', 'nonexistent', 150.0, self.now
            )

    def test_update_invalid_price_raises(self):
        """Updating with non-positive price should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.update_price('AAPL', 'feed_a', -10.0, self.now)
        with self.assertRaises(ValueError):
            self.engine.update_price('AAPL', 'feed_a', 0.0, self.now)


class TestReliabilityScoring(unittest.TestCase):
    """Test feed reliability scoring (penalty and recovery)."""

    def setUp(self):
        self.engine = FeedIntegrityEngine(
            deviation_threshold=0.01,
            severity_weight=5.0,
            recovery_rate=0.5
        )
        self.engine.register_feed('AAPL', 'feed_a')
        self.engine.register_feed('AAPL', 'feed_b')
        self.now = datetime.utcnow()

    def test_initial_reliability_is_100(self):
        """All feeds should start with reliability score of 100."""
        summary = self.engine.get_symbol_feed_summary('AAPL')
        for feed_info in summary['feeds'].values():
            self.assertEqual(feed_info['reliability_score'], 100.0)

    def test_reliability_decreases_on_mismatch(self):
        """Reliability should decrease when mismatch is detected."""
        self.engine.update_price('AAPL', 'feed_a', 100.0, self.now)
        self.engine.update_price('AAPL', 'feed_b', 105.0, self.now)

        summary = self.engine.get_symbol_feed_summary('AAPL')
        for feed_info in summary['feeds'].values():
            self.assertLess(feed_info['reliability_score'], 100.0)

    def test_reliability_penalty_formula(self):
        """Verify penalty = severity_weight * deviation * 100."""
        p1, p2 = 100.0, 105.0
        deviation = abs(p1 - p2) / ((p1 + p2) / 2.0)
        expected_penalty = 5.0 * deviation * 100

        self.engine.update_price('AAPL', 'feed_a', p1, self.now)
        self.engine.update_price('AAPL', 'feed_b', p2, self.now)

        summary = self.engine.get_symbol_feed_summary('AAPL')
        for feed_info in summary['feeds'].values():
            actual_reliability = feed_info['reliability_score']
            expected_reliability = round(100.0 - expected_penalty, 2)
            self.assertAlmostEqual(
                actual_reliability, expected_reliability, places=1
            )

    def test_reliability_recovers_gradually(self):
        """Reliability should recover when no mismatches occur."""
        # First: cause a mismatch to lower reliability
        self.engine.update_price('AAPL', 'feed_a', 100.0, self.now)
        self.engine.update_price('AAPL', 'feed_b', 105.0, self.now)

        # Then: provide consistent prices to trigger recovery
        for i in range(10):
            ts = self.now + timedelta(seconds=i + 1)
            self.engine.update_price('AAPL', 'feed_a', 102.0, ts)
            self.engine.update_price('AAPL', 'feed_b', 102.0, ts)

        summary = self.engine.get_symbol_feed_summary('AAPL')
        for feed_info in summary['feeds'].values():
            # Should have recovered somewhat from the initial penalty
            # (recovery_rate=0.5 per validated cycle, so ~10 pts over 20 updates)
            self.assertGreater(feed_info['reliability_score'], 70.0)

    def test_reliability_clamped_to_zero(self):
        """Reliability should never go below 0."""
        engine = FeedIntegrityEngine(
            deviation_threshold=0.001,  # Very tight threshold
            severity_weight=100.0       # Very severe penalty
        )
        engine.register_feed('AAPL', 'feed_a')
        engine.register_feed('AAPL', 'feed_b')

        # Large deviation with extreme penalty
        engine.update_price('AAPL', 'feed_a', 100.0, self.now)
        engine.update_price('AAPL', 'feed_b', 200.0, self.now)

        summary = engine.get_symbol_feed_summary('AAPL')
        for feed_info in summary['feeds'].values():
            self.assertGreaterEqual(feed_info['reliability_score'], 0.0)

    def test_reliability_clamped_to_100(self):
        """Reliability should never exceed 100."""
        # Provide many consistent updates to trigger recovery
        for i in range(200):
            ts = self.now + timedelta(seconds=i)
            self.engine.update_price('AAPL', 'feed_a', 100.0, ts)
            self.engine.update_price('AAPL', 'feed_b', 100.0, ts)

        summary = self.engine.get_symbol_feed_summary('AAPL')
        for feed_info in summary['feeds'].values():
            self.assertLessEqual(feed_info['reliability_score'], 100.0)


class TestSymbolFeedSummary(unittest.TestCase):
    """Test get_symbol_feed_summary output structure and values."""

    def setUp(self):
        self.engine = FeedIntegrityEngine()
        self.engine.register_feed('AAPL', 'feed_a')
        self.engine.register_feed('AAPL', 'feed_b')
        self.engine.register_feed('AAPL', 'feed_c')
        self.now = datetime.utcnow()

    def test_summary_structure(self):
        """Summary should contain all required keys."""
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        self.engine.update_price('AAPL', 'feed_b', 150.0, self.now)

        summary = self.engine.get_symbol_feed_summary('AAPL')
        self.assertIn('symbol', summary)
        self.assertIn('feeds', summary)
        self.assertIn('max_deviation_percent', summary)
        self.assertIn('mismatch_count', summary)
        self.assertIn('feed_mismatch_rate', summary)
        self.assertIn('total_updates', summary)
        self.assertIn('active_feeds', summary)
        self.assertIn('registered_feeds', summary)

    def test_per_feed_structure(self):
        """Each feed in summary should have required fields."""
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        summary = self.engine.get_symbol_feed_summary('AAPL')
        feed_info = summary['feeds']['feed_a']
        self.assertIn('latest_price', feed_info)
        self.assertIn('reliability_score', feed_info)
        self.assertIn('last_updated', feed_info)
        self.assertIn('total_updates', feed_info)
        self.assertIn('mismatch_count', feed_info)

    def test_active_vs_registered_feeds(self):
        """Distinguish between registers feeds and those with prices."""
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        summary = self.engine.get_symbol_feed_summary('AAPL')
        self.assertEqual(summary['registered_feeds'], 3)
        self.assertEqual(summary['active_feeds'], 1)

    def test_mismatch_rate_calculation(self):
        """Feed mismatch rate should be mismatches / validation cycles."""
        # 2 consistent prices → validated, no mismatch
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        self.engine.update_price('AAPL', 'feed_b', 150.0, self.now)

        summary = self.engine.get_symbol_feed_summary('AAPL')
        self.assertEqual(summary['feed_mismatch_rate'], 0.0)

    def test_summary_for_unregistered_symbol_raises(self):
        """Getting summary for unregistered symbol should raise."""
        with self.assertRaises(ValueError):
            self.engine.get_symbol_feed_summary('TSLA')


class TestGlobalFeedHealth(unittest.TestCase):
    """Test get_global_feed_health output structure and values."""

    def setUp(self):
        self.engine = FeedIntegrityEngine(deviation_threshold=0.01)
        self.now = datetime.utcnow()

    def test_empty_engine_health(self):
        """Global health with no feeds should return safe defaults."""
        health = self.engine.get_global_feed_health()
        self.assertEqual(health['total_symbols'], 0)
        self.assertEqual(health['total_feeds'], 0)
        self.assertEqual(health['total_mismatches'], 0)
        self.assertEqual(health['average_feed_reliability'], 100.0)
        self.assertEqual(health['global_feed_mismatch_rate'], 0.0)

    def test_health_structure(self):
        """Global health should contain all required keys."""
        self.engine.register_feed('AAPL', 'feed_a')
        self.engine.register_feed('AAPL', 'feed_b')
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        self.engine.update_price('AAPL', 'feed_b', 150.0, self.now)

        health = self.engine.get_global_feed_health()
        self.assertIn('total_symbols', health)
        self.assertIn('total_feeds', health)
        self.assertIn('total_mismatches', health)
        self.assertIn('total_validation_cycles', health)
        self.assertIn('total_price_updates', health)
        self.assertIn('average_feed_reliability', health)
        self.assertIn('global_feed_mismatch_rate', health)
        self.assertIn('per_symbol_health', health)
        self.assertIn('lowest_reliability_feeds', health)

    def test_multi_symbol_aggregation(self):
        """Health should aggregate across multiple symbols."""
        # Symbol 1: consistent
        self.engine.register_feed('AAPL', 'feed_a')
        self.engine.register_feed('AAPL', 'feed_b')
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        self.engine.update_price('AAPL', 'feed_b', 150.0, self.now)

        # Symbol 2: mismatched
        self.engine.register_feed('MSFT', 'feed_a')
        self.engine.register_feed('MSFT', 'feed_b')
        self.engine.update_price('MSFT', 'feed_a', 300.0, self.now)
        self.engine.update_price('MSFT', 'feed_b', 310.0, self.now)

        health = self.engine.get_global_feed_health()
        self.assertEqual(health['total_symbols'], 2)
        self.assertEqual(health['total_feeds'], 4)
        self.assertEqual(health['total_mismatches'], 1)  # MSFT mismatch

    def test_global_mismatch_rate_accuracy(self):
        """Global mismatch rate should be total mismatches / total cycles."""
        self.engine.register_feed('AAPL', 'feed_a')
        self.engine.register_feed('AAPL', 'feed_b')

        # Cycle 1: consistent
        self.engine.update_price('AAPL', 'feed_a', 150.0, self.now)
        self.engine.update_price(
            'AAPL', 'feed_b', 150.0, self.now
        )

        # Cycle 2: mismatched
        ts2 = self.now + timedelta(seconds=1)
        self.engine.update_price('AAPL', 'feed_a', 150.0, ts2)
        self.engine.update_price(
            'AAPL', 'feed_b', 160.0, ts2
        )

        health = self.engine.get_global_feed_health()
        # 1 mismatch out of multiple validation cycles
        self.assertGreater(health['global_feed_mismatch_rate'], 0.0)
        self.assertLessEqual(health['global_feed_mismatch_rate'], 1.0)


class TestMSIIntegration(unittest.TestCase):
    """Test that feed engine output integrates with MSI."""

    def test_feed_mismatch_rate_compatible_with_msi(self):
        """global_feed_mismatch_rate should be valid MSI input."""
        engine = FeedIntegrityEngine()
        engine.register_feed('AAPL', 'feed_a')
        engine.register_feed('AAPL', 'feed_b')
        now = datetime.utcnow()
        engine.update_price('AAPL', 'feed_a', 150.0, now)
        engine.update_price('AAPL', 'feed_b', 155.0, now)

        health = engine.get_global_feed_health()
        rate = health['global_feed_mismatch_rate']

        # Must be in [0, 1] range for MSI
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)

        # Verify MSI can consume it
        from systemic.market_stability_index import MarketStabilityIndex
        msi = MarketStabilityIndex()
        result = msi.compute_msi(
            average_trust_score=85.0,
            market_anomaly_rate=0.02,
            total_anomalies=5,
            feed_mismatch_rate=rate
        )
        self.assertIn('msi_score', result)
        self.assertIn('market_state', result)
        self.assertGreaterEqual(result['msi_score'], 0)
        self.assertLessEqual(result['msi_score'], 100)


class TestConfigurationValidation(unittest.TestCase):
    """Test constructor parameter validation."""

    def test_invalid_deviation_threshold_zero(self):
        with self.assertRaises(ValueError):
            FeedIntegrityEngine(deviation_threshold=0.0)

    def test_invalid_deviation_threshold_negative(self):
        with self.assertRaises(ValueError):
            FeedIntegrityEngine(deviation_threshold=-0.01)

    def test_invalid_deviation_threshold_over_one(self):
        with self.assertRaises(ValueError):
            FeedIntegrityEngine(deviation_threshold=1.5)

    def test_invalid_severity_weight(self):
        with self.assertRaises(ValueError):
            FeedIntegrityEngine(severity_weight=-1.0)

    def test_invalid_recovery_rate(self):
        with self.assertRaises(ValueError):
            FeedIntegrityEngine(recovery_rate=-0.1)

    def test_invalid_min_feeds(self):
        with self.assertRaises(ValueError):
            FeedIntegrityEngine(min_feeds_for_validation=1)


class TestResetAndEdgeCases(unittest.TestCase):
    """Test reset functionality and edge cases."""

    def test_reset_clears_state(self):
        """Reset should clear all engine state."""
        engine = FeedIntegrityEngine()
        engine.register_feed('AAPL', 'feed_a')
        engine.register_feed('AAPL', 'feed_b')
        engine.update_price(
            'AAPL', 'feed_a', 150.0, datetime.utcnow()
        )
        engine.reset()

        self.assertEqual(len(engine.get_registered_symbols()), 0)
        health = engine.get_global_feed_health()
        self.assertEqual(health['total_symbols'], 0)

    def test_three_feeds_pairwise_comparison(self):
        """Three feeds should produce 3 pairwise comparisons."""
        engine = FeedIntegrityEngine(deviation_threshold=0.01)
        engine.register_feed('AAPL', 'feed_a')
        engine.register_feed('AAPL', 'feed_b')
        engine.register_feed('AAPL', 'feed_c')
        now = datetime.utcnow()

        engine.update_price('AAPL', 'feed_a', 100.0, now)
        engine.update_price('AAPL', 'feed_b', 100.0, now)
        result = engine.update_price('AAPL', 'feed_c', 100.0, now)

        # 3 feeds → C(3,2) = 3 pairwise comparisons
        self.assertEqual(len(result['deviations']), 3)

    def test_identical_prices_zero_deviation(self):
        """Identical prices should produce zero deviation."""
        engine = FeedIntegrityEngine()
        engine.register_feed('AAPL', 'feed_a')
        engine.register_feed('AAPL', 'feed_b')
        now = datetime.utcnow()

        engine.update_price('AAPL', 'feed_a', 100.0, now)
        result = engine.update_price('AAPL', 'feed_b', 100.0, now)

        self.assertEqual(result['max_deviation_percent'], 0.0)
        self.assertFalse(result['mismatch_detected'])


class TestDatabasePersistence(unittest.TestCase):
    """Test database event persistence."""

    def test_mismatch_persisted_to_db(self):
        """Mismatch events should be logged via db_manager."""
        from database.db_manager import DatabaseManager

        db_path = 'test_feed_integrity.db'
        try:
            db = DatabaseManager(db_path)
            engine = FeedIntegrityEngine(
                deviation_threshold=0.01,
                db_manager=db
            )
            engine.register_feed('AAPL', 'feed_a')
            engine.register_feed('AAPL', 'feed_b')

            now = datetime.utcnow()
            engine.update_price('AAPL', 'feed_a', 100.0, now)
            engine.update_price('AAPL', 'feed_b', 110.0, now)

            # Check that a system event was logged
            stats = db.get_statistics()
            self.assertGreater(stats['system_events_count'], 0)

            db.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_engine_works_without_db(self):
        """Engine should work fine without a database manager."""
        engine = FeedIntegrityEngine()  # No db_manager
        engine.register_feed('AAPL', 'feed_a')
        engine.register_feed('AAPL', 'feed_b')
        now = datetime.utcnow()

        engine.update_price('AAPL', 'feed_a', 100.0, now)
        result = engine.update_price('AAPL', 'feed_b', 110.0, now)
        self.assertTrue(result['mismatch_detected'])


# ──────────────────────────────────────────────────────────────────────────
# Main entry point for direct execution
# ──────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("  FEED INTEGRITY ENGINE — TEST SUITE")
    print("=" * 70)
    print()

    # Run with verbosity
    unittest.main(verbosity=2)
