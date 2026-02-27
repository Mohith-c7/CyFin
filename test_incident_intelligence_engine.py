"""
Test Suite for Incident Intelligence & Governance Engine
==========================================================

Comprehensive tests covering:
- Incident creation and structure
- Severity score computation
- Regulatory classification
- Root cause chain generation
- UUID uniqueness
- JSON export
- Compliance report generation
- Incident querying and filtering
- Database persistence
- Input validation
- Full-stack integration (all modules)

Run with:
    python -m pytest test_incident_intelligence_engine.py -v -p no:asyncio
    OR
    python test_incident_intelligence_engine.py
"""

import sys
import os
import json
import unittest
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from governance.incident_intelligence_engine import (
    IncidentIntelligenceEngine,
    CLASSIFICATION_CRITICAL,
    CLASSIFICATION_HIGH,
    CLASSIFICATION_ELEVATED,
    CLASSIFICATION_NORMAL,
)


# ══════════════════════════════════════════════════════════════════════════
# Helper for creating test incidents quickly
# ══════════════════════════════════════════════════════════════════════════

def _make_incident(engine, **overrides):
    """Create a test incident with sensible defaults."""
    defaults = dict(
        msi=70.0,
        contagion_risk_score=30.0,
        feed_mismatch_rate=0.01,
        average_trust_score=75.0,
        risk_tier="ELEVATED_RISK",
        recommended_action="INCREASE_MONITORING",
        escalation_reasons=[]
    )
    defaults.update(overrides)
    return engine.create_systemic_incident(**defaults)


