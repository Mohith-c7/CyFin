"""
Incident Intelligence & Governance Engine
============================================

Production-grade module for generating structured, regulator-ready
systemic risk incident records with full forensic traceability.

Governance Philosophy:
    In capital markets, the most dangerous moment is not the crisis
    itself—it is the post-crisis audit when regulators ask:

        "What did you know, when did you know it, and what did you do?"

    Every financial institution operating algorithmic infrastructure
    must maintain an unbroken chain of evidence from detection
    through classification to enforcement. This module provides
    that chain by:

    1. **Capturing**: Recording every systemic risk evaluation with
       full forensic context—inputs, computations, and decisions.

    2. **Classifying**: Assigning severity scores and regulatory
       classifications that map directly to compliance obligations.

    3. **Linking**: Connecting individual data points (anomalies,
       feed issues, contagion signals) to the systemic picture,
       creating root-cause traceability.

    4. **Persisting**: Writing audit-grade records to the database
       with tamper-evident UUIDs and ISO timestamps.

    5. **Exporting**: Producing structured JSON/dict reports suitable
       for regulatory submission, board reporting, and compliance
       review.

Financial Regulatory Relevance:
    This module directly supports compliance with:

    - **MiFID II (EU)**: Article 17 requires algorithmic trading
      firms to maintain records of all trading decisions and the
      market conditions that influenced them. Incident records
      provide this evidence.

    - **SEC Rule 15c3-5 (US)**: Requires pre-trade risk controls
      and documentation of market access risk management. The
      severity score and enforcement records satisfy this.

    - **Basel III / CRD IV**: Operational risk capital charges
      require documented incident response procedures and
      loss event databases. This module generates the incident
      records for that database.

    - **IOSCO Principles for Financial Benchmarks**: Requires
      benchmark administrators to maintain audit trails and
      incident logs. Our feed integrity → contagion → MSI chain
      constitutes a benchmark integrity framework.

    - **DORA (EU Digital Operational Resilience Act)**: Requires
      ICT incident reporting with severity classification and
      root cause analysis. This module's regulatory classification
      maps directly to DORA severity levels.

Importance of Audit Trails in Capital Markets:
    Audit trails serve three critical functions:

    1. **Regulatory Defense**: When regulators investigate, the
       quality of your audit trail determines whether you face
       a caution or a fine. Structured incident records with
       clear cause-effect chains are the gold standard.

    2. **Post-Incident Learning**: Root cause analysis requires
       forensic reconstruction of the sequence of events. UUID-
       linked incident chains enable time-travel debugging.

    3. **Continuous Improvement**: Incident statistics reveal
       patterns—which feeds fail most, which assets trigger
       contagion, which thresholds need tuning. This is the
       feedback loop that makes the system smarter over time.

Integration Points:
    Consumes output from SystemicActionEngine:
    - risk_tier, recommended_action, escalation_reasons
    - MSI, CRS, feed_mismatch_rate, average_trust_score

    Persists to DatabaseManager:
    - governance_incidents table (auto-created)
    - system_events table (via log_system_event)

    Exports via:
    - export_incident_to_json() → JSON string
    - export_incident_to_dict() → Python dict
    - generate_compliance_report() → multi-incident summary

Author: CyFin Team
Version: 1.0.0
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(logging.NullHandler())


# ══════════════════════════════════════════════════════════════════════════
# Regulatory Classification Constants
# ══════════════════════════════════════════════════════════════════════════

CLASSIFICATION_CRITICAL = "CRITICAL_MARKET_EVENT"
CLASSIFICATION_HIGH = "HIGH_RISK_EVENT"
CLASSIFICATION_ELEVATED = "ELEVATED_MONITORING_EVENT"
CLASSIFICATION_NORMAL = "NORMAL_OPERATION"

SEVERITY_CRITICAL_THRESHOLD = 80.0
SEVERITY_HIGH_THRESHOLD = 60.0
SEVERITY_ELEVATED_THRESHOLD = 40.0


class IncidentIntelligenceEngine:
    """
    Generates structured, regulator-ready systemic risk incident records
    with full forensic traceability and audit compliance.

    This engine sits at the apex of the CyFin risk intelligence
    pipeline, consuming output from all upstream modules and
    producing compliance-grade documentation of every systemic
    risk evaluation.

    Architecture::

        ┌──────────────────────────────────────────────────────┐
        │          INCIDENT INTELLIGENCE ENGINE                │
        │                                                      │
        │  Inputs:                     Outputs:                │
        │  ──────                      ───────                 │
        │  MSI score                   UUID incident record    │
        │  Contagion Risk Score        Severity score           │
        │  Feed mismatch rate          Regulatory class         │
        │  Average trust score         Root cause chain         │
        │  Risk tier                   JSON export              │
        │  Recommended action          Compliance report        │
        │  Escalation reasons          Database persistence     │
        └──────────────────────────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
        ┌─────▼─────┐ ┌──▼──────┐ ┌──▼──────────┐
        │ Database  │ │ JSON    │ │ Compliance  │
        │ Audit     │ │ Export  │ │ Reports     │
        │ Trail     │ │         │ │             │
        └───────────┘ └─────────┘ └─────────────┘

    Severity Score Formula:
        severity = (
            0.4 × (100 - MSI)              [Market instability]
          + 0.3 × contagion_risk_score       [Contagion weight]
          + 0.2 × (feed_mismatch_rate × 100) [Data integrity]
          + 0.1 × (100 - average_trust)      [Trust deficit]
        )

        Clamped to [0, 100].

        Weight rationale:
        - Market instability (40%): Composite MSI already aggregates
          multiple signals, making it the most informative single
          metric. Its complement (100 - MSI) measures distance
          from stability.
        - Contagion (30%): Cross-asset contagion is the primary
          systemic amplifier; high weight because contagion events
          escalate nonlinearly.
        - Feed integrity (20%): Data corruption undermines all
          downstream analytics but is typically recoverable.
        - Trust deficit (10%): Slow-moving indicator that
          contextualizes long-term data quality trends.

    Regulatory Classification:
        severity > 80  → CRITICAL_MARKET_EVENT
        60-80          → HIGH_RISK_EVENT
        40-60          → ELEVATED_MONITORING_EVENT
        < 40           → NORMAL_OPERATION

    Thread Safety:
        Incident creation is stateless per call. The in-memory
        incident store uses append-only semantics, safe for
        concurrent reads. Database persistence is transactional.

    Attributes:
        db_manager: Optional DatabaseManager for audit persistence.

    Usage Example::

        >>> from governance import IncidentIntelligenceEngine
        >>> engine = IncidentIntelligenceEngine(db_manager=db)
        >>> incident = engine.create_systemic_incident(
        ...     msi=45.0,
        ...     contagion_risk_score=65.0,
        ...     feed_mismatch_rate=0.03,
        ...     average_trust_score=55.0,
        ...     risk_tier="HIGH_VOLATILITY",
        ...     recommended_action="ENABLE_TRADE_THROTTLING",
        ...     escalation_reasons=["CRS > 70"]
        ... )
        >>> print(incident['incident_id'])
        >>> print(incident['regulatory_classification'])
        >>> json_str = engine.export_incident_to_json(
        ...     incident['incident_id']
        ... )
    """

    # ──────────────────────────────────────────────────────────────────
    # Severity formula weights
    # ──────────────────────────────────────────────────────────────────
    WEIGHT_MSI_COMPLEMENT = 0.4
    WEIGHT_CONTAGION = 0.3
    WEIGHT_FEED_MISMATCH = 0.2
    WEIGHT_TRUST_DEFICIT = 0.1

    SEVERITY_MIN = 0.0
    SEVERITY_MAX = 100.0

    def __init__(
        self,
        db_manager: Optional[Any] = None
    ):
        """
        Initialize the Incident Intelligence & Governance Engine.

        Args:
            db_manager: Optional DatabaseManager instance for
                persisting incident records to the audit database.
                If None, incidents are stored in-memory only and
                logged via Python logging.

        The engine maintains an in-memory incident store indexed
        by UUID for fast retrieval and export. For production
        deployments, always provide a db_manager to ensure
        durable audit trails that survive process restarts.
        """
        self.db_manager = db_manager

        # In-memory incident store: incident_id (str) → incident dict
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._incident_count: int = 0
        self._max_in_memory: int = 5000

        logger.info(
            "IncidentIntelligenceEngine initialized | db=%s",
            "connected" if db_manager else "in-memory only"
        )

    # ──────────────────────────────────────────────────────────────────
    # Core API: Incident Creation
    # ──────────────────────────────────────────────────────────────────

    def create_systemic_incident(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float,
        risk_tier: str,
        recommended_action: str,
        escalation_reasons: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a structured systemic risk incident record.

        This is the primary entry point. It:
        1. Validates all inputs
        2. Generates a unique incident UUID
        3. Computes the severity score
        4. Determines regulatory classification
        5. Constructs the forensic root-cause chain
        6. Persists to database if configured
        7. Stores in in-memory index
        8. Returns the complete incident record

        The incident record is designed to be self-contained—a
        regulator should be able to understand the full context
        of the event from the record alone, without needing to
        query additional systems.

        Args:
            msi (float): Market Stability Index score (0-100).

            contagion_risk_score (float): Cross-asset contagion
                risk score (0-100).

            feed_mismatch_rate (float): Global feed mismatch
                rate (0-1).

            average_trust_score (float): Average trust score
                across all monitored symbols (0-100).

            risk_tier (str): Risk tier from SystemicActionEngine.
                One of: "NORMAL", "ELEVATED_RISK",
                "HIGH_VOLATILITY", "SYSTEMIC_CRISIS".

            recommended_action (str): Recommended protective
                action from SystemicActionEngine. One of:
                "NO_ACTION", "INCREASE_MONITORING",
                "ENABLE_TRADE_THROTTLING",
                "ACTIVATE_EMERGENCY_CONTROLS".

            escalation_reasons (list[str], optional): List of
                human-readable escalation trigger descriptions
                from SystemicActionEngine. Default: [].

        Returns:
            dict: Complete incident record with fields:
                {
                    "incident_id": str (UUID4),
                    "timestamp": str (ISO 8601 UTC),
                    "risk_tier": str,
                    "msi_score": float,
                    "contagion_risk_score": float,
                    "feed_mismatch_rate": float,
                    "average_trust_score": float,
                    "recommended_action": str,
                    "escalation_reasons": list[str],
                    "severity_score": float (0-100),
                    "regulatory_classification": str,
                    "root_cause_chain": list[str],
                    "incident_sequence": int
                }

        Raises:
            ValueError: If any input is outside valid range.
            TypeError: If any input is wrong type.
        """
        # ── Validate inputs ───────────────────────────────────────────
        self._validate_inputs(
            msi, contagion_risk_score,
            feed_mismatch_rate, average_trust_score,
            risk_tier, recommended_action
        )

        if escalation_reasons is None:
            escalation_reasons = []

        # ── Generate incident identity ────────────────────────────────
        incident_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        self._incident_count += 1

        # ── Compute severity score ────────────────────────────────────
        severity_score = self._compute_severity_score(
            msi, contagion_risk_score,
            feed_mismatch_rate, average_trust_score
        )

        # ── Determine regulatory classification ───────────────────────
        regulatory_classification = self._classify_regulatory(
            severity_score
        )

        # ── Build root cause chain ────────────────────────────────────
        root_cause_chain = self._build_root_cause_chain(
            msi, contagion_risk_score,
            feed_mismatch_rate, average_trust_score,
            escalation_reasons
        )

        # ── Construct incident record ─────────────────────────────────
        incident = {
            "incident_id": incident_id,
            "timestamp": timestamp.isoformat(),
            "risk_tier": risk_tier,
            "msi_score": round(msi, 2),
            "contagion_risk_score": round(contagion_risk_score, 2),
            "feed_mismatch_rate": round(feed_mismatch_rate, 6),
            "average_trust_score": round(average_trust_score, 2),
            "recommended_action": recommended_action,
            "escalation_reasons": list(escalation_reasons),
            "severity_score": round(severity_score, 2),
            "regulatory_classification": regulatory_classification,
            "root_cause_chain": root_cause_chain,
            "incident_sequence": self._incident_count
        }

        # ── Persist and store ─────────────────────────────────────────
        self._store_incident(incident)
        self._persist_to_database(incident, timestamp)
        self._log_incident(incident)

        return incident

    # ──────────────────────────────────────────────────────────────────
    # Core API: Export & Reporting
    # ──────────────────────────────────────────────────────────────────

    def export_incident_to_json(
        self,
        incident_id: str,
        indent: int = 2
    ) -> str:
        """
        Export a single incident record as a formatted JSON string.

        The JSON output is designed for:
        - Regulatory submission attachments
        - REST API responses
        - Log aggregation systems (ELK, Splunk)
        - Archival storage

        Args:
            incident_id (str): The UUID of the incident to export.
            indent (int): JSON indentation level. Default: 2.

        Returns:
            str: Formatted JSON string of the incident record.

        Raises:
            KeyError: If incident_id is not found.
        """
        if incident_id not in self._incidents:
            raise KeyError(
                f"Incident '{incident_id}' not found. "
                f"Available: {len(self._incidents)} incidents."
            )

        return json.dumps(
            self._incidents[incident_id],
            indent=indent,
            default=str
        )

    def export_incident_to_dict(
        self,
        incident_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve an incident record as a Python dictionary.

        Args:
            incident_id: The UUID of the incident.

        Returns:
            dict: Copy of the incident record.

        Raises:
            KeyError: If incident_id is not found.
        """
        if incident_id not in self._incidents:
            raise KeyError(
                f"Incident '{incident_id}' not found."
            )

        # Return a copy to prevent external mutation
        return dict(self._incidents[incident_id])

    def generate_compliance_report(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Generate an aggregate compliance report across all incidents.

        This report provides the summary statistics and incident
        listings that a compliance officer or regulator would need
        for periodic review (daily, weekly, or ad-hoc).

        The report structure follows best practices from:
        - DORA ICT incident reporting templates
        - SEC market event reporting guidelines
        - Basel III operational risk event databases

        Args:
            limit: Maximum number of individual incidents to include
                in the detailed listing. Default: 100.

        Returns:
            dict: Compliance report containing:
                {
                    "report_id": str (UUID),
                    "generated_at": str (ISO 8601),
                    "summary": {
                        "total_incidents": int,
                        "classification_breakdown": dict,
                        "average_severity": float,
                        "max_severity": float,
                        "enforcement_incidents": int,
                        "escalated_incidents": int
                    },
                    "incidents": list[dict]  (most recent first)
                }
        """
        report_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc)

        all_incidents = list(self._incidents.values())

        # Classification breakdown
        classification_breakdown = {
            CLASSIFICATION_CRITICAL: 0,
            CLASSIFICATION_HIGH: 0,
            CLASSIFICATION_ELEVATED: 0,
            CLASSIFICATION_NORMAL: 0
        }

        severity_scores = []
        enforcement_count = 0
        escalated_count = 0

        enforcement_tiers = {"HIGH_VOLATILITY", "SYSTEMIC_CRISIS"}

        for inc in all_incidents:
            classification_breakdown[
                inc["regulatory_classification"]
            ] += 1
            severity_scores.append(inc["severity_score"])
            if inc["risk_tier"] in enforcement_tiers:
                enforcement_count += 1
            if inc["escalation_reasons"]:
                escalated_count += 1

        avg_severity = (
            sum(severity_scores) / len(severity_scores)
            if severity_scores else 0.0
        )
        max_severity = max(severity_scores) if severity_scores else 0.0

        # Get most recent incidents for detailed listing
        sorted_incidents = sorted(
            all_incidents,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]

        return {
            "report_id": report_id,
            "generated_at": generated_at.isoformat(),
            "summary": {
                "total_incidents": len(all_incidents),
                "classification_breakdown": classification_breakdown,
                "average_severity": round(avg_severity, 2),
                "max_severity": round(max_severity, 2),
                "enforcement_incidents": enforcement_count,
                "escalated_incidents": escalated_count
            },
            "incidents": sorted_incidents
        }

    # ──────────────────────────────────────────────────────────────────
    # Core API: Querying
    # ──────────────────────────────────────────────────────────────────

    def get_incident(
        self,
        incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single incident by ID. Returns None if not found.
        """
        return self._incidents.get(incident_id)

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        """
        Retrieve all incidents, ordered by timestamp (newest first).
        """
        return sorted(
            self._incidents.values(),
            key=lambda x: x["timestamp"],
            reverse=True
        )

    def get_incidents_by_classification(
        self,
        classification: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all incidents matching a regulatory classification.

        Args:
            classification: One of CRITICAL_MARKET_EVENT,
                HIGH_RISK_EVENT, ELEVATED_MONITORING_EVENT,
                NORMAL_OPERATION.

        Returns:
            list[dict]: Matching incidents, newest first.
        """
        matching = [
            inc for inc in self._incidents.values()
            if inc["regulatory_classification"] == classification
        ]
        return sorted(
            matching,
            key=lambda x: x["timestamp"],
            reverse=True
        )

    def get_incident_count(self) -> int:
        """Return total number of incidents created."""
        return self._incident_count

    # ──────────────────────────────────────────────────────────────────
    # Internal: Severity Score Computation
    # ──────────────────────────────────────────────────────────────────

    def _compute_severity_score(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float
    ) -> float:
        """
        Compute the composite severity score for an incident.

        The severity score quantifies the overall danger level of
        the current market state on a 0-100 scale, independent of
        the policy-driven risk tier classification.

        Formula:
            severity = (
                0.4 × (100 - MSI)
              + 0.3 × contagion_risk_score
              + 0.2 × (feed_mismatch_rate × 100)
              + 0.1 × (100 - average_trust_score)
            )

        Each component measures a different dimension of risk:
        - (100 - MSI): Market instability—distance from ideal stability
        - CRS: Cross-asset contagion—systemic amplification risk
        - Feed mismatch × 100: Data corruption—reliability of inputs
        - (100 - trust): Trust deficit—long-term data quality trend

        Args:
            msi: Market Stability Index (0-100)
            contagion_risk_score: CRS (0-100)
            feed_mismatch_rate: Feed mismatch (0-1)
            average_trust_score: Average trust (0-100)

        Returns:
            float: Severity score clamped to [0, 100].
        """
        msi_component = self.WEIGHT_MSI_COMPLEMENT * (100.0 - msi)
        contagion_component = self.WEIGHT_CONTAGION * contagion_risk_score
        feed_component = (
            self.WEIGHT_FEED_MISMATCH * (feed_mismatch_rate * 100.0)
        )
        trust_component = (
            self.WEIGHT_TRUST_DEFICIT * (100.0 - average_trust_score)
        )

        severity_raw = (
            msi_component
            + contagion_component
            + feed_component
            + trust_component
        )

        return max(
            self.SEVERITY_MIN,
            min(self.SEVERITY_MAX, severity_raw)
        )

    # ──────────────────────────────────────────────────────────────────
    # Internal: Regulatory Classification
    # ──────────────────────────────────────────────────────────────────

    def _classify_regulatory(
        self,
        severity_score: float
    ) -> str:
        """
        Map severity score to regulatory classification.

        Classifications align with standard financial regulatory
        event categories:

        - CRITICAL_MARKET_EVENT (severity > 80):
          Requires immediate regulatory notification.
          Comparable to SEC Form 8-K material event or
          DORA "Major ICT Incident".

        - HIGH_RISK_EVENT (60-80):
          Requires senior management notification and
          detailed post-event analysis.
          Comparable to DORA significant incident.

        - ELEVATED_MONITORING_EVENT (40-60):
          Requires enhanced surveillance and documentation.
          Logged for trend analysis.

        - NORMAL_OPERATION (< 40):
          Standard operation. Logged for completeness
          and baseline comparison.

        Args:
            severity_score: Computed severity (0-100).

        Returns:
            str: Regulatory classification string.
        """
        if severity_score > SEVERITY_CRITICAL_THRESHOLD:
            return CLASSIFICATION_CRITICAL
        elif severity_score > SEVERITY_HIGH_THRESHOLD:
            return CLASSIFICATION_HIGH
        elif severity_score > SEVERITY_ELEVATED_THRESHOLD:
            return CLASSIFICATION_ELEVATED
        else:
            return CLASSIFICATION_NORMAL

    # ──────────────────────────────────────────────────────────────────
    # Internal: Root Cause Chain
    # ──────────────────────────────────────────────────────────────────

    def _build_root_cause_chain(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float,
        escalation_reasons: List[str]
    ) -> List[str]:
        """
        Build a human-readable root cause analysis chain.

        The chain links upstream data quality issues to downstream
        systemic effects, providing the causal narrative that
        regulators require for incident investigation.

        The chain is ordered from most fundamental cause (data/feeds)
        to highest-level effect (systemic classification).

        Args:
            msi: Market Stability Index
            contagion_risk_score: CRS
            feed_mismatch_rate: Feed mismatch rate
            average_trust_score: Average trust
            escalation_reasons: Escalation trigger descriptions

        Returns:
            list[str]: Ordered root cause statements.
        """
        chain: List[str] = []

        # Layer 1: Data integrity assessment
        if feed_mismatch_rate > 0.02:
            chain.append(
                "DATA_LAYER: Feed mismatch rate "
                "(%.2f%%) indicates cross-feed "
                "data integrity failure" % (feed_mismatch_rate * 100)
            )
        elif feed_mismatch_rate > 0.01:
            chain.append(
                "DATA_LAYER: Feed mismatch rate "
                "(%.2f%%) is elevated but within "
                "tolerance" % (feed_mismatch_rate * 100)
            )
        else:
            chain.append(
                "DATA_LAYER: Feed integrity normal "
                "(%.2f%% mismatch)" % (feed_mismatch_rate * 100)
            )

        # Layer 2: Trust assessment
        if average_trust_score < 50:
            chain.append(
                "TRUST_LAYER: Average trust (%.1f) below "
                "critical threshold — majority of data unreliable"
                % average_trust_score
            )
        elif average_trust_score < 70:
            chain.append(
                "TRUST_LAYER: Average trust (%.1f) is degraded — "
                "elevated data quality concerns"
                % average_trust_score
            )
        else:
            chain.append(
                "TRUST_LAYER: Average trust (%.1f) is acceptable"
                % average_trust_score
            )

        # Layer 3: Contagion assessment
        if contagion_risk_score > 70:
            chain.append(
                "CONTAGION_LAYER: CRS (%.1f) indicates active "
                "cross-asset systemic contagion"
                % contagion_risk_score
            )
        elif contagion_risk_score > 40:
            chain.append(
                "CONTAGION_LAYER: CRS (%.1f) shows elevated "
                "cross-asset correlation"
                % contagion_risk_score
            )
        else:
            chain.append(
                "CONTAGION_LAYER: CRS (%.1f) within normal range"
                % contagion_risk_score
            )

        # Layer 4: Market stability assessment
        if msi < 40:
            chain.append(
                "STABILITY_LAYER: MSI (%.1f) in systemic risk "
                "zone — market stability critically impaired"
                % msi
            )
        elif msi < 60:
            chain.append(
                "STABILITY_LAYER: MSI (%.1f) indicates high "
                "volatility conditions" % msi
            )
        elif msi < 80:
            chain.append(
                "STABILITY_LAYER: MSI (%.1f) shows elevated "
                "risk — increased monitoring required" % msi
            )
        else:
            chain.append(
                "STABILITY_LAYER: MSI (%.1f) is stable" % msi
            )

        # Layer 5: Escalation triggers
        if escalation_reasons:
            for reason in escalation_reasons:
                chain.append("ESCALATION: %s" % reason)

        return chain

    # ──────────────────────────────────────────────────────────────────
    # Internal: Storage & Persistence
    # ──────────────────────────────────────────────────────────────────

    def _store_incident(self, incident: Dict[str, Any]) -> None:
        """Store incident in in-memory index."""
        self._incidents[incident["incident_id"]] = incident

        # Evict oldest if over capacity
        if len(self._incidents) > self._max_in_memory:
            oldest_key = min(
                self._incidents,
                key=lambda k: self._incidents[k]["timestamp"]
            )
            del self._incidents[oldest_key]

    def _persist_to_database(
        self,
        incident: Dict[str, Any],
        timestamp: datetime
    ) -> None:
        """
        Persist incident to the database audit trail.

        Creates the governance_incidents table if it doesn't exist,
        then inserts the complete incident record.

        Also logs a system event for cross-referencing with the
        existing system_events audit trail.
        """
        if self.db_manager is None:
            return

        try:
            cursor = self.db_manager.conn.cursor()

            # Ensure governance_incidents table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS governance_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL UNIQUE,
                    timestamp TEXT NOT NULL,
                    risk_tier TEXT NOT NULL,
                    msi_score REAL NOT NULL,
                    contagion_risk_score REAL NOT NULL,
                    feed_mismatch_rate REAL NOT NULL,
                    average_trust_score REAL NOT NULL,
                    recommended_action TEXT NOT NULL,
                    escalation_reasons TEXT,
                    severity_score REAL NOT NULL,
                    regulatory_classification TEXT NOT NULL,
                    root_cause_chain TEXT,
                    incident_sequence INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert incident
            cursor.execute('''
                INSERT INTO governance_incidents (
                    incident_id, timestamp, risk_tier,
                    msi_score, contagion_risk_score,
                    feed_mismatch_rate, average_trust_score,
                    recommended_action, escalation_reasons,
                    severity_score, regulatory_classification,
                    root_cause_chain, incident_sequence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident["incident_id"],
                incident["timestamp"],
                incident["risk_tier"],
                incident["msi_score"],
                incident["contagion_risk_score"],
                incident["feed_mismatch_rate"],
                incident["average_trust_score"],
                incident["recommended_action"],
                json.dumps(incident["escalation_reasons"]),
                incident["severity_score"],
                incident["regulatory_classification"],
                json.dumps(incident["root_cause_chain"]),
                incident["incident_sequence"]
            ))

            self.db_manager.conn.commit()

            # Also log to system_events for cross-referencing
            severity_map = {
                CLASSIFICATION_CRITICAL: "CRITICAL",
                CLASSIFICATION_HIGH: "HIGH",
                CLASSIFICATION_ELEVATED: "WARNING",
                CLASSIFICATION_NORMAL: "INFO"
            }

            self.db_manager.log_system_event(
                timestamp=timestamp,
                event_type="GOVERNANCE_INCIDENT",
                severity=severity_map.get(
                    incident["regulatory_classification"], "INFO"
                ),
                message=(
                    "Incident %s | Tier: %s | Severity: %.1f | "
                    "Class: %s" % (
                        incident["incident_id"][:8],
                        incident["risk_tier"],
                        incident["severity_score"],
                        incident["regulatory_classification"]
                    )
                ),
                data={
                    "incident_id": incident["incident_id"],
                    "severity_score": incident["severity_score"],
                    "regulatory_classification": (
                        incident["regulatory_classification"]
                    )
                }
            )

            logger.debug(
                "Incident %s persisted to database",
                incident["incident_id"][:8]
            )

        except Exception as e:
            logger.error(
                "Failed to persist incident %s: %s",
                incident["incident_id"][:8],
                str(e), exc_info=True
            )

    # ──────────────────────────────────────────────────────────────────
    # Internal: Logging
    # ──────────────────────────────────────────────────────────────────

    def _log_incident(self, incident: Dict[str, Any]) -> None:
        """Log incident at appropriate severity level."""
        classification = incident["regulatory_classification"]
        msg = (
            "INCIDENT #%d [%s] | ID=%s | "
            "Tier=%s | Severity=%.1f | Action=%s" % (
                incident["incident_sequence"],
                classification,
                incident["incident_id"][:8],
                incident["risk_tier"],
                incident["severity_score"],
                incident["recommended_action"]
            )
        )

        if classification == CLASSIFICATION_CRITICAL:
            logger.critical(msg)
        elif classification == CLASSIFICATION_HIGH:
            logger.warning(msg)
        elif classification == CLASSIFICATION_ELEVATED:
            logger.info(msg)
        else:
            logger.debug(msg)

    # ──────────────────────────────────────────────────────────────────
    # Internal: Input Validation
    # ──────────────────────────────────────────────────────────────────

    VALID_TIERS = {
        "NORMAL", "ELEVATED_RISK",
        "HIGH_VOLATILITY", "SYSTEMIC_CRISIS"
    }

    VALID_ACTIONS = {
        "NO_ACTION", "INCREASE_MONITORING",
        "ENABLE_TRADE_THROTTLING",
        "ACTIVATE_EMERGENCY_CONTROLS"
    }

    def _validate_inputs(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float,
        risk_tier: str,
        recommended_action: str
    ) -> None:
        """
        Validate all inputs for incident creation.

        Raises:
            ValueError: If numeric inputs are out of range or
                string inputs are not valid enum values.
            TypeError: If inputs are wrong type.
        """
        # Numeric validation
        for name, value, low, high in [
            ("msi", msi, 0.0, 100.0),
            ("contagion_risk_score", contagion_risk_score, 0.0, 100.0),
            ("feed_mismatch_rate", feed_mismatch_rate, 0.0, 1.0),
            ("average_trust_score", average_trust_score, 0.0, 100.0),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    "%s must be numeric, got %s" % (name, type(value))
                )
            if not (low <= value <= high):
                raise ValueError(
                    "%s must be in [%s, %s], got %s"
                    % (name, low, high, value)
                )

        # String validation
        if not isinstance(risk_tier, str):
            raise TypeError(
                "risk_tier must be str, got %s" % type(risk_tier)
            )
        if risk_tier not in self.VALID_TIERS:
            raise ValueError(
                "risk_tier must be one of %s, got '%s'"
                % (self.VALID_TIERS, risk_tier)
            )

        if not isinstance(recommended_action, str):
            raise TypeError(
                "recommended_action must be str, got %s"
                % type(recommended_action)
            )
        if recommended_action not in self.VALID_ACTIONS:
            raise ValueError(
                "recommended_action must be one of %s, got '%s'"
                % (self.VALID_ACTIONS, recommended_action)
            )
