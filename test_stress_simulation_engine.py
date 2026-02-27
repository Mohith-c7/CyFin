"""
Test Suite for Stress Simulation & Resilience Engine
======================================================

Comprehensive tests covering:
- Single-asset shock scenarios
- Multi-asset synchronized shocks
- Volatility amplification
- Feed corruption simulation
- Composite scenarios
- Resilience score computation
- Fragility classification
- Report structure validation
- Baseline immutability
- Standard battery execution
- Input validation
- Edge cases
- Full-stack integration

Run with:
    python -m pytest test_stress_simulation_engine.py -v -p no:asyncio
    OR
    python test_stress_simulation_engine.py
"""

import sys
import os
import math
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resilience.stress_simulation_engine import (
    StressSimulationEngine,
    FRAGILITY_ROBUST,
    FRAGILITY_MODERATE,
    FRAGILITY_FRAGILE,
    FRAGILITY_CRISIS_PRONE,
)


def _make_engine(**overrides):
    """Create a test engine with sensible defaults."""
    defaults = dict(
        baseline_msi=75.0,
        baseline_trust_scores={"AAPL": 85.0, "MSFT": 80.0, "GOOGL": 90.0},
        baseline_contagion_risk_score=15.0,
        baseline_feed_mismatch_rate=0.01,
        baseline_market_anomaly_rate=0.02,
        baseline_total_anomalies=5
    )
    defaults.update(overrides)
    return StressSimulationEngine(**defaults)