class TestIncidentCreation(unittest.TestCase):
    """Test basic incident creation and structure."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_incident_has_uuid(self):
        """Incident must have a valid UUID4 identifier."""
        inc = _make_incident(self.engine)
        # Should not raise
        parsed = uuid.UUID(inc['incident_id'], version=4)
        self.assertIsNotNone(parsed)

    def test_unique_uuids(self):
        """Each incident must have a unique UUID."""
        ids = set()
        for _ in range(20):
            inc = _make_incident(self.engine)
            ids.add(inc['incident_id'])
        self.assertEqual(len(ids), 20)

    def test_incident_has_timestamp(self):
        """Incident must have ISO 8601 timestamp."""
        inc = _make_incident(self.engine)
        self.assertIn('timestamp', inc)
        # Should parse without error
        from datetime import datetime
        datetime.fromisoformat(inc['timestamp'])

    def test_incident_has_all_required_fields(self):
        """Incident must contain all specified fields."""
        inc = _make_incident(self.engine)
        required = [
            'incident_id', 'timestamp', 'risk_tier',
            'msi_score', 'contagion_risk_score',
            'feed_mismatch_rate', 'average_trust_score',
            'recommended_action', 'escalation_reasons',
            'severity_score', 'regulatory_classification',
            'root_cause_chain', 'incident_sequence'
        ]
        for key in required:
            self.assertIn(key, inc, "Missing: %s" % key)

    def test_incident_sequence_increments(self):
        """Incident sequence must increment monotonically."""
        i1 = _make_incident(self.engine)
        i2 = _make_incident(self.engine)
        i3 = _make_incident(self.engine)
        self.assertEqual(i2['incident_sequence'],
                         i1['incident_sequence'] + 1)
        self.assertEqual(i3['incident_sequence'],
                         i2['incident_sequence'] + 1)

    def test_inputs_echoed_in_output(self):
        """Input values must appear in the output record."""
        inc = self.engine.create_systemic_incident(
            msi=55.0,
            contagion_risk_score=42.0,
            feed_mismatch_rate=0.015,
            average_trust_score=68.0,
            risk_tier="HIGH_VOLATILITY",
            recommended_action="ENABLE_TRADE_THROTTLING",
            escalation_reasons=["CRS exceeded threshold"]
        )
        self.assertEqual(inc['msi_score'], 55.0)
        self.assertEqual(inc['contagion_risk_score'], 42.0)
        self.assertAlmostEqual(inc['feed_mismatch_rate'], 0.015, places=4)
        self.assertEqual(inc['average_trust_score'], 68.0)
        self.assertEqual(inc['risk_tier'], "HIGH_VOLATILITY")
        self.assertEqual(inc['recommended_action'],
                         "ENABLE_TRADE_THROTTLING")
        self.assertEqual(inc['escalation_reasons'],
                         ["CRS exceeded threshold"])

    def test_default_escalation_reasons(self):
        """Escalation reasons should default to empty list."""
        inc = self.engine.create_systemic_incident(
            msi=70.0,
            contagion_risk_score=30.0,
            feed_mismatch_rate=0.01,
            average_trust_score=75.0,
            risk_tier="ELEVATED_RISK",
            recommended_action="INCREASE_MONITORING"
        )
        self.assertEqual(inc['escalation_reasons'], [])


class TestSeverityScore(unittest.TestCase):
    """Test severity score computation."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_perfect_conditions_low_severity(self):
        """MSI=100, CRS=0, feed=0, trust=100 should give severity 0."""
        inc = _make_incident(self.engine,
                             msi=100.0, contagion_risk_score=0.0,
                             feed_mismatch_rate=0.0,
                             average_trust_score=100.0,
                             risk_tier="NORMAL",
                             recommended_action="NO_ACTION")
        self.assertEqual(inc['severity_score'], 0.0)

    def test_worst_conditions_max_severity(self):
        """MSI=0, CRS=100, feed=1.0, trust=0 should give severity 100."""
        inc = _make_incident(self.engine,
                             msi=0.0, contagion_risk_score=100.0,
                             feed_mismatch_rate=1.0,
                             average_trust_score=0.0,
                             risk_tier="SYSTEMIC_CRISIS",
                             recommended_action="ACTIVATE_EMERGENCY_CONTROLS")
        self.assertEqual(inc['severity_score'], 100.0)

    def test_severity_formula_components(self):
        """Verify severity formula: 0.4*(100-MSI) + 0.3*CRS + 0.2*(FR*100) + 0.1*(100-trust)."""
        msi = 60.0
        crs = 50.0
        fr = 0.05
        trust = 70.0

        expected = (
            0.4 * (100 - msi)
            + 0.3 * crs
            + 0.2 * (fr * 100)
            + 0.1 * (100 - trust)
        )

        inc = _make_incident(self.engine,
                             msi=msi, contagion_risk_score=crs,
                             feed_mismatch_rate=fr,
                             average_trust_score=trust,
                             risk_tier="ELEVATED_RISK",
                             recommended_action="INCREASE_MONITORING")

        self.assertAlmostEqual(inc['severity_score'], expected, places=2)

    def test_severity_clamped_lower(self):
        """Severity should not go below 0."""
        inc = _make_incident(self.engine,
                             msi=100.0, contagion_risk_score=0.0,
                             feed_mismatch_rate=0.0,
                             average_trust_score=100.0,
                             risk_tier="NORMAL",
                             recommended_action="NO_ACTION")
        self.assertGreaterEqual(inc['severity_score'], 0.0)

    def test_severity_clamped_upper(self):
        """Severity should not exceed 100."""
        inc = _make_incident(self.engine,
                             msi=0.0, contagion_risk_score=100.0,
                             feed_mismatch_rate=1.0,
                             average_trust_score=0.0,
                             risk_tier="SYSTEMIC_CRISIS",
                             recommended_action="ACTIVATE_EMERGENCY_CONTROLS")
        self.assertLessEqual(inc['severity_score'], 100.0)


