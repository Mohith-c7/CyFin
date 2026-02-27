"""
Test Suite for Risk Attribution & Explainability Engine
=========================================================

Comprehensive tests covering:
- MSI decomposition and component verification
- Severity score decomposition
- Dominant risk factor identification
- Asset systemic impact ranking
- Risk tier explanation
- Narrative generation
- Input validation
- Edge cases and boundary conditions
- Cross-verification with actual MSI/Severity engines
- Full-stack integration

Run with:
    python -m pytest test_explainability_engine.py -v -p no:asyncio
    OR
    python test_explainability_engine.py
"""

import sys
import os
import math
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from governance.explainability_engine import ExplainabilityEngine


class TestMSIExplanation(unittest.TestCase):
    """Test MSI decomposition and attribution."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_output_has_all_required_fields(self):
        """Output must contain all required keys."""
        result = self.engine.explain_msi(
            average_trust_score=80.0,
            market_anomaly_rate=0.05,
            total_anomalies=10,
            feed_mismatch_rate=0.02,
            contagion_risk_score=30.0
        )
        required = [
            'msi_final_score', 'msi_raw_score',
            'component_contributions', 'component_percentages',
            'dominant_risk_factor', 'dominant_risk_magnitude',
            'inputs', 'formula'
        ]
        for key in required:
            self.assertIn(key, result, "Missing: %s" % key)

    def test_component_contributions_keys(self):
        """Component contributions must contain all 5 MSI components."""
        result = self.engine.explain_msi(80.0, 0.05, 10, 0.02, 30.0)
        components = result['component_contributions']
        expected_keys = [
            'trust_component', 'anomaly_rate_penalty',
            'anomaly_count_penalty', 'feed_mismatch_penalty',
            'contagion_penalty'
        ]
        for key in expected_keys:
            self.assertIn(key, components)

    def test_trust_component_calculation(self):
        """Trust component should be 1.0 * trust_score."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 0.0)
        expected = 1.0 * 80.0
        self.assertAlmostEqual(
            result['component_contributions']['trust_component'],
            expected, places=2
        )

    def test_anomaly_rate_penalty(self):
        """Anomaly rate penalty should be -20 * rate."""
        result = self.engine.explain_msi(80.0, 0.1, 0, 0.0, 0.0)
        expected = -20.0 * 0.1
        self.assertAlmostEqual(
            result['component_contributions']['anomaly_rate_penalty'],
            expected, places=2
        )

    def test_anomaly_count_penalty(self):
        """Anomaly count penalty should be -4 * log(1+count)."""
        result = self.engine.explain_msi(80.0, 0.0, 50, 0.0, 0.0)
        expected = -4.0 * math.log(1 + 50)
        self.assertAlmostEqual(
            result['component_contributions']['anomaly_count_penalty'],
            expected, places=2
        )

    def test_feed_mismatch_penalty(self):
        """Feed penalty should be -25 * rate."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.10, 0.0)
        expected = -25.0 * 0.10
        self.assertAlmostEqual(
            result['component_contributions']['feed_mismatch_penalty'],
            expected, places=2
        )

    def test_contagion_penalty(self):
        """Contagion penalty should be -0.30 * CRS."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 60.0)
        expected = -0.30 * 60.0
        self.assertAlmostEqual(
            result['component_contributions']['contagion_penalty'],
            expected, places=2
        )

    def test_components_sum_to_raw_msi(self):
        """Components must sum to the raw MSI score."""
        result = self.engine.explain_msi(75.0, 0.08, 20, 0.03, 45.0)
        comps = result['component_contributions']
        total = sum(comps.values())
        self.assertAlmostEqual(total, result['msi_raw_score'], places=2)

    def test_msi_clamped_to_100(self):
        """MSI final score must not exceed 100."""
        result = self.engine.explain_msi(100.0, 0.0, 0, 0.0, 0.0)
        self.assertLessEqual(result['msi_final_score'], 100.0)

    def test_msi_clamped_to_0(self):
        """MSI final score must not go below 0."""
        result = self.engine.explain_msi(0.0, 1.0, 1000, 1.0, 100.0)
        self.assertEqual(result['msi_final_score'], 0.0)

    def test_perfect_conditions(self):
        """Perfect inputs: trust=100, no anomalies, no feed, no contagion."""
        result = self.engine.explain_msi(100.0, 0.0, 0, 0.0, 0.0)
        self.assertEqual(result['msi_final_score'], 100.0)
        self.assertEqual(result['dominant_risk_factor'], "NONE")

    def test_inputs_echoed(self):
        """Input values must be echoed in output."""
        result = self.engine.explain_msi(80.0, 0.05, 10, 0.02, 30.0)
        self.assertEqual(result['inputs']['average_trust_score'], 80.0)
        self.assertEqual(result['inputs']['market_anomaly_rate'], 0.05)

    def test_formula_present(self):
        """Formula string must be present."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 0.0)
        self.assertIn('MSI', result['formula'])


class TestDominantRiskFactor(unittest.TestCase):
    """Test dominant risk factor identification."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_contagion_dominant(self):
        """When contagion penalty is largest, it should be dominant."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 80.0)
        self.assertEqual(
            result['dominant_risk_factor'], 'contagion_penalty'
        )

    def test_feed_dominant(self):
        """When feed penalty is largest, it should be dominant."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.50, 0.0)
        self.assertEqual(
            result['dominant_risk_factor'], 'feed_mismatch_penalty'
        )

    def test_anomaly_rate_dominant(self):
        """When anomaly rate penalty is largest, it should be dominant."""
        result = self.engine.explain_msi(80.0, 0.80, 0, 0.0, 0.0)
        self.assertEqual(
            result['dominant_risk_factor'], 'anomaly_rate_penalty'
        )

    def test_no_penalties(self):
        """With no penalties, dominant should be NONE."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 0.0)
        self.assertEqual(result['dominant_risk_factor'], 'NONE')

    def test_dominant_magnitude(self):
        """Dominant magnitude should equal the absolute penalty value."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 60.0)
        expected_mag = abs(-0.30 * 60.0)
        self.assertAlmostEqual(
            result['dominant_risk_magnitude'], expected_mag, places=2
        )