class TestSingleAssetShock(unittest.TestCase):
    """Test single-asset shock scenarios."""

    def setUp(self):
        self.engine = _make_engine()

    def test_report_structure(self):
        """Report must contain all required fields."""
        report = self.engine.simulate_single_asset_shock("AAPL", -20.0)
        required = [
            'simulation_id', 'timestamp', 'scenario_type',
            'baseline_msi', 'post_shock_msi', 'delta_msi',
            'resilience_score', 'baseline_risk_tier',
            'post_shock_risk_tier', 'tier_changed',
            'system_fragility_level', 'post_shock_metrics',
            'scenario_params', 'simulation_number'
        ]
        for key in required:
            self.assertIn(key, report, "Missing: %s" % key)

    def test_scenario_type(self):
        report = self.engine.simulate_single_asset_shock("AAPL", -10.0)
        self.assertEqual(report['scenario_type'], 'SINGLE_ASSET_SHOCK')

    def test_msi_decreases_on_negative_shock(self):
        """Negative shock should reduce MSI."""
        report = self.engine.simulate_single_asset_shock("AAPL", -30.0)
        self.assertLess(report['post_shock_msi'], report['baseline_msi'])

    def test_larger_shock_bigger_impact(self):
        """Larger shocks should cause bigger MSI drops."""
        r1 = self.engine.simulate_single_asset_shock("AAPL", -10.0)
        # Re-create engine since simulation_count incremented
        engine2 = _make_engine()
        r2 = engine2.simulate_single_asset_shock("AAPL", -50.0)
        self.assertGreater(r2['delta_msi'], r1['delta_msi'])

    def test_resilience_score_positive(self):
        """Resilience score should be positive for negative shocks."""
        report = self.engine.simulate_single_asset_shock("AAPL", -20.0)
        self.assertGreater(report['resilience_score'], 0.0)

    def test_unknown_symbol_raises(self):
        """Unknown symbol should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.simulate_single_asset_shock("UNKNOWN", -20.0)

    def test_shock_range_validation(self):
        """Shock outside [-100, 100] should raise."""
        with self.assertRaises(ValueError):
            self.engine.simulate_single_asset_shock("AAPL", -150.0)

    def test_delta_msi_computation(self):
        """Delta should equal baseline - post_shock."""
        report = self.engine.simulate_single_asset_shock("AAPL", -25.0)
        expected = report['baseline_msi'] - report['post_shock_msi']
        self.assertAlmostEqual(report['delta_msi'], expected, places=1)


class TestMultiAssetShock(unittest.TestCase):
    """Test multi-asset synchronized shocks."""

    def setUp(self):
        self.engine = _make_engine()

    def test_scenario_type(self):
        report = self.engine.simulate_multi_asset_shock(
            ["AAPL", "MSFT"], -15.0
        )
        self.assertEqual(report['scenario_type'], 'MULTI_ASSET_SHOCK')

    def test_worse_than_single(self):
        """Multi-asset shock should cause more damage than single."""
        r_single = self.engine.simulate_single_asset_shock("AAPL", -20.0)
        engine2 = _make_engine()
        r_multi = engine2.simulate_multi_asset_shock(
            ["AAPL", "MSFT", "GOOGL"], -20.0
        )
        self.assertGreater(r_multi['delta_msi'], r_single['delta_msi'])

    def test_all_assets_shock(self):
        """Shocking all assets should be severe."""
        report = self.engine.simulate_multi_asset_shock(
            ["AAPL", "MSFT", "GOOGL"], -40.0
        )
        self.assertGreater(report['delta_msi'], 10.0)

    def test_empty_symbols_raises(self):
        with self.assertRaises(ValueError):
            self.engine.simulate_multi_asset_shock([], -10.0)

    def test_unknown_symbol_raises(self):
        with self.assertRaises(ValueError):
            self.engine.simulate_multi_asset_shock(["FAKE"], -10.0)

    def test_scenario_params(self):
        """Report should include affected asset count."""
        report = self.engine.simulate_multi_asset_shock(
            ["AAPL", "MSFT"], -20.0
        )
        self.assertEqual(
            report['scenario_params']['affected_assets'], 2
        )


class TestVolatilityAmplification(unittest.TestCase):
    """Test volatility amplification scenarios."""

    def setUp(self):
        self.engine = _make_engine()

    def test_scenario_type(self):
        report = self.engine.simulate_volatility_amplification(2.0)
        self.assertEqual(
            report['scenario_type'], 'VOLATILITY_AMPLIFICATION'
        )

    def test_msi_decreases_with_vol(self):
        """Higher volatility should reduce MSI."""
        report = self.engine.simulate_volatility_amplification(3.0)
        self.assertLess(report['post_shock_msi'], report['baseline_msi'])

    def test_no_change_at_1x(self):
        """Factor 1.0 should not change MSI."""
        report = self.engine.simulate_volatility_amplification(1.0)
        self.assertAlmostEqual(
            report['post_shock_msi'], report['baseline_msi'], places=1
        )

    def test_extreme_vol(self):
        """Extreme volatility (5x) should cause large drop."""
        report = self.engine.simulate_volatility_amplification(5.0)
        self.assertGreater(report['delta_msi'], 10.0)

    def test_invalid_factor(self):
        with self.assertRaises(ValueError):
            self.engine.simulate_volatility_amplification(0.5)

    def test_crs_increases_with_vol(self):
        """CRS should increase with volatility amplification."""
        report = self.engine.simulate_volatility_amplification(3.0)
        post_crs = report['post_shock_metrics']['contagion_risk_score']
        self.assertGreater(post_crs, self.engine.baseline_contagion_risk_score)


class TestFeedCorruption(unittest.TestCase):
    """Test feed corruption simulation."""

    def setUp(self):
        self.engine = _make_engine()

    def test_scenario_type(self):
        report = self.engine.simulate_feed_corruption("AAPL", 20.0)
        self.assertEqual(report['scenario_type'], 'FEED_CORRUPTION')

    def test_msi_decreases(self):
        """Feed corruption should reduce MSI."""
        report = self.engine.simulate_feed_corruption("AAPL", 30.0)
        self.assertLess(report['post_shock_msi'], report['baseline_msi'])

    def test_feed_rate_increases(self):
        """Feed mismatch rate should increase."""
        report = self.engine.simulate_feed_corruption("AAPL", 50.0)
        post_feed = report['post_shock_metrics']['feed_mismatch_rate']
        self.assertGreater(post_feed, self.engine.baseline_feed_mismatch_rate)

    def test_trust_degrades_for_affected(self):
        """Corrupted asset's trust should degrade."""
        report = self.engine.simulate_feed_corruption("AAPL", 40.0)
        post_trust = report['post_shock_metrics']['trust_scores']['AAPL']
        self.assertLess(post_trust, self.engine.baseline_trust_scores['AAPL'])

    def test_zero_corruption_minimal_impact(self):
        """Zero deviation should have minimal impact."""
        report = self.engine.simulate_feed_corruption("AAPL", 0.0)
        self.assertAlmostEqual(
            report['post_shock_msi'], report['baseline_msi'],
            places=0
        )

    def test_unknown_symbol_raises(self):
        with self.assertRaises(ValueError):
            self.engine.simulate_feed_corruption("FAKE", 10.0)

    def test_invalid_deviation(self):
        with self.assertRaises(ValueError):
            self.engine.simulate_feed_corruption("AAPL", 150.0)