class TestRegulatoryClassification(unittest.TestCase):
    """Test regulatory classification logic."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_critical_classification(self):
        """Severity > 80 should classify as CRITICAL_MARKET_EVENT."""
        # severity = 0.4*(100-0) + 0.3*100 + 0.2*(1*100) + 0.1*(100-0) = 100
        inc = _make_incident(self.engine,
                             msi=0.0, contagion_risk_score=100.0,
                             feed_mismatch_rate=1.0,
                             average_trust_score=0.0,
                             risk_tier="SYSTEMIC_CRISIS",
                             recommended_action="ACTIVATE_EMERGENCY_CONTROLS")
        self.assertEqual(inc['regulatory_classification'],
                         CLASSIFICATION_CRITICAL)

    def test_high_risk_classification(self):
        """Severity 60-80 should classify as HIGH_RISK_EVENT."""
        # We need severity between 60 and 80
        # severity = 0.4*(100-30) + 0.3*50 + 0.2*5 + 0.1*(100-60) = 28+15+1+4 = 48
        # Let's try: msi=10, crs=80, feed=0.1, trust=30
        # severity = 0.4*90 + 0.3*80 + 0.2*10 + 0.1*70 = 36+24+2+7 = 69
        inc = _make_incident(self.engine,
                             msi=10.0, contagion_risk_score=80.0,
                             feed_mismatch_rate=0.10,
                             average_trust_score=30.0,
                             risk_tier="SYSTEMIC_CRISIS",
                             recommended_action="ACTIVATE_EMERGENCY_CONTROLS")
        self.assertEqual(inc['regulatory_classification'],
                         CLASSIFICATION_HIGH)

    def test_elevated_classification(self):
        """Severity 40-60 should classify as ELEVATED_MONITORING_EVENT."""
        # severity = 0.4*(100-50) + 0.3*30 + 0.2*5 + 0.1*(100-70) = 20+9+1+3 = 33
        # Try: msi=30, crs=60, feed=0.05, trust=50
        # sev = 0.4*70 + 0.3*60 + 0.2*5 + 0.1*50 = 28+18+1+5 = 52
        inc = _make_incident(self.engine,
                             msi=30.0, contagion_risk_score=60.0,
                             feed_mismatch_rate=0.05,
                             average_trust_score=50.0,
                             risk_tier="SYSTEMIC_CRISIS",
                             recommended_action="ACTIVATE_EMERGENCY_CONTROLS")
        self.assertEqual(inc['regulatory_classification'],
                         CLASSIFICATION_ELEVATED)

    def test_normal_classification(self):
        """Severity < 40 should classify as NORMAL_OPERATION."""
        inc = _make_incident(self.engine,
                             msi=90.0, contagion_risk_score=10.0,
                             feed_mismatch_rate=0.01,
                             average_trust_score=85.0,
                             risk_tier="NORMAL",
                             recommended_action="NO_ACTION")
        self.assertEqual(inc['regulatory_classification'],
                         CLASSIFICATION_NORMAL)


class TestRootCauseChain(unittest.TestCase):
    """Test root cause analysis chain generation."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_chain_has_all_layers(self):
        """Root cause chain must include all 4 analysis layers."""
        inc = _make_incident(self.engine)
        chain = inc['root_cause_chain']
        self.assertGreaterEqual(len(chain), 4)

        layers_found = set()
        for entry in chain:
            if entry.startswith("DATA_LAYER"):
                layers_found.add("DATA")
            elif entry.startswith("TRUST_LAYER"):
                layers_found.add("TRUST")
            elif entry.startswith("CONTAGION_LAYER"):
                layers_found.add("CONTAGION")
            elif entry.startswith("STABILITY_LAYER"):
                layers_found.add("STABILITY")

        expected = {"DATA", "TRUST", "CONTAGION", "STABILITY"}
        self.assertEqual(layers_found, expected)

    def test_chain_includes_escalation_reasons(self):
        """Chain should include escalation trigger reasons."""
        inc = _make_incident(self.engine,
                             escalation_reasons=[
                                 "CRS exceeded threshold",
                                 "Feed mismatch critical"
                             ])
        chain = inc['root_cause_chain']
        escalation_entries = [
            e for e in chain if e.startswith("ESCALATION")
        ]
        self.assertEqual(len(escalation_entries), 2)

    def test_chain_no_escalation_when_empty(self):
        """Chain should not have ESCALATION entries if none triggered."""
        inc = _make_incident(self.engine, escalation_reasons=[])
        chain = inc['root_cause_chain']
        escalation_entries = [
            e for e in chain if e.startswith("ESCALATION")
        ]
        self.assertEqual(len(escalation_entries), 0)

    def test_feed_critical_chain(self):
        """High feed mismatch should produce critical DATA_LAYER entry."""
        inc = _make_incident(self.engine, feed_mismatch_rate=0.05)
        data_entries = [
            e for e in inc['root_cause_chain']
            if e.startswith("DATA_LAYER")
        ]
        self.assertEqual(len(data_entries), 1)
        self.assertIn("integrity failure", data_entries[0])

    def test_low_trust_chain(self):
        """Low trust should produce critical TRUST_LAYER entry."""
        inc = _make_incident(self.engine, average_trust_score=30.0)
        trust_entries = [
            e for e in inc['root_cause_chain']
            if e.startswith("TRUST_LAYER")
        ]
        self.assertEqual(len(trust_entries), 1)
        self.assertIn("unreliable", trust_entries[0])