class TestComponentPercentages(unittest.TestCase):
    """Test component percentage calculations."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_percentages_sum_to_100(self):
        """Component percentages should sum to ~100%."""
        result = self.engine.explain_msi(75.0, 0.05, 10, 0.02, 40.0)
        total = sum(result['component_percentages'].values())
        self.assertAlmostEqual(total, 100.0, places=0)

    def test_trust_dominant_percentage(self):
        """With only trust (no penalties), it should be 100%."""
        result = self.engine.explain_msi(80.0, 0.0, 0, 0.0, 0.0)
        self.assertAlmostEqual(
            result['component_percentages']['trust_component'],
            100.0, places=0
        )


class TestSeverityExplanation(unittest.TestCase):
    """Test severity score decomposition."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_output_structure(self):
        """Output must contain all required keys."""
        result = self.engine.explain_severity(
            msi=50.0, contagion_risk_score=60.0,
            feed_mismatch_rate=0.03,
            average_trust_score=55.0
        )
        required = [
            'severity_score', 'component_contributions',
            'component_percentages', 'dominant_severity_factor',
            'dominant_severity_magnitude',
            'regulatory_classification', 'inputs', 'formula'
        ]
        for key in required:
            self.assertIn(key, result)

    def test_severity_components_keys(self):
        """Components should have all 4 severity dimensions."""
        result = self.engine.explain_severity(50.0, 60.0, 0.03, 55.0)
        expected = [
            'market_instability', 'contagion_risk',
            'data_integrity_risk', 'trust_deficit'
        ]
        for key in expected:
            self.assertIn(key, result['component_contributions'])

    def test_severity_formula_verification(self):
        """Verify severity matches formula."""
        msi, crs, fr, trust = 60.0, 50.0, 0.05, 70.0
        expected = (
            0.4 * (100 - msi)
            + 0.3 * crs
            + 0.2 * (fr * 100)
            + 0.1 * (100 - trust)
        )
        result = self.engine.explain_severity(msi, crs, fr, trust)
        self.assertAlmostEqual(
            result['severity_score'], expected, places=2
        )

    def test_severity_zero(self):
        """Perfect conditions should give severity 0."""
        result = self.engine.explain_severity(100.0, 0.0, 0.0, 100.0)
        self.assertEqual(result['severity_score'], 0.0)

    def test_severity_max(self):
        """Worst conditions should give severity 100."""
        result = self.engine.explain_severity(0.0, 100.0, 1.0, 0.0)
        self.assertEqual(result['severity_score'], 100.0)

    def test_critical_classification(self):
        """Severity > 80 should be CRITICAL_MARKET_EVENT."""
        result = self.engine.explain_severity(0.0, 100.0, 0.5, 0.0)
        self.assertEqual(
            result['regulatory_classification'],
            'CRITICAL_MARKET_EVENT'
        )

    def test_normal_classification(self):
        """Severity < 40 should be NORMAL_OPERATION."""
        result = self.engine.explain_severity(80.0, 10.0, 0.01, 85.0)
        self.assertEqual(
            result['regulatory_classification'],
            'NORMAL_OPERATION'
        )

    def test_dominant_severity_factor(self):
        """Should identify the largest contributing factor."""
        # MSI complement = 0.4 * 50 = 20 (dominant)
        # CRS = 0.3 * 10 = 3
        # Feed = 0.2 * 1 = 0.2
        # Trust = 0.1 * 15 = 1.5
        result = self.engine.explain_severity(50.0, 10.0, 0.01, 85.0)
        self.assertEqual(
            result['dominant_severity_factor'],
            'market_instability'
        )

    def test_components_sum_to_severity(self):
        """Components should sum to severity score."""
        result = self.engine.explain_severity(55.0, 45.0, 0.04, 60.0)
        total = sum(result['component_contributions'].values())
        self.assertAlmostEqual(total, result['severity_score'], places=2)