class TestCompositeScenario(unittest.TestCase):
    """Test composite scenario simulation."""

    def setUp(self):
        self.engine = _make_engine()

    def test_scenario_type(self):
        report = self.engine.simulate_composite_scenario(
            asset_shocks={"AAPL": -20.0}
        )
        self.assertEqual(report['scenario_type'], 'COMPOSITE_SCENARIO')

    def test_worse_than_individual(self):
        """Composite should be worse than any individual component."""
        r_single = self.engine.simulate_single_asset_shock("AAPL", -20.0)
        engine2 = _make_engine()
        r_comp = engine2.simulate_composite_scenario(
            asset_shocks={"AAPL": -20.0},
            volatility_factor=3.0,
            feed_corruption={"MSFT": 30.0}
        )
        self.assertGreater(r_comp['delta_msi'], r_single['delta_msi'])

    def test_empty_scenario(self):
        """Empty scenario should produce minimal change."""
        report = self.engine.simulate_composite_scenario()
        self.assertAlmostEqual(
            report['post_shock_msi'], report['baseline_msi'],
            places=1
        )

    def test_components_count(self):
        """Should track number of active components."""
        report = self.engine.simulate_composite_scenario(
            asset_shocks={"AAPL": -10.0},
            volatility_factor=2.0,
            feed_corruption={"MSFT": 10.0}
        )
        self.assertEqual(
            report['scenario_params']['components_active'], 3
        )


class TestFragilityClassification(unittest.TestCase):
    """Test fragility classification logic."""

    def setUp(self):
        self.engine = _make_engine()

    def test_robust(self):
        """Small delta (< 10) should be ROBUST."""
        report = self.engine.simulate_single_asset_shock("AAPL", -5.0)
        self.assertEqual(report['system_fragility_level'], FRAGILITY_ROBUST)

    def test_fragile_or_crisis_under_extreme(self):
        """Extreme multi-asset shock should be FRAGILE or CRISIS_PRONE."""
        report = self.engine.simulate_multi_asset_shock(
            ["AAPL", "MSFT", "GOOGL"], -60.0
        )
        self.assertIn(report['system_fragility_level'], [
            FRAGILITY_FRAGILE, FRAGILITY_CRISIS_PRONE
        ])


class TestBaselineImmutability(unittest.TestCase):
    """Test that simulations never modify baseline state."""

    def test_baseline_msi_unchanged(self):
        """Baseline MSI must not change after simulation."""
        engine = _make_engine()
        original_msi = engine.baseline_msi
        engine.simulate_single_asset_shock("AAPL", -50.0)
        self.assertAlmostEqual(engine.baseline_msi, original_msi, places=2)

    def test_baseline_trust_unchanged(self):
        """Baseline trust scores must not change."""
        engine = _make_engine()
        original_trust = dict(engine.baseline_trust_scores)
        engine.simulate_single_asset_shock("AAPL", -50.0)
        self.assertEqual(engine.baseline_trust_scores, original_trust)

    def test_baseline_crs_unchanged(self):
        """Baseline CRS must not change."""
        engine = _make_engine()
        original_crs = engine.baseline_contagion_risk_score
        engine.simulate_volatility_amplification(5.0)
        self.assertEqual(
            engine.baseline_contagion_risk_score, original_crs
        )

    def test_baseline_feed_unchanged(self):
        """Baseline feed rate must not change."""
        engine = _make_engine()
        original_feed = engine.baseline_feed_mismatch_rate
        engine.simulate_feed_corruption("AAPL", 50.0)
        self.assertEqual(
            engine.baseline_feed_mismatch_rate, original_feed
        )


class TestSimulationHistory(unittest.TestCase):
    """Test simulation history tracking."""

    def test_history_accumulates(self):
        engine = _make_engine()
        engine.simulate_single_asset_shock("AAPL", -10.0)
        engine.simulate_volatility_amplification(2.0)
        engine.simulate_feed_corruption("MSFT", 20.0)
        self.assertEqual(engine.get_simulation_count(), 3)
        self.assertEqual(len(engine.get_simulation_history()), 3)

    def test_history_newest_first(self):
        engine = _make_engine()
        engine.simulate_single_asset_shock("AAPL", -10.0)
        engine.simulate_volatility_amplification(2.0)
        history = engine.get_simulation_history()
        self.assertEqual(
            history[0]['scenario_type'], 'VOLATILITY_AMPLIFICATION'
        )

    def test_simulation_numbers_sequential(self):
        engine = _make_engine()
        r1 = engine.simulate_single_asset_shock("AAPL", -10.0)
        r2 = engine.simulate_volatility_amplification(2.0)
        self.assertEqual(r2['simulation_number'],
                         r1['simulation_number'] + 1)