class TestExport(unittest.TestCase):
    """Test incident export functionality."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_export_to_json(self):
        """JSON export should produce valid JSON string."""
        inc = _make_incident(self.engine)
        json_str = self.engine.export_incident_to_json(
            inc['incident_id']
        )
        # Should parse without error
        parsed = json.loads(json_str)
        self.assertEqual(parsed['incident_id'], inc['incident_id'])

    def test_export_to_dict(self):
        """Dict export should return a copy of the incident."""
        inc = _make_incident(self.engine)
        exported = self.engine.export_incident_to_dict(
            inc['incident_id']
        )
        self.assertEqual(exported['incident_id'], inc['incident_id'])
        # Should be a new dict (copy)
        self.assertIsNot(exported, self.engine._incidents[inc['incident_id']])

    def test_export_invalid_id_raises(self):
        """Exporting non-existent ID should raise KeyError."""
        with self.assertRaises(KeyError):
            self.engine.export_incident_to_json("non-existent-id")

    def test_export_dict_invalid_id_raises(self):
        with self.assertRaises(KeyError):
            self.engine.export_incident_to_dict("non-existent-id")


class TestComplianceReport(unittest.TestCase):
    """Test compliance report generation."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_empty_report(self):
        """Report with no incidents should have zero counts."""
        report = self.engine.generate_compliance_report()
        self.assertEqual(report['summary']['total_incidents'], 0)
        self.assertEqual(report['summary']['average_severity'], 0.0)
        self.assertIn('report_id', report)
        self.assertIn('generated_at', report)

    def test_report_counts(self):
        """Report should count incidents correctly."""
        # Create 3 incidents of different severities
        _make_incident(self.engine,
                       msi=90.0, contagion_risk_score=5.0,
                       average_trust_score=90.0,
                       risk_tier="NORMAL",
                       recommended_action="NO_ACTION")
        _make_incident(self.engine,
                       msi=50.0, contagion_risk_score=40.0,
                       average_trust_score=60.0,
                       risk_tier="HIGH_VOLATILITY",
                       recommended_action="ENABLE_TRADE_THROTTLING")
        _make_incident(self.engine,
                       msi=10.0, contagion_risk_score=90.0,
                       feed_mismatch_rate=0.5,
                       average_trust_score=20.0,
                       risk_tier="SYSTEMIC_CRISIS",
                       recommended_action="ACTIVATE_EMERGENCY_CONTROLS")

        report = self.engine.generate_compliance_report()
        self.assertEqual(report['summary']['total_incidents'], 3)
        self.assertGreater(report['summary']['average_severity'], 0)
        self.assertGreater(report['summary']['max_severity'], 0)

    def test_report_classification_breakdown(self):
        """Report should break down by regulatory classification."""
        report = self.engine.generate_compliance_report()
        breakdown = report['summary']['classification_breakdown']
        self.assertIn(CLASSIFICATION_CRITICAL, breakdown)
        self.assertIn(CLASSIFICATION_HIGH, breakdown)
        self.assertIn(CLASSIFICATION_ELEVATED, breakdown)
        self.assertIn(CLASSIFICATION_NORMAL, breakdown)

    def test_report_limit(self):
        """Report should respect incident listing limit."""
        for _ in range(10):
            _make_incident(self.engine)
        report = self.engine.generate_compliance_report(limit=3)
        self.assertLessEqual(len(report['incidents']), 3)

    def test_report_newest_first(self):
        """Report incidents should be ordered newest first."""
        for msi in [90.0, 70.0, 50.0]:
            _make_incident(self.engine, msi=msi,
                           risk_tier="NORMAL" if msi >= 80 else "ELEVATED_RISK",
                           recommended_action="NO_ACTION" if msi >= 80 else "INCREASE_MONITORING")
        report = self.engine.generate_compliance_report()
        timestamps = [i['timestamp'] for i in report['incidents']]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))


