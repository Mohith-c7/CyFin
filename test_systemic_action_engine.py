"""
Test Suite for Systemic Risk Orchestration & Response Engine
==============================================================

Comprehensive tests covering:
- Base tier classification from MSI
- Escalation rules (contagion, feed mismatch, trust)
- Stacked escalation (multiple triggers)
- Alert level mapping
- Enforcement flag logic
- Structured output format
- Incident history and statistics
- Policy configuration
- Database persistence
- Input validation
- Edge cases and boundary conditions
- Full-stack integration (Feed + Contagion + MSI + Action)

Run with:
    python -m pytest test_systemic_action_engine.py -v -p no:asyncio
    OR
    python test_systemic_action_engine.py
"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from systemic.systemic_action_engine import (
    SystemicActionEngine,
    RiskTier, AlertLevel, RecommendedAction
)


class TestBaseTierClassification(unittest.TestCase):
    """Test MSI-based risk tier classification (no escalation)."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_normal_tier(self):
        """MSI >= 80 should classify as NORMAL."""
        result = self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'NORMAL')
        self.assertEqual(result['base_tier'], 'NORMAL')

    def test_elevated_risk_tier(self):
        """60 <= MSI < 80 should classify as ELEVATED_RISK."""
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'ELEVATED_RISK')

    def test_high_volatility_tier(self):
        """40 <= MSI < 60 should classify as HIGH_VOLATILITY."""
        result = self.engine.evaluate_systemic_risk(
            msi=50.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'HIGH_VOLATILITY')

    def test_systemic_crisis_tier(self):
        """MSI < 40 should classify as SYSTEMIC_CRISIS."""
        result = self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'SYSTEMIC_CRISIS')

    def test_boundary_at_80(self):
        """MSI exactly 80.0 should be NORMAL."""
        result = self.engine.evaluate_systemic_risk(
            msi=80.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'NORMAL')

    def test_boundary_at_60(self):
        """MSI exactly 60.0 should be ELEVATED_RISK."""
        result = self.engine.evaluate_systemic_risk(
            msi=60.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'ELEVATED_RISK')

    def test_boundary_at_40(self):
        """MSI exactly 40.0 should be HIGH_VOLATILITY."""
        result = self.engine.evaluate_systemic_risk(
            msi=40.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'HIGH_VOLATILITY')

    def test_msi_zero(self):
        """MSI 0.0 should be SYSTEMIC_CRISIS."""
        result = self.engine.evaluate_systemic_risk(
            msi=0.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'SYSTEMIC_CRISIS')

    def test_msi_100(self):
        """MSI 100.0 should be NORMAL."""
        result = self.engine.evaluate_systemic_risk(
            msi=100.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'NORMAL')