class TestStandardBattery(unittest.TestCase):
    """Test standard stress test battery."""

    def test_battery_runs(self):
        """Standard battery should produce multiple reports."""
        engine = _make_engine()
        results = engine.run_standard_battery()
        self.assertGreater(len(results), 5)

    def test_battery_all_valid(self):
        """All battery reports should have valid structure."""
        engine = _make_engine()
        results = engine.run_standard_battery()
        for report in results:
            self.assertIn('scenario_type', report)
            self.assertIn('delta_msi', report)
            self.assertIn('system_fragility_level', report)

    def test_battery_covers_scenarios(self):
        """Battery should cover multiple scenario types."""
        engine = _make_engine()
        results = engine.run_standard_battery()
        types = set(r['scenario_type'] for r in results)
        self.assertIn('SINGLE_ASSET_SHOCK', types)
        self.assertIn('MULTI_ASSET_SHOCK', types)
        self.assertIn('VOLATILITY_AMPLIFICATION', types)
        self.assertIn('FEED_CORRUPTION', types)
        self.assertIn('COMPOSITE_SCENARIO', types)


class TestTierChanges(unittest.TestCase):
    """Test risk tier change detection."""

    def test_mild_no_tier_change(self):
        """Very mild shock likely keeps same tier."""
        # Use high trust scores so baseline computes high MSI in same tier
        engine = _make_engine(
            baseline_msi=90.0,
            baseline_trust_scores={"AAPL": 95.0, "MSFT": 95.0, "GOOGL": 95.0},
            baseline_contagion_risk_score=0.0,
            baseline_feed_mismatch_rate=0.0,
            baseline_market_anomaly_rate=0.0,
            baseline_total_anomalies=0
        )
        report = engine.simulate_single_asset_shock("AAPL", -2.0)
        self.assertFalse(report['tier_changed'])

    def test_severe_tier_change(self):
        """Severe shock should trigger tier change."""
        # Use high trust so baseline tier is NORMAL or ELEVATED
        engine = _make_engine(
            baseline_msi=85.0,
            baseline_trust_scores={"AAPL": 95.0, "MSFT": 95.0, "GOOGL": 95.0},
            baseline_contagion_risk_score=0.0,
            baseline_feed_mismatch_rate=0.0,
            baseline_market_anomaly_rate=0.0,
            baseline_total_anomalies=0
        )
        report = engine.simulate_multi_asset_shock(
            ["AAPL", "MSFT", "GOOGL"], -60.0
        )
        self.assertTrue(report['tier_changed'])


class TestInputValidation(unittest.TestCase):
    """Test constructor and method input validation."""

    def test_invalid_baseline_msi(self):
        with self.assertRaises(ValueError):
            StressSimulationEngine(
                baseline_msi=150.0,
                baseline_trust_scores={"A": 80.0}
            )

    def test_empty_trust_scores(self):
        with self.assertRaises(ValueError):
            StressSimulationEngine(
                baseline_msi=75.0,
                baseline_trust_scores={}
            )

    def test_invalid_trust_type(self):
        with self.assertRaises(TypeError):
            StressSimulationEngine(
                baseline_msi=75.0,
                baseline_trust_scores={"A": "high"}
            )

    def test_invalid_crs_range(self):
        with self.assertRaises(ValueError):
            StressSimulationEngine(
                baseline_msi=75.0,
                baseline_trust_scores={"A": 80.0},
                baseline_contagion_risk_score=-10.0
            )


class TestMSIConsistency(unittest.TestCase):
    """Verify internal MSI formula matches actual MarketStabilityIndex."""

    def test_formula_match(self):
        """Internal MSI should match actual MSI engine."""
        from systemic.market_stability_index import MarketStabilityIndex

        trust = {"AAPL": 85.0, "MSFT": 80.0, "GOOGL": 90.0}
        avg_trust = sum(trust.values()) / len(trust)
        crs = 25.0
        feed = 0.02
        anomaly_rate = 0.05
        total_anom = 15

        # Actual MSI
        msi_calc = MarketStabilityIndex()
        actual = msi_calc.compute_msi(
            average_trust_score=avg_trust,
            market_anomaly_rate=anomaly_rate,
            total_anomalies=total_anom,
            feed_mismatch_rate=feed,
            contagion_risk_score=crs
        )

        # Stress engine internal MSI
        engine = StressSimulationEngine(
            baseline_msi=75.0,
            baseline_trust_scores=trust,
            baseline_contagion_risk_score=crs,
            baseline_feed_mismatch_rate=feed,
            baseline_market_anomaly_rate=anomaly_rate,
            baseline_total_anomalies=total_anom
        )
        internal = engine._compute_msi(
            trust, crs, feed, anomaly_rate, total_anom
        )

        self.assertAlmostEqual(
            actual['msi_score'], internal, places=1
        )