class TestAssetRanking(unittest.TestCase):
    """Test asset systemic impact ranking."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_ranking_order(self):
        """Assets should be ranked by highest risk (lowest trust) first."""
        scores = {"AAPL": 90.0, "MSFT": 30.0, "GOOGL": 60.0}
        ranking = self.engine.rank_asset_systemic_impact(scores)
        self.assertEqual(ranking[0]['symbol'], 'MSFT')
        self.assertEqual(ranking[1]['symbol'], 'GOOGL')
        self.assertEqual(ranking[2]['symbol'], 'AAPL')

    def test_rank_numbers(self):
        """Rank numbers should be 1-indexed and sequential."""
        scores = {"A": 80.0, "B": 50.0, "C": 30.0}
        ranking = self.engine.rank_asset_systemic_impact(scores)
        ranks = [r['rank'] for r in ranking]
        self.assertEqual(ranks, [1, 2, 3])

    def test_risk_contribution(self):
        """Risk contribution should be 100 - trust."""
        scores = {"AAPL": 80.0}
        ranking = self.engine.rank_asset_systemic_impact(scores)
        self.assertAlmostEqual(
            ranking[0]['risk_contribution'], 20.0, places=1
        )

    def test_risk_levels(self):
        """Risk levels should map correctly from trust scores."""
        scores = {
            "LOW": 85.0,      # trust >= 80 → LOW
            "MOD": 65.0,      # trust >= 60 → MODERATE
            "HIGH": 45.0,     # trust >= 40 → HIGH
            "CRIT": 20.0      # trust < 40 → CRITICAL
        }
        ranking = self.engine.rank_asset_systemic_impact(scores)
        levels = {r['symbol']: r['risk_level'] for r in ranking}
        self.assertEqual(levels['LOW'], 'LOW')
        self.assertEqual(levels['MOD'], 'MODERATE')
        self.assertEqual(levels['HIGH'], 'HIGH')
        self.assertEqual(levels['CRIT'], 'CRITICAL')

    def test_explanation_present(self):
        """Each ranked asset should have an explanation."""
        scores = {"AAPL": 30.0, "MSFT": 85.0}
        ranking = self.engine.rank_asset_systemic_impact(scores)
        for item in ranking:
            self.assertIn('explanation', item)
            self.assertGreater(len(item['explanation']), 10)

    def test_empty_scores_raises(self):
        """Empty asset scores should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.rank_asset_systemic_impact({})

    def test_invalid_score_type(self):
        """Non-numeric trust score should raise TypeError."""
        with self.assertRaises(TypeError):
            self.engine.rank_asset_systemic_impact({"A": "high"})

    def test_single_asset(self):
        """Single asset should work and have rank 1."""
        scores = {"ONLY": 50.0}
        ranking = self.engine.rank_asset_systemic_impact(scores)
        self.assertEqual(len(ranking), 1)
        self.assertEqual(ranking[0]['rank'], 1)