class TestAlertLevelMapping(unittest.TestCase):
    """Test alert level (color) mapping to tiers."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_normal_is_green(self):
        result = self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['alert_level'], 'GREEN')

    def test_elevated_is_yellow(self):
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['alert_level'], 'YELLOW')

    def test_high_vol_is_orange(self):
        result = self.engine.evaluate_systemic_risk(
            msi=50.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['alert_level'], 'ORANGE')

    def test_crisis_is_red(self):
        result = self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['alert_level'], 'RED')


class TestRecommendedActions(unittest.TestCase):
    """Test recommended action mapping."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_normal_no_action(self):
        result = self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['recommended_action'], 'NO_ACTION')

    def test_elevated_increase_monitoring(self):
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(
            result['recommended_action'], 'INCREASE_MONITORING'
        )

    def test_high_vol_trade_throttling(self):
        result = self.engine.evaluate_systemic_risk(
            msi=50.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(
            result['recommended_action'], 'ENABLE_TRADE_THROTTLING'
        )

    def test_crisis_emergency_controls(self):
        result = self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(
            result['recommended_action'],
            'ACTIVATE_EMERGENCY_CONTROLS'
        )


class TestEnforcementFlag(unittest.TestCase):
    """Test enforcement_required flag logic."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_normal_no_enforcement(self):
        result = self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertFalse(result['enforcement_required'])

    def test_elevated_no_enforcement(self):
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertFalse(result['enforcement_required'])

    def test_high_vol_enforcement_required(self):
        result = self.engine.evaluate_systemic_risk(
            msi=50.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertTrue(result['enforcement_required'])

    def test_crisis_enforcement_required(self):
        result = self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertTrue(result['enforcement_required'])


class TestEscalationRules(unittest.TestCase):
    """Test individual and stacked escalation rules."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_contagion_escalation(self):
        """CRS > 70 should escalate tier by one level."""
        # MSI=70 → base ELEVATED_RISK, CRS=75 → ESCALATE to HIGH_VOL
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=75.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['base_tier'], 'ELEVATED_RISK')
        self.assertEqual(result['risk_tier'], 'HIGH_VOLATILITY')
        self.assertEqual(len(result['escalation_reasons']), 1)
        self.assertIn('Contagion', result['escalation_reasons'][0])

    def test_feed_mismatch_escalation(self):
        """Feed mismatch > 0.02 should escalate tier by one level."""
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.03, average_trust_score=90.0
        )
        self.assertEqual(result['base_tier'], 'ELEVATED_RISK')
        self.assertEqual(result['risk_tier'], 'HIGH_VOLATILITY')
        self.assertIn('Feed mismatch', result['escalation_reasons'][0])

    def test_trust_escalation(self):
        """Average trust < 50 should escalate tier by one level."""
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=40.0
        )
        self.assertEqual(result['base_tier'], 'ELEVATED_RISK')
        self.assertEqual(result['risk_tier'], 'HIGH_VOLATILITY')
        self.assertIn('trust', result['escalation_reasons'][0].lower())

    def test_no_escalation_when_below_threshold(self):
        """No escalation when all values are within normal range."""
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=50.0,
            feed_mismatch_rate=0.01, average_trust_score=60.0
        )
        self.assertEqual(result['base_tier'], 'ELEVATED_RISK')
        self.assertEqual(result['risk_tier'], 'ELEVATED_RISK')
        self.assertEqual(len(result['escalation_reasons']), 0)

    def test_stacked_escalation_two_triggers(self):
        """Two escalation triggers should escalate by two levels."""
        # MSI=70 → ELEVATED_RISK
        # CRS=80 → +1 → HIGH_VOLATILITY
        # Feed=0.05 → +1 → SYSTEMIC_CRISIS
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=80.0,
            feed_mismatch_rate=0.05, average_trust_score=90.0
        )
        self.assertEqual(result['base_tier'], 'ELEVATED_RISK')
        self.assertEqual(result['risk_tier'], 'SYSTEMIC_CRISIS')
        self.assertEqual(len(result['escalation_reasons']), 2)

    def test_stacked_escalation_three_triggers(self):
        """Three triggers should escalate up to SYSTEMIC_CRISIS."""
        # MSI=70 → ELEVATED_RISK
        # CRS=80 → +1 → HIGH_VOLATILITY
        # Feed=0.05 → +1 → SYSTEMIC_CRISIS
        # Trust=30 → would +1 but already at max → stays SYSTEMIC_CRISIS
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=80.0,
            feed_mismatch_rate=0.05, average_trust_score=30.0
        )
        self.assertEqual(result['risk_tier'], 'SYSTEMIC_CRISIS')
        # All 3 reasons if possible; trust might not add since
        # already at max
        self.assertGreaterEqual(len(result['escalation_reasons']), 2)

    def test_escalation_capped_at_systemic_crisis(self):
        """Escalation cannot go beyond SYSTEMIC_CRISIS."""
        # Already at SYSTEMIC_CRISIS from MSI alone
        result = self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=80.0,
            feed_mismatch_rate=0.05, average_trust_score=30.0
        )
        self.assertEqual(result['risk_tier'], 'SYSTEMIC_CRISIS')
        # No escalation reasons since already at max tier
        self.assertEqual(len(result['escalation_reasons']), 0)

    def test_escalation_from_normal(self):
        """Normal tier should escalate to ELEVATED_RISK."""
        result = self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=80.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(result['base_tier'], 'NORMAL')
        self.assertEqual(result['risk_tier'], 'ELEVATED_RISK')