class TestFullStackIntegration(unittest.TestCase):
    """Test full 7-module pipeline integration."""

    def test_end_to_end(self):
        """Full pipeline → stress simulation should work."""
        import numpy as np
        from datetime import datetime
        from feed_validation.feed_integrity_engine import (
            FeedIntegrityEngine
        )
        from systemic.contagion_engine import ContagionEngine
        from systemic.market_stability_index import MarketStabilityIndex
        from systemic.systemic_action_engine import SystemicActionEngine
        from governance.incident_intelligence_engine import (
            IncidentIntelligenceEngine
        )
        from governance.explainability_engine import ExplainabilityEngine

        # 1-6: Full pipeline
        fe = FeedIntegrityEngine(deviation_threshold=0.01)
        fe.register_feed('AAPL', 'yahoo')
        fe.register_feed('AAPL', 'bloomberg')
        fe.register_feed('MSFT', 'yahoo')
        fe.register_feed('MSFT', 'bloomberg')
        now = datetime.utcnow()
        fe.update_price('AAPL', 'yahoo', 178.50, now)
        fe.update_price('AAPL', 'bloomberg', 178.55, now)
        fe.update_price('MSFT', 'yahoo', 350.0, now)
        fe.update_price('MSFT', 'bloomberg', 350.1, now)
        feed_health = fe.get_global_feed_health()

        ce = ContagionEngine(window_size=10)
        np.random.seed(42)
        for i in range(15):
            ce.update_price('AAPL', 150.0 + i * 0.5)
            ce.update_price('MSFT', 300.0 + i * 0.3)
        contagion = ce.get_contagion_summary()

        trust_scores = {"AAPL": 85.0, "MSFT": 80.0}

        msi_calc = MarketStabilityIndex()
        msi_result = msi_calc.compute_msi(
            average_trust_score=82.5,
            market_anomaly_rate=0.02,
            total_anomalies=5,
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            contagion_risk_score=contagion['contagion_risk_score']
        )

        ae = SystemicActionEngine()
        action = ae.evaluate_systemic_risk(
            msi=msi_result['msi_score'],
            contagion_risk_score=contagion['contagion_risk_score'],
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            average_trust_score=82.5
        )

        # 7: Stress Simulation
        stress = StressSimulationEngine(
            baseline_msi=msi_result['msi_score'],
            baseline_trust_scores=trust_scores,
            baseline_contagion_risk_score=contagion['contagion_risk_score'],
            baseline_feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            baseline_market_anomaly_rate=0.02,
            baseline_total_anomalies=5
        )

        # Run scenarios
        r1 = stress.simulate_single_asset_shock("AAPL", -30.0)
        r2 = stress.simulate_multi_asset_shock(
            ["AAPL", "MSFT"], -25.0
        )
        r3 = stress.simulate_volatility_amplification(3.0)
        r4 = stress.simulate_feed_corruption("MSFT", 25.0)
        r5 = stress.simulate_composite_scenario(
            asset_shocks={"AAPL": -20.0, "MSFT": -15.0},
            volatility_factor=2.0,
            feed_corruption={"AAPL": 10.0}
        )

        # Validate all results
        for report in [r1, r2, r3, r4, r5]:
            self.assertIn('delta_msi', report)
            self.assertIn('system_fragility_level', report)
            self.assertGreaterEqual(report['post_shock_msi'], 0.0)
            self.assertLessEqual(report['post_shock_msi'], 100.0)

        # Multi should be worse than single
        self.assertGreater(r2['delta_msi'], r1['delta_msi'])

        # Composite should be worst
        self.assertGreater(r5['delta_msi'], r1['delta_msi'])

        # History should have all 5
        self.assertEqual(stress.get_simulation_count(), 5)

        # Standard battery should also work
        battery = stress.run_standard_battery()
        self.assertGreater(len(battery), 5)


# ──────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("  STRESS SIMULATION ENGINE - TEST SUITE")
    print("=" * 70)
    print()
    unittest.main(verbosity=2)