class TestRiskTierExplanation(unittest.TestCase):
    """Test risk tier explanation."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_no_escalation(self):
        """When base == final tier, no escalation."""
        result = self.engine.explain_risk_tier(
            msi=85.0, risk_tier="NORMAL",
            base_tier="NORMAL",
            escalation_reasons=[], enforcement_required=False
        )
        self.assertFalse(result['was_escalated'])
        self.assertEqual(result['escalation_steps'], 0)

    def test_single_escalation(self):
        """Single escalation should show 1 step."""
        result = self.engine.explain_risk_tier(
            msi=70.0, risk_tier="HIGH_VOLATILITY",
            base_tier="ELEVATED_RISK",
            escalation_reasons=["CRS > 70"],
            enforcement_required=True
        )
        self.assertTrue(result['was_escalated'])
        self.assertEqual(result['escalation_steps'], 1)

    def test_double_escalation(self):
        """Double escalation should show 2 steps."""
        result = self.engine.explain_risk_tier(
            msi=70.0, risk_tier="SYSTEMIC_CRISIS",
            base_tier="ELEVATED_RISK",
            escalation_reasons=["CRS > 70", "Feed > 2%"],
            enforcement_required=True
        )
        self.assertTrue(result['was_escalated'])
        self.assertEqual(result['escalation_steps'], 2)

    def test_reasoning_narrative(self):
        """Reasoning should contain MSI and tier info."""
        result = self.engine.explain_risk_tier(
            msi=45.0, risk_tier="HIGH_VOLATILITY",
            base_tier="HIGH_VOLATILITY",
            escalation_reasons=[], enforcement_required=True
        )
        self.assertIn('45.0', result['tier_reasoning'])
        self.assertIn('HIGH_VOLATILITY', result['tier_reasoning'])

    def test_enforcement_noted(self):
        """Enforcement requirement should be noted in reasoning."""
        result = self.engine.explain_risk_tier(
            msi=30.0, risk_tier="SYSTEMIC_CRISIS",
            base_tier="SYSTEMIC_CRISIS",
            escalation_reasons=[], enforcement_required=True
        )
        self.assertIn('ENFORCEMENT', result['tier_reasoning'])

    def test_msi_bracket(self):
        """MSI bracket should describe the correct zone."""
        result = self.engine.explain_risk_tier(
            msi=85.0, risk_tier="NORMAL",
            base_tier="NORMAL",
            escalation_reasons=[], enforcement_required=False
        )
        self.assertIn('STABLE', result['msi_bracket'])


class TestNarrativeGeneration(unittest.TestCase):
    """Test human-readable narrative generation."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_basic_narrative(self):
        """Narrative should contain MSI info."""
        msi_exp = self.engine.explain_msi(70.0, 0.05, 10, 0.02, 30.0)
        narrative = self.engine.generate_narrative(msi_exp)
        self.assertIn('MARKET STABILITY INDEX', narrative)
        self.assertGreater(len(narrative), 50)

    def test_full_narrative(self):
        """Full narrative with all explanations."""
        msi_exp = self.engine.explain_msi(60.0, 0.1, 20, 0.05, 50.0)
        sev_exp = self.engine.explain_severity(45.0, 50.0, 0.05, 60.0)
        tier_exp = self.engine.explain_risk_tier(
            45.0, "SYSTEMIC_CRISIS", "HIGH_VOLATILITY",
            ["CRS > 70"], True
        )
        asset_rank = self.engine.rank_asset_systemic_impact({
            "AAPL": 85.0, "MSFT": 30.0, "GOOGL": 60.0
        })

        narrative = self.engine.generate_narrative(
            msi_exp, sev_exp, tier_exp, asset_rank
        )
        self.assertIn('MARKET STABILITY INDEX', narrative)
        self.assertIn('SEVERITY ASSESSMENT', narrative)
        self.assertIn('RISK TIER', narrative)
        self.assertIn('ASSET RISK RANKING', narrative)
        self.assertIn('MSFT', narrative)  # Highest risk asset