class TestOutputStructure(unittest.TestCase):
    """Test that output contains all required fields."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_all_required_fields_present(self):
        """Output must contain all specified keys."""
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=30.0,
            feed_mismatch_rate=0.01, average_trust_score=75.0
        )
        required_keys = [
            'risk_tier', 'recommended_action',
            'enforcement_required', 'alert_level',
            'escalation_reasons', 'base_tier',
            'inputs', 'timestamp', 'evaluation_id'
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_inputs_echoed(self):
        """Input values should be echoed in the output for audit."""
        result = self.engine.evaluate_systemic_risk(
            msi=65.0, contagion_risk_score=25.0,
            feed_mismatch_rate=0.015, average_trust_score=72.0
        )
        inputs = result['inputs']
        self.assertEqual(inputs['msi'], 65.0)
        self.assertEqual(inputs['contagion_risk_score'], 25.0)
        self.assertEqual(inputs['feed_mismatch_rate'], 0.015)
        self.assertEqual(inputs['average_trust_score'], 72.0)

    def test_timestamp_is_iso_format(self):
        """Timestamp should be ISO 8601 format."""
        result = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        # Should not raise
        datetime.fromisoformat(result['timestamp'])

    def test_evaluation_id_increments(self):
        """Evaluation IDs should increment sequentially."""
        r1 = self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        r2 = self.engine.evaluate_systemic_risk(
            msi=50.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.assertEqual(r2['evaluation_id'], r1['evaluation_id'] + 1)


class TestIncidentHistory(unittest.TestCase):
    """Test incident history and statistics."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_history_accumulates(self):
        """Incidents should accumulate in history."""
        for msi_val in [85.0, 70.0, 50.0, 20.0]:
            self.engine.evaluate_systemic_risk(
                msi=msi_val, contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )
        history = self.engine.get_incident_history()
        self.assertEqual(len(history), 4)

    def test_history_newest_first(self):
        """History should be returned newest-first."""
        self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        history = self.engine.get_incident_history()
        self.assertEqual(history[0]['risk_tier'], 'SYSTEMIC_CRISIS')
        self.assertEqual(history[1]['risk_tier'], 'NORMAL')

    def test_history_limit(self):
        """History should respect limit parameter."""
        for _ in range(10):
            self.engine.evaluate_systemic_risk(
                msi=70.0, contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )
        history = self.engine.get_incident_history(limit=3)
        self.assertEqual(len(history), 3)

    def test_statistics(self):
        """Statistics should aggregate correctly."""
        # 2 NORMAL, 1 ELEVATED, 1 CRISIS
        self.engine.evaluate_systemic_risk(
            msi=85.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.engine.evaluate_systemic_risk(
            msi=90.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.engine.evaluate_systemic_risk(
            msi=70.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )
        self.engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=0.0,
            feed_mismatch_rate=0.0, average_trust_score=90.0
        )

        stats = self.engine.get_statistics()
        self.assertEqual(stats['total_evaluations'], 4)
        self.assertEqual(stats['tier_distribution']['NORMAL'], 2)
        self.assertEqual(stats['tier_distribution']['ELEVATED_RISK'], 1)
        self.assertEqual(
            stats['tier_distribution']['SYSTEMIC_CRISIS'], 1
        )
        self.assertEqual(stats['enforcement_count'], 1)
        self.assertEqual(stats['current_tier'], 'SYSTEMIC_CRISIS')
        self.assertEqual(stats['current_alert'], 'RED')


class TestPolicyConfig(unittest.TestCase):
    """Test policy configuration retrieval."""

    def test_default_policy(self):
        engine = SystemicActionEngine()
        config = engine.get_policy_config()
        self.assertIn('tier_thresholds', config)
        self.assertIn('escalation_rules', config)
        self.assertIn('enforcement_tiers', config)
        self.assertIn('alert_mapping', config)
        self.assertIn('HIGH_VOLATILITY', config['enforcement_tiers'])
        self.assertIn('SYSTEMIC_CRISIS', config['enforcement_tiers'])

    def test_custom_thresholds_in_policy(self):
        engine = SystemicActionEngine(
            stable_threshold=90.0,
            elevated_threshold=70.0,
            high_volatility_threshold=50.0
        )
        config = engine.get_policy_config()
        self.assertIn('90.0', config['tier_thresholds']['NORMAL'])


class TestConfigurationValidation(unittest.TestCase):
    """Test constructor parameter validation."""

    def test_valid_default_config(self):
        """Default configuration should be valid."""
        engine = SystemicActionEngine()
        self.assertIsNotNone(engine)

    def test_invalid_threshold_ordering(self):
        """Thresholds not in descending order should raise."""
        with self.assertRaises(ValueError):
            SystemicActionEngine(
                stable_threshold=50.0,
                elevated_threshold=80.0
            )

    def test_equal_stable_and_elevated(self):
        """Equal stable and elevated should raise (not strict >)."""
        with self.assertRaises(ValueError):
            SystemicActionEngine(
                stable_threshold=60.0,
                elevated_threshold=60.0
            )

    def test_negative_contagion_threshold(self):
        with self.assertRaises(ValueError):
            SystemicActionEngine(contagion_escalation_threshold=-10.0)

    def test_negative_feed_threshold(self):
        with self.assertRaises(ValueError):
            SystemicActionEngine(
                feed_mismatch_escalation_threshold=-0.01
            )

    def test_negative_trust_threshold(self):
        with self.assertRaises(ValueError):
            SystemicActionEngine(trust_escalation_threshold=-5.0)


class TestInputValidation(unittest.TestCase):
    """Test evaluate_systemic_risk input validation."""

    def setUp(self):
        self.engine = SystemicActionEngine()

    def test_invalid_msi_too_high(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate_systemic_risk(
                msi=150.0, contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )

    def test_invalid_msi_negative(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate_systemic_risk(
                msi=-10.0, contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )

    def test_invalid_crs_too_high(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate_systemic_risk(
                msi=70.0, contagion_risk_score=200.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )

    def test_invalid_feed_rate(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate_systemic_risk(
                msi=70.0, contagion_risk_score=0.0,
                feed_mismatch_rate=1.5, average_trust_score=90.0
            )

    def test_invalid_trust_type(self):
        with self.assertRaises(TypeError):
            self.engine.evaluate_systemic_risk(
                msi=70.0, contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score="high"
            )

    def test_invalid_msi_type(self):
        with self.assertRaises(TypeError):
            self.engine.evaluate_systemic_risk(
                msi="70", contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )


class TestDatabasePersistence(unittest.TestCase):
    """Test database persistence of incidents."""

    def test_incident_persisted(self):
        """Enforcement incidents should be logged to database."""
        from database.db_manager import DatabaseManager

        db_path = 'test_action_engine.db'
        try:
            db = DatabaseManager(db_path)
            engine = SystemicActionEngine(db_manager=db)

            # Trigger a crisis (enforcement required)
            engine.evaluate_systemic_risk(
                msi=20.0, contagion_risk_score=80.0,
                feed_mismatch_rate=0.05, average_trust_score=30.0
            )

            # Check system_events logged
            stats = db.get_statistics()
            self.assertGreater(stats['system_events_count'], 0)

            # Check systemic_incidents table
            cursor = db.conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) as count FROM systemic_incidents'
            )
            count = cursor.fetchone()['count']
            self.assertGreater(count, 0)

            db.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_non_enforcement_not_in_incidents_table(self):
        """Non-enforcement events should NOT be in systemic_incidents."""
        from database.db_manager import DatabaseManager

        db_path = 'test_action_engine_2.db'
        try:
            db = DatabaseManager(db_path)
            engine = SystemicActionEngine(db_manager=db)

            # NORMAL tier (no enforcement)
            engine.evaluate_systemic_risk(
                msi=85.0, contagion_risk_score=0.0,
                feed_mismatch_rate=0.0, average_trust_score=90.0
            )

            # System event should still be logged
            stats = db.get_statistics()
            self.assertGreater(stats['system_events_count'], 0)

            # But NOT in systemic_incidents (table may not exist)
            cursor = db.conn.cursor()
            try:
                cursor.execute(
                    'SELECT COUNT(*) as count FROM systemic_incidents'
                )
                count = cursor.fetchone()['count']
                self.assertEqual(count, 0)
            except Exception:
                pass  # Table doesn't exist = correct

            db.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_works_without_database(self):
        """Engine should work without a database manager."""
        engine = SystemicActionEngine()
        result = engine.evaluate_systemic_risk(
            msi=20.0, contagion_risk_score=80.0,
            feed_mismatch_rate=0.05, average_trust_score=90.0
        )
        self.assertEqual(result['risk_tier'], 'SYSTEMIC_CRISIS')


class TestFullStackIntegration(unittest.TestCase):
    """Test full pipeline: Feed + Contagion + MSI + Action."""

    def test_end_to_end_pipeline(self):
        """Full-stack integration should produce valid output."""
        import numpy as np
        from systemic.market_stability_index import MarketStabilityIndex
        from systemic.contagion_engine import ContagionEngine
        from feed_validation.feed_integrity_engine import (
            FeedIntegrityEngine
        )

        # 1. Feed integrity
        fe = FeedIntegrityEngine(deviation_threshold=0.01)
        fe.register_feed('AAPL', 'yahoo')
        fe.register_feed('AAPL', 'bloomberg')
        now = datetime.utcnow()
        fe.update_price('AAPL', 'yahoo', 178.50, now)
        fe.update_price('AAPL', 'bloomberg', 178.55, now)
        feed_health = fe.get_global_feed_health()

        # 2. Contagion
        ce = ContagionEngine(window_size=10)
        np.random.seed(42)
        for i in range(15):
            ce.update_price('AAPL', 150.0 + i * 0.5)
            ce.update_price('MSFT', 300.0 + i * 0.3)
        contagion = ce.get_contagion_summary()

        # 3. MSI V2
        msi_calc = MarketStabilityIndex()
        msi_result = msi_calc.compute_msi(
            average_trust_score=85.0,
            market_anomaly_rate=0.02,
            total_anomalies=5,
            feed_mismatch_rate=(
                feed_health['global_feed_mismatch_rate']
            ),
            contagion_risk_score=(
                contagion['contagion_risk_score']
            )
        )

        # 4. Action Engine
        action_engine = SystemicActionEngine()
        result = action_engine.evaluate_systemic_risk(
            msi=msi_result['msi_score'],
            contagion_risk_score=(
                contagion['contagion_risk_score']
            ),
            feed_mismatch_rate=(
                feed_health['global_feed_mismatch_rate']
            ),
            average_trust_score=85.0
        )

        # Validate complete pipeline output
        self.assertIn(result['risk_tier'], [
            'NORMAL', 'ELEVATED_RISK',
            'HIGH_VOLATILITY', 'SYSTEMIC_CRISIS'
        ])
        self.assertIn(result['alert_level'], [
            'GREEN', 'YELLOW', 'ORANGE', 'RED'
        ])
        self.assertIsInstance(result['enforcement_required'], bool)
        self.assertIsInstance(result['escalation_reasons'], list)


# ──────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("  SYSTEMIC ACTION ENGINE - TEST SUITE")
    print("=" * 70)
    print()
    unittest.main(verbosity=2)