class TestQuerying(unittest.TestCase):
    """Test incident querying methods."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_get_incident_by_id(self):
        """Should retrieve incident by UUID."""
        inc = _make_incident(self.engine)
        retrieved = self.engine.get_incident(inc['incident_id'])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['incident_id'], inc['incident_id'])

    def test_get_incident_missing(self):
        """Should return None for missing ID."""
        result = self.engine.get_incident("does-not-exist")
        self.assertIsNone(result)

    def test_get_all_incidents(self):
        """Should return all incidents newest first."""
        for _ in range(5):
            _make_incident(self.engine)
        all_inc = self.engine.get_all_incidents()
        self.assertEqual(len(all_inc), 5)
        # Verify ordering
        sequences = [i['incident_sequence'] for i in all_inc]
        self.assertEqual(sequences, sorted(sequences, reverse=True))

    def test_get_by_classification(self):
        """Should filter incidents by regulatory classification."""
        # Create a NORMAL one (low severity)
        _make_incident(self.engine,
                       msi=95.0, contagion_risk_score=0.0,
                       feed_mismatch_rate=0.0,
                       average_trust_score=95.0,
                       risk_tier="NORMAL",
                       recommended_action="NO_ACTION")
        # Create a CRITICAL one (high severity)
        _make_incident(self.engine,
                       msi=0.0, contagion_risk_score=100.0,
                       feed_mismatch_rate=1.0,
                       average_trust_score=0.0,
                       risk_tier="SYSTEMIC_CRISIS",
                       recommended_action="ACTIVATE_EMERGENCY_CONTROLS")

        normals = self.engine.get_incidents_by_classification(
            CLASSIFICATION_NORMAL
        )
        criticals = self.engine.get_incidents_by_classification(
            CLASSIFICATION_CRITICAL
        )

        self.assertEqual(len(normals), 1)
        self.assertEqual(len(criticals), 1)

    def test_incident_count(self):
        """Count should track total incidents."""
        self.assertEqual(self.engine.get_incident_count(), 0)
        _make_incident(self.engine)
        _make_incident(self.engine)
        self.assertEqual(self.engine.get_incident_count(), 2)


class TestDatabasePersistence(unittest.TestCase):
    """Test database persistence of governance incidents."""

    def test_incident_persisted_to_db(self):
        """Incidents should be stored in governance_incidents table."""
        from database.db_manager import DatabaseManager

        db_path = 'test_governance.db'
        try:
            db = DatabaseManager(db_path)
            engine = IncidentIntelligenceEngine(db_manager=db)

            inc = engine.create_systemic_incident(
                msi=20.0,
                contagion_risk_score=80.0,
                feed_mismatch_rate=0.05,
                average_trust_score=30.0,
                risk_tier="SYSTEMIC_CRISIS",
                recommended_action="ACTIVATE_EMERGENCY_CONTROLS",
                escalation_reasons=["CRS > 70"]
            )

            # Verify in governance_incidents table
            cursor = db.conn.cursor()
            cursor.execute(
                "SELECT * FROM governance_incidents WHERE incident_id = ?",
                (inc['incident_id'],)
            )
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row['risk_tier'], 'SYSTEMIC_CRISIS')
            self.assertAlmostEqual(row['severity_score'],
                                   inc['severity_score'], places=1)

            # Verify system_event also logged
            stats = db.get_statistics()
            self.assertGreater(stats['system_events_count'], 0)

            db.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_works_without_database(self):
        """Engine should work without a database manager."""
        engine = IncidentIntelligenceEngine()
        inc = _make_incident(engine)
        self.assertIsNotNone(inc['incident_id'])

    def test_multiple_incidents_persisted(self):
        """Multiple incidents should all be persisted."""
        from database.db_manager import DatabaseManager

        db_path = 'test_governance_multi.db'
        try:
            db = DatabaseManager(db_path)
            engine = IncidentIntelligenceEngine(db_manager=db)

            for _ in range(5):
                _make_incident(engine)

            cursor = db.conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM governance_incidents"
            )
            count = cursor.fetchone()['count']
            self.assertEqual(count, 5)

            db.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestInputValidation(unittest.TestCase):
    """Test input validation."""

    def setUp(self):
        self.engine = IncidentIntelligenceEngine()

    def test_invalid_msi_range(self):
        with self.assertRaises(ValueError):
            _make_incident(self.engine, msi=150.0)

    def test_invalid_crs_range(self):
        with self.assertRaises(ValueError):
            _make_incident(self.engine, contagion_risk_score=-10.0)

    def test_invalid_feed_range(self):
        with self.assertRaises(ValueError):
            _make_incident(self.engine, feed_mismatch_rate=2.0)

    def test_invalid_trust_range(self):
        with self.assertRaises(ValueError):
            _make_incident(self.engine, average_trust_score=-5.0)

    def test_invalid_risk_tier(self):
        with self.assertRaises(ValueError):
            _make_incident(self.engine, risk_tier="UNKNOWN_TIER")

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            _make_incident(self.engine,
                           recommended_action="DO_NOTHING")

    def test_invalid_msi_type(self):
        with self.assertRaises(TypeError):
            _make_incident(self.engine, msi="high")

    def test_invalid_tier_type(self):
        with self.assertRaises(TypeError):
            _make_incident(self.engine, risk_tier=42)


class TestFullStackIntegration(unittest.TestCase):
    """Test full pipeline: Feed + Contagion + MSI + Action + Governance."""

    def test_end_to_end(self):
        """Complete pipeline should produce valid governance incident."""
        import numpy as np
        from datetime import datetime
        from feed_validation.feed_integrity_engine import (
            FeedIntegrityEngine
        )
        from systemic.contagion_engine import ContagionEngine
        from systemic.market_stability_index import MarketStabilityIndex
        from systemic.systemic_action_engine import SystemicActionEngine

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
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            contagion_risk_score=contagion['contagion_risk_score']
        )

        # 4. Action Engine
        ae = SystemicActionEngine()
        action = ae.evaluate_systemic_risk(
            msi=msi_result['msi_score'],
            contagion_risk_score=contagion['contagion_risk_score'],
            feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            average_trust_score=85.0
        )

        # 5. Governance Engine
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

        # Validate complete pipeline
        self.assertIn(incident['regulatory_classification'], [
            CLASSIFICATION_CRITICAL, CLASSIFICATION_HIGH,
            CLASSIFICATION_ELEVATED, CLASSIFICATION_NORMAL
        ])
        self.assertGreaterEqual(incident['severity_score'], 0)
        self.assertLessEqual(incident['severity_score'], 100)
        self.assertGreaterEqual(len(incident['root_cause_chain']), 4)

        # Export should work
        json_str = gov.export_incident_to_json(incident['incident_id'])
        parsed = json.loads(json_str)
        self.assertEqual(parsed['incident_id'], incident['incident_id'])

        # Compliance report should include this incident
        report = gov.generate_compliance_report()
        self.assertEqual(report['summary']['total_incidents'], 1)


# ──────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("  INCIDENT INTELLIGENCE ENGINE - TEST SUITE")
    print("=" * 70)
    print()
    unittest.main(verbosity=2)