class TestInputValidation(unittest.TestCase):
    """Test input validation for all methods."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_msi_invalid_trust(self):
        with self.assertRaises(ValueError):
            self.engine.explain_msi(150.0, 0.0, 0, 0.0, 0.0)

    def test_msi_invalid_anomaly_rate(self):
        with self.assertRaises(ValueError):
            self.engine.explain_msi(80.0, -0.1, 0, 0.0, 0.0)

    def test_msi_invalid_anomalies_negative(self):
        with self.assertRaises(ValueError):
            self.engine.explain_msi(80.0, 0.0, -5, 0.0, 0.0)

    def test_msi_invalid_feed(self):
        with self.assertRaises(ValueError):
            self.engine.explain_msi(80.0, 0.0, 0, 2.0, 0.0)

    def test_msi_invalid_crs(self):
        with self.assertRaises(ValueError):
            self.engine.explain_msi(80.0, 0.0, 0, 0.0, 200.0)

    def test_msi_invalid_type(self):
        with self.assertRaises(TypeError):
            self.engine.explain_msi("80", 0.0, 0, 0.0, 0.0)

    def test_severity_invalid_msi(self):
        with self.assertRaises(ValueError):
            self.engine.explain_severity(-10.0, 0.0, 0.0, 80.0)

    def test_severity_invalid_type(self):
        with self.assertRaises(TypeError):
            self.engine.explain_severity("50", 0.0, 0.0, 80.0)


class TestCrossVerification(unittest.TestCase):
    """Cross-verify explainability output against actual engines."""

    def setUp(self):
        self.engine = ExplainabilityEngine()

    def test_msi_matches_actual_engine(self):
        """Explained MSI should match actual MarketStabilityIndex."""
        from systemic.market_stability_index import MarketStabilityIndex

        msi_calc = MarketStabilityIndex()
        actual = msi_calc.compute_msi(
            average_trust_score=75.0,
            market_anomaly_rate=0.08,
            total_anomalies=20,
            feed_mismatch_rate=0.03,
            contagion_risk_score=45.0
        )

        explained = self.engine.explain_msi(
            average_trust_score=75.0,
            market_anomaly_rate=0.08,
            total_anomalies=20,
            feed_mismatch_rate=0.03,
            contagion_risk_score=45.0
        )

        self.assertAlmostEqual(
            actual['msi_score'],
            explained['msi_final_score'],
            places=1
        )

    def test_severity_matches_actual_engine(self):
        """Explained severity should match IncidentIntelligenceEngine."""
        from governance.incident_intelligence_engine import (
            IncidentIntelligenceEngine
        )

        gov = IncidentIntelligenceEngine()
        incident = gov.create_systemic_incident(
            msi=50.0, contagion_risk_score=60.0,
            feed_mismatch_rate=0.04,
            average_trust_score=55.0,
            risk_tier="HIGH_VOLATILITY",
            recommended_action="ENABLE_TRADE_THROTTLING"
        )

        explained = self.engine.explain_severity(
            msi=50.0, contagion_risk_score=60.0,
            feed_mismatch_rate=0.04,
            average_trust_score=55.0
        )

        self.assertAlmostEqual(
            incident['severity_score'],
            explained['severity_score'],
            places=1
        )


class TestFullStackIntegration(unittest.TestCase):
    """Test full pipeline integration."""

    def test_end_to_end(self):
        """All engines → explainability should work."""
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

        # 1-5: Full pipeline
        fe = FeedIntegrityEngine(deviation_threshold=0.01)
        fe.register_feed('AAPL', 'yahoo')
        fe.register_feed('AAPL', 'bloomberg')
        now = datetime.utcnow()
        fe.update_price('AAPL', 'yahoo', 178.50, now)
        fe.update_price('AAPL', 'bloomberg', 178.55, now)
        feed_health = fe.get_global_feed_health()

        ce = ContagionEngine(window_size=10)
        np.random.seed(42)
        for i in range(15):
            ce.update_price('AAPL', 150.0 + i * 0.5)
            ce.update_price('MSFT', 300.0 + i * 0.3)
        contagion = ce.get_contagion_summary()

        msi_calc = MarketStabilityIndex()
        msi_result = msi_calc.compute_msi(
            average_trust_score=85.0,
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
            average_trust_score=85.0
        )

        gov = IncidentIntelligenceEngine()
        incident = gov.create_systemic_incident(
            msi=msi_result['msi_score'],
            contagion_risk_score=contagion['contagion_risk_score'],
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            average_trust_score=85.0,
            risk_tier=action['risk_tier'],
            recommended_action=action['recommended_action'],
            escalation_reasons=action['escalation_reasons']
        )

        # 6: Explainability
        exp = ExplainabilityEngine()

        msi_exp = exp.explain_msi(
            average_trust_score=85.0,
            market_anomaly_rate=0.02,
            total_anomalies=5,
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            contagion_risk_score=contagion['contagion_risk_score']
        )

        sev_exp = exp.explain_severity(
            msi=msi_result['msi_score'],
            contagion_risk_score=contagion['contagion_risk_score'],
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            average_trust_score=85.0
        )

        tier_exp = exp.explain_risk_tier(
            msi=msi_result['msi_score'],
            risk_tier=action['risk_tier'],
            base_tier=action['base_tier'],
            escalation_reasons=action['escalation_reasons'],
            enforcement_required=action['enforcement_required']
        )

        asset_rank = exp.rank_asset_systemic_impact({
            "AAPL": 85.0, "MSFT": 72.0, "GOOGL": 90.0
        })

        narrative = exp.generate_narrative(
            msi_exp, sev_exp, tier_exp, asset_rank
        )

        # Assertions
        self.assertAlmostEqual(
            msi_exp['msi_final_score'],
            msi_result['msi_score'], places=1
        )
        self.assertGreater(len(narrative), 100)
        self.assertEqual(len(asset_rank), 3)
        self.assertEqual(asset_rank[0]['symbol'], 'MSFT')


# ──────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("  EXPLAINABILITY ENGINE - TEST SUITE")
    print("=" * 70)
    print()
    unittest.main(verbosity=2)
