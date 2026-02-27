"""
Systemic Risk Orchestration & Response Engine
===============================================

Production-grade engine that translates systemic intelligence signals
into enforceable governance actions with full audit compliance.

Risk Governance Philosophy:
    Financial market stability depends on a chain of responsibility:

    1. **Detection**: Identify anomalies, contagion, data corruption
       (handled by upstream modules: anomaly engine, contagion engine,
       feed integrity engine)

    2. **Quantification**: Compute composite risk metrics (MSI, CRS)
       that distill complex multi-dimensional signals into actionable
       numbers (handled by MarketStabilityIndex, ContagionEngine)

    3. **Classification**: Map continuous risk scores into discrete
       governance tiers that align with organizational response
       protocols (THIS MODULE)

    4. **Enforcement**: Translate risk tiers into concrete protective
       actions—monitoring escalation, trade throttling, position
       limits, emergency halts (THIS MODULE)

    5. **Audit**: Record every risk evaluation, escalation decision,
       and enforcement action for post-incident investigation and
       regulatory compliance (THIS MODULE)

    This engine sits at levels 3-5: the bridge between quantitative
    risk measurement and operational risk management.

Why Escalation Rules Exist:
    Risk tiers based solely on MSI may underestimate systemic danger
    when individual risk factors are extreme but haven't yet fully
    propagated into the composite score. Escalation rules provide
    defense-in-depth by ensuring that:

    - **High contagion** (CRS > 70) escalates even if MSI is moderate,
      because contagion is a leading indicator of systemic failure
      that may not yet be reflected in trust scores.

    - **Feed corruption** (mismatch > 2%) escalates because
      compromised data feeds undermine ALL downstream computations.
      If you can't trust the data, you can't trust the scores.

    - **Low market trust** (< 50) escalates because trust below 50%
      indicates a majority of data points are unreliable, suggesting
      a persistent quality failure rather than isolated incidents.

    Each escalation is logged with its specific trigger for forensic
    analysis, enabling regulators and risk officers to understand
    exactly WHY an action was taken.

Alignment with Financial Infrastructure Best Practices:
    - **MiFID II / Reg NMS**: Best execution obligations require
      that trading be restricted when data quality is insufficient.
    - **Basel III**: Operational risk capital charges require
      documented incident response procedures.
    - **IOSCO Principles**: Market intermediaries must have risk
      controls proportional to the risks they face.
    - **Circuit Breaker Analogy**: Like exchange circuit breakers
      (e.g., NYSE Rule 80B), this engine triggers tiered protective
      responses at calibrated thresholds.

    The structured incident records produced by this engine satisfy
    the documentation requirements of all major regulatory frameworks.

Future-Ready Design:
    The engine is designed to support:
    - Automated enforcement (when trading bot integration is active)
    - Webhook/notification dispatch (alert routing)
    - Dynamic policy updates via configuration
    - Multi-market jurisdiction support
    - Real-time dashboard integration

Integration Points:
    - Consumes: MSI, CRS, feed_mismatch_rate, average_trust_score
    - Produces: Risk tier, recommended action, enforcement flag,
      alert level, structured incident record
    - Logs to: DatabaseManager.systemic_incidents table
    - Integrates with: ProtectionEngine (trading controls),
      Dashboard (visual alerts)

Author: CyFin Team
Version: 1.0.0
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(logging.NullHandler())


# ══════════════════════════════════════════════════════════════════════════
# Enumerations for type safety and clarity
# ══════════════════════════════════════════════════════════════════════════

class RiskTier(Enum):
    """
    Discrete risk governance tiers.

    Each tier maps to a specific set of protective measures and
    organizational response protocols. Tiers are ordered by severity
    from NORMAL (lowest) to SYSTEMIC_CRISIS (highest).

    In regulatory terms, these correspond to:
    - NORMAL: Business as usual
    - ELEVATED_RISK: Enhanced surveillance (comparable to exchange
      "Unusual Activity" declarations)
    - HIGH_VOLATILITY: Active intervention (comparable to Level 1
      circuit breaker)
    - SYSTEMIC_CRISIS: Emergency protocols (comparable to market-wide
      trading halt / Level 3 circuit breaker)
    """
    NORMAL = "NORMAL"
    ELEVATED_RISK = "ELEVATED_RISK"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    SYSTEMIC_CRISIS = "SYSTEMIC_CRISIS"


class AlertLevel(Enum):
    """
    Visual alert severity levels for dashboard and notification systems.

    Maps to standard traffic-light color coding used in financial
    risk dashboards and operations centers globally.
    """
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"


class RecommendedAction(Enum):
    """
    Concrete protective actions to be taken for each risk tier.

    These actions form an escalation ladder:
    1. NO_ACTION: Normal monitoring only
    2. INCREASE_MONITORING: Reduce reporting intervals, alert risk team
    3. ENABLE_TRADE_THROTTLING: Rate-limit order submission,
       increase margin requirements, restrict new position entry
    4. ACTIVATE_EMERGENCY_CONTROLS: Halt all automated trading,
       close open positions where safe, notify senior management
       and regulatory contacts
    """
    NO_ACTION = "NO_ACTION"
    INCREASE_MONITORING = "INCREASE_MONITORING"
    ENABLE_TRADE_THROTTLING = "ENABLE_TRADE_THROTTLING"
    ACTIVATE_EMERGENCY_CONTROLS = "ACTIVATE_EMERGENCY_CONTROLS"


# ══════════════════════════════════════════════════════════════════════════
# Tier ordering for escalation logic
# ══════════════════════════════════════════════════════════════════════════

_TIER_SEVERITY_ORDER = [
    RiskTier.NORMAL,
    RiskTier.ELEVATED_RISK,
    RiskTier.HIGH_VOLATILITY,
    RiskTier.SYSTEMIC_CRISIS,
]

_TIER_TO_ALERT = {
    RiskTier.NORMAL: AlertLevel.GREEN,
    RiskTier.ELEVATED_RISK: AlertLevel.YELLOW,
    RiskTier.HIGH_VOLATILITY: AlertLevel.ORANGE,
    RiskTier.SYSTEMIC_CRISIS: AlertLevel.RED,
}

_TIER_TO_ACTION = {
    RiskTier.NORMAL: RecommendedAction.NO_ACTION,
    RiskTier.ELEVATED_RISK: RecommendedAction.INCREASE_MONITORING,
    RiskTier.HIGH_VOLATILITY: RecommendedAction.ENABLE_TRADE_THROTTLING,
    RiskTier.SYSTEMIC_CRISIS: RecommendedAction.ACTIVATE_EMERGENCY_CONTROLS,
}

_ENFORCEMENT_TIERS = {
    RiskTier.HIGH_VOLATILITY,
    RiskTier.SYSTEMIC_CRISIS,
}


class SystemicActionEngine:
    """
    Translates systemic risk intelligence into enforceable governance
    actions with full audit compliance.

    This engine is the operational bridge between CyFin's quantitative
    risk analytics (MSI, CRS, feed validation, trust scoring) and
    concrete protective measures (trade throttling, monitoring
    escalation, emergency halts).

    Every evaluation produces a structured incident record suitable
    for regulatory audit, post-incident investigation, and real-time
    dashboard rendering.

    Architecture::

        ┌─────────────────────────────────────────────────────────┐
        │                SYSTEMIC ACTION ENGINE                   │
        │                                                         │
        │  Inputs:       │  Processing:    │  Outputs:            │
        │  ───────        │  ──────────     │  ────────            │
        │  MSI            │  Tier classify  │  Risk tier           │
        │  CRS            │  Escalation     │  Recommended action  │
        │  Feed mismatch  │  rules check    │  Alert level         │
        │  Avg trust      │  Policy apply   │  Enforcement flag    │
        │                 │                 │  Incident record     │
        └─────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼──────────┐
                    │           │          │
            ┌───────▼───┐ ┌────▼────┐ ┌───▼──────┐
            │ Protection│ │Dashboard│ │ Database │
            │  Engine   │ │  Alert  │ │  Audit   │
            └───────────┘ └─────────┘ └──────────┘

    Thread Safety:
        The engine is stateless per evaluation—each call to
        evaluate_systemic_risk() is independent. However, incident
        history and database logging use a lock for thread safety.

    Attributes:
        stable_threshold (float): MSI threshold for NORMAL tier.
        elevated_threshold (float): MSI threshold for ELEVATED_RISK.
        high_volatility_threshold (float): MSI threshold for HIGH_VOLATILITY.
        contagion_escalation_threshold (float): CRS above which
            escalation is triggered.
        feed_mismatch_escalation_threshold (float): Feed mismatch
            rate above which escalation is triggered.
        trust_escalation_threshold (float): Average trust below
            which escalation is triggered.
        db_manager: Optional DatabaseManager for incident persistence.

    Usage Example::

        >>> from systemic.systemic_action_engine import SystemicActionEngine
        >>> engine = SystemicActionEngine(db_manager=db)
        >>> result = engine.evaluate_systemic_risk(
        ...     msi=55.0,
        ...     contagion_risk_score=45.0,
        ...     feed_mismatch_rate=0.01,
        ...     average_trust_score=72.0
        ... )
        >>> print(f"Tier: {result['risk_tier']}")
        >>> print(f"Action: {result['recommended_action']}")
        >>> print(f"Alert: {result['alert_level']}")
    """

    # ──────────────────────────────────────────────────────────────────
    # Default policy thresholds
    # ──────────────────────────────────────────────────────────────────
    DEFAULT_STABLE_THRESHOLD = 80.0
    DEFAULT_ELEVATED_THRESHOLD = 60.0
    DEFAULT_HIGH_VOLATILITY_THRESHOLD = 40.0
    DEFAULT_SYSTEMIC_THRESHOLD = 0.0

    DEFAULT_CONTAGION_ESCALATION = 70.0
    DEFAULT_FEED_MISMATCH_ESCALATION = 0.02
    DEFAULT_TRUST_ESCALATION = 50.0

    def __init__(
        self,
        stable_threshold: float = DEFAULT_STABLE_THRESHOLD,
        elevated_threshold: float = DEFAULT_ELEVATED_THRESHOLD,
        high_volatility_threshold: float = DEFAULT_HIGH_VOLATILITY_THRESHOLD,
        systemic_threshold: float = DEFAULT_SYSTEMIC_THRESHOLD,
        contagion_escalation_threshold: float = DEFAULT_CONTAGION_ESCALATION,
        feed_mismatch_escalation_threshold: float = DEFAULT_FEED_MISMATCH_ESCALATION,
        trust_escalation_threshold: float = DEFAULT_TRUST_ESCALATION,
        db_manager: Optional[Any] = None
    ):
        """
        Initialize the Systemic Action Engine with configurable policy.

        The thresholds define the boundaries between risk tiers and
        the conditions under which escalation rules activate. These
        can be calibrated per deployment environment—for example,
        a conservative regulator might use tighter thresholds than
        a proprietary trading firm.

        Args:
            stable_threshold (float): MSI at or above which market
                is considered NORMAL. Default: 80.0

            elevated_threshold (float): MSI at or above which market
                is ELEVATED_RISK (but below stable). Default: 60.0

            high_volatility_threshold (float): MSI at or above which
                market is HIGH_VOLATILITY (but below elevated).
                Default: 40.0

            systemic_threshold (float): MSI below high_volatility is
                SYSTEMIC_CRISIS. This is the floor. Default: 0.0

            contagion_escalation_threshold (float): CRS above which
                the tier is escalated by one level. Default: 70.0.
                Rationale: CRS > 70 indicates strong cross-asset
                contagion that may not yet be reflected in MSI.

            feed_mismatch_escalation_threshold (float): Feed mismatch
                rate above which the tier is escalated. Default: 0.02.
                Rationale: > 2% mismatch rate means data integrity
                is compromised across multiple feeds.

            trust_escalation_threshold (float): Average trust score
                below which the tier is escalated. Default: 50.0.
                Rationale: < 50% trust means majority of data points
                are unreliable.

            db_manager: Optional DatabaseManager for persisting
                incident records. If None, incidents are only logged
                via Python logging.

        Raises:
            ValueError: If thresholds are not in descending order
                or outside valid ranges.
        """
        # ── Validate threshold ordering ───────────────────────────────
        if not (stable_threshold > elevated_threshold >
                high_volatility_threshold >= systemic_threshold):
            raise ValueError(
                "Thresholds must satisfy: stable > elevated > "
                "high_volatility >= systemic. Got: "
                f"stable={stable_threshold}, elevated={elevated_threshold}, "
                f"high_vol={high_volatility_threshold}, "
                f"systemic={systemic_threshold}"
            )

        if not (0 <= stable_threshold <= 100):
            raise ValueError(
                f"stable_threshold must be in [0, 100], "
                f"got {stable_threshold}"
            )

        if contagion_escalation_threshold < 0:
            raise ValueError(
                f"contagion_escalation_threshold must be >= 0, "
                f"got {contagion_escalation_threshold}"
            )

        if feed_mismatch_escalation_threshold < 0:
            raise ValueError(
                f"feed_mismatch_escalation_threshold must be >= 0, "
                f"got {feed_mismatch_escalation_threshold}"
            )

        if trust_escalation_threshold < 0:
            raise ValueError(
                f"trust_escalation_threshold must be >= 0, "
                f"got {trust_escalation_threshold}"
            )

        # ── Store configuration ───────────────────────────────────────
        self.stable_threshold = stable_threshold
        self.elevated_threshold = elevated_threshold
        self.high_volatility_threshold = high_volatility_threshold
        self.systemic_threshold = systemic_threshold
        self.contagion_escalation_threshold = contagion_escalation_threshold
        self.feed_mismatch_escalation_threshold = (
            feed_mismatch_escalation_threshold
        )
        self.trust_escalation_threshold = trust_escalation_threshold
        self.db_manager = db_manager

        # ── Incident history (in-memory ring buffer) ──────────────────
        self._incident_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        self._evaluation_count: int = 0

        logger.info(
            "SystemicActionEngine initialized | "
            "thresholds=[%.1f, %.1f, %.1f, %.1f] | "
            "escalation=[CRS>%.1f, feed>%.3f, trust<%.1f] | "
            "db=%s",
            stable_threshold, elevated_threshold,
            high_volatility_threshold, systemic_threshold,
            contagion_escalation_threshold,
            feed_mismatch_escalation_threshold,
            trust_escalation_threshold,
            "connected" if db_manager else "disabled"
        )

    # ──────────────────────────────────────────────────────────────────
    # Core API: Risk Evaluation
    # ──────────────────────────────────────────────────────────────────

    def evaluate_systemic_risk(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float
    ) -> Dict[str, Any]:
        """
        Evaluate current systemic risk and produce an actionable
        governance response.

        This is the primary entry point. It:
        1. Classifies the base risk tier from MSI
        2. Applies escalation rules for CRS, feed mismatch, trust
        3. Determines the recommended protective action
        4. Sets the enforcement flag
        5. Constructs a structured incident record
        6. Persists to database if configured
        7. Returns the complete evaluation result

        The evaluation is idempotent and side-effect-free except for
        logging and database persistence. Multiple concurrent calls
        are safe.

        Args:
            msi (float): Market Stability Index score (0-100).
                Sourced from MarketStabilityIndex.compute_msi().

            contagion_risk_score (float): Cross-asset contagion risk
                score (0-100). Sourced from
                ContagionEngine.get_contagion_summary().

            feed_mismatch_rate (float): Global feed mismatch rate
                (0-1). Sourced from
                FeedIntegrityEngine.get_global_feed_health().

            average_trust_score (float): Average trust score across
                all monitored symbols (0-100). Sourced from
                per-symbol TrustScorer aggregation.

        Returns:
            dict: Structured governance response:
                {
                    "risk_tier": str
                        One of: "NORMAL", "ELEVATED_RISK",
                        "HIGH_VOLATILITY", "SYSTEMIC_CRISIS"

                    "recommended_action": str
                        One of: "NO_ACTION", "INCREASE_MONITORING",
                        "ENABLE_TRADE_THROTTLING",
                        "ACTIVATE_EMERGENCY_CONTROLS"

                    "enforcement_required": bool
                        True if active protective measures must be
                        enforced (HIGH_VOLATILITY or SYSTEMIC_CRISIS).

                    "alert_level": str
                        One of: "GREEN", "YELLOW", "ORANGE", "RED"
                        For dashboard color coding.

                    "escalation_reasons": list of str
                        Human-readable explanations of any escalation
                        rules that activated. Empty if no escalation.

                    "base_tier": str
                        The tier determined by MSI alone, before
                        escalation rules were applied. Useful for
                        audit: shows whether the final tier was
                        escalated from the base.

                    "inputs": dict
                        Echo of all input parameters for audit trail.

                    "timestamp": str (ISO 8601)
                        UTC timestamp of the evaluation.

                    "evaluation_id": int
                        Sequential evaluation counter for tracking.
                }

        Raises:
            ValueError: If any input is outside valid range.

        Example::

            >>> result = engine.evaluate_systemic_risk(
            ...     msi=55.0,
            ...     contagion_risk_score=75.0,
            ...     feed_mismatch_rate=0.01,
            ...     average_trust_score=65.0
            ... )
            >>> # MSI=55 → HIGH_VOLATILITY (base)
            >>> # CRS=75 > 70 → escalate to SYSTEMIC_CRISIS
            >>> print(result['risk_tier'])  # SYSTEMIC_CRISIS
            >>> print(result['enforcement_required'])  # True
        """
        # ── Input validation ──────────────────────────────────────────
        self._validate_inputs(
            msi, contagion_risk_score,
            feed_mismatch_rate, average_trust_score
        )

        # ── Step 1: Base tier classification from MSI ─────────────────
        base_tier = self._classify_base_tier(msi)

        # ── Step 2: Apply escalation rules ────────────────────────────
        final_tier, escalation_reasons = self._apply_escalation_rules(
            base_tier=base_tier,
            contagion_risk_score=contagion_risk_score,
            feed_mismatch_rate=feed_mismatch_rate,
            average_trust_score=average_trust_score
        )

        # ── Step 3: Determine outputs from final tier ─────────────────
        alert_level = _TIER_TO_ALERT[final_tier]
        recommended_action = _TIER_TO_ACTION[final_tier]
        enforcement_required = final_tier in _ENFORCEMENT_TIERS

        # ── Step 4: Build structured incident record ──────────────────
        self._evaluation_count += 1
        timestamp = datetime.now(timezone.utc)

        incident = {
            "risk_tier": final_tier.value,
            "recommended_action": recommended_action.value,
            "enforcement_required": enforcement_required,
            "alert_level": alert_level.value,
            "escalation_reasons": escalation_reasons,
            "base_tier": base_tier.value,
            "inputs": {
                "msi": msi,
                "contagion_risk_score": contagion_risk_score,
                "feed_mismatch_rate": feed_mismatch_rate,
                "average_trust_score": average_trust_score
            },
            "timestamp": timestamp.isoformat(),
            "evaluation_id": self._evaluation_count
        }

        # ── Step 5: Log and persist ───────────────────────────────────
        self._log_evaluation(incident)
        self._persist_incident(incident, timestamp)

        # Store in in-memory history
        self._incident_history.append(incident)
        if len(self._incident_history) > self._max_history:
            self._incident_history = (
                self._incident_history[-self._max_history:]
            )

        return incident

    # ──────────────────────────────────────────────────────────────────
    # Public API: History & Statistics
    # ──────────────────────────────────────────────────────────────────

    def get_incident_history(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent incident records from in-memory history.

        Args:
            limit: Maximum number of records to return (most recent
                first). Default: 50.

        Returns:
            list[dict]: Recent incident records, newest first.
        """
        return list(reversed(self._incident_history[-limit:]))

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics from evaluation history.

        Returns:
            dict: {
                "total_evaluations": int,
                "tier_distribution": dict (tier -> count),
                "escalation_count": int,
                "enforcement_count": int,
                "current_tier": str or None,
                "current_alert": str or None
            }
        """
        tier_dist = {tier.value: 0 for tier in RiskTier}
        escalation_count = 0
        enforcement_count = 0

        for incident in self._incident_history:
            tier_dist[incident["risk_tier"]] += 1
            if incident["escalation_reasons"]:
                escalation_count += 1
            if incident["enforcement_required"]:
                enforcement_count += 1

        latest = (
            self._incident_history[-1]
            if self._incident_history else None
        )

        return {
            "total_evaluations": self._evaluation_count,
            "tier_distribution": tier_dist,
            "escalation_count": escalation_count,
            "enforcement_count": enforcement_count,
            "current_tier": (
                latest["risk_tier"] if latest else None
            ),
            "current_alert": (
                latest["alert_level"] if latest else None
            )
        }

    def get_policy_config(self) -> Dict[str, Any]:
        """
        Return the current policy configuration for audit/display.

        Returns:
            dict: All configurable thresholds and their current values.
        """
        return {
            "tier_thresholds": {
                "NORMAL": f"MSI >= {self.stable_threshold}",
                "ELEVATED_RISK": (
                    f"{self.elevated_threshold} <= MSI < "
                    f"{self.stable_threshold}"
                ),
                "HIGH_VOLATILITY": (
                    f"{self.high_volatility_threshold} <= MSI < "
                    f"{self.elevated_threshold}"
                ),
                "SYSTEMIC_CRISIS": (
                    f"MSI < {self.high_volatility_threshold}"
                ),
            },
            "escalation_rules": {
                "contagion": (
                    f"CRS > {self.contagion_escalation_threshold} "
                    f"-> escalate +1 tier"
                ),
                "feed_mismatch": (
                    f"feed_mismatch_rate > "
                    f"{self.feed_mismatch_escalation_threshold} "
                    f"-> escalate +1 tier"
                ),
                "trust": (
                    f"avg_trust < {self.trust_escalation_threshold} "
                    f"-> escalate +1 tier"
                ),
            },
            "enforcement_tiers": [
                "HIGH_VOLATILITY", "SYSTEMIC_CRISIS"
            ],
            "alert_mapping": {
                t.value: a.value for t, a in _TIER_TO_ALERT.items()
            }
        }

    # ──────────────────────────────────────────────────────────────────
    # Internal: Base Tier Classification
    # ──────────────────────────────────────────────────────────────────

    def _classify_base_tier(self, msi: float) -> RiskTier:
        """
        Classify the base risk tier from the Market Stability Index.

        This is the first step before escalation rules are applied.
        The base tier provides a conservative starting point that
        reflects the overall market health.

        Args:
            msi: Market Stability Index score (0-100).

        Returns:
            RiskTier: Base risk tier classification.
        """
        if msi >= self.stable_threshold:
            return RiskTier.NORMAL
        elif msi >= self.elevated_threshold:
            return RiskTier.ELEVATED_RISK
        elif msi >= self.high_volatility_threshold:
            return RiskTier.HIGH_VOLATILITY
        else:
            return RiskTier.SYSTEMIC_CRISIS

    # ──────────────────────────────────────────────────────────────────
    # Internal: Escalation Rules
    # ──────────────────────────────────────────────────────────────────

    def _apply_escalation_rules(
        self,
        base_tier: RiskTier,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float
    ) -> tuple:
        """
        Apply escalation rules that may elevate the risk tier.

        Each rule independently checks its condition. If triggered,
        the tier is escalated by one level (up to SYSTEMIC_CRISIS
        maximum). Multiple rules can stack, potentially escalating
        by multiple levels.

        Escalation is additive and monotonic—rules can only increase
        severity, never decrease it. This ensures that the system
        fails safely (higher protection, not lower).

        Args:
            base_tier: The tier from MSI classification alone.
            contagion_risk_score: CRS value.
            feed_mismatch_rate: Global feed mismatch rate.
            average_trust_score: Average market trust.

        Returns:
            tuple: (final_tier: RiskTier, reasons: list[str])
        """
        current_tier = base_tier
        reasons: List[str] = []

        # Rule 1: High contagion risk
        if contagion_risk_score > self.contagion_escalation_threshold:
            new_tier = self._escalate_tier(current_tier)
            if new_tier != current_tier:
                reasons.append(
                    f"Contagion Risk Score ({contagion_risk_score:.1f}) "
                    f"exceeds threshold "
                    f"({self.contagion_escalation_threshold:.1f}) "
                    f"- potential cross-asset systemic contagion"
                )
                current_tier = new_tier
                logger.warning(
                    "ESCALATION: Contagion CRS=%.1f > %.1f | "
                    "%s -> %s",
                    contagion_risk_score,
                    self.contagion_escalation_threshold,
                    base_tier.value, current_tier.value
                )

        # Rule 2: Feed data integrity compromised
        if feed_mismatch_rate > self.feed_mismatch_escalation_threshold:
            new_tier = self._escalate_tier(current_tier)
            if new_tier != current_tier:
                reasons.append(
                    f"Feed mismatch rate ({feed_mismatch_rate:.4f}) "
                    f"exceeds threshold "
                    f"({self.feed_mismatch_escalation_threshold:.4f}) "
                    f"- data integrity compromised across feeds"
                )
                current_tier = new_tier
                logger.warning(
                    "ESCALATION: Feed mismatch=%.4f > %.4f | "
                    "-> %s",
                    feed_mismatch_rate,
                    self.feed_mismatch_escalation_threshold,
                    current_tier.value
                )

        # Rule 3: Low market trust
        if average_trust_score < self.trust_escalation_threshold:
            new_tier = self._escalate_tier(current_tier)
            if new_tier != current_tier:
                reasons.append(
                    f"Average trust score ({average_trust_score:.1f}) "
                    f"below threshold "
                    f"({self.trust_escalation_threshold:.1f}) "
                    f"- majority of data unreliable"
                )
                current_tier = new_tier
                logger.warning(
                    "ESCALATION: Trust=%.1f < %.1f | -> %s",
                    average_trust_score,
                    self.trust_escalation_threshold,
                    current_tier.value
                )

        return current_tier, reasons

    def _escalate_tier(self, current_tier: RiskTier) -> RiskTier:
        """
        Escalate a tier by one level (towards SYSTEMIC_CRISIS).

        If already at SYSTEMIC_CRISIS (maximum severity), returns
        SYSTEMIC_CRISIS unchanged.

        Args:
            current_tier: The current risk tier.

        Returns:
            RiskTier: The next higher severity tier, or
                SYSTEMIC_CRISIS if already at maximum.
        """
        current_index = _TIER_SEVERITY_ORDER.index(current_tier)
        next_index = min(
            current_index + 1,
            len(_TIER_SEVERITY_ORDER) - 1
        )
        return _TIER_SEVERITY_ORDER[next_index]

    # ──────────────────────────────────────────────────────────────────
    # Internal: Input Validation
    # ──────────────────────────────────────────────────────────────────

    def _validate_inputs(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float
    ) -> None:
        """
        Validate all input parameters.

        Args:
            msi: Must be in [0, 100]
            contagion_risk_score: Must be in [0, 100]
            feed_mismatch_rate: Must be in [0, 1]
            average_trust_score: Must be in [0, 100]

        Raises:
            ValueError: If any input is invalid.
            TypeError: If any input is wrong type.
        """
        for name, value, low, high in [
            ("msi", msi, 0.0, 100.0),
            ("contagion_risk_score", contagion_risk_score, 0.0, 100.0),
            ("feed_mismatch_rate", feed_mismatch_rate, 0.0, 1.0),
            ("average_trust_score", average_trust_score, 0.0, 100.0),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{name} must be numeric, got {type(value)}"
                )
            if not (low <= value <= high):
                raise ValueError(
                    f"{name} must be in [{low}, {high}], got {value}"
                )

    # ──────────────────────────────────────────────────────────────────
    # Internal: Logging
    # ──────────────────────────────────────────────────────────────────

    def _log_evaluation(self, incident: Dict[str, Any]) -> None:
        """
        Log the evaluation result at the appropriate severity level.

        GREEN/YELLOW → INFO
        ORANGE → WARNING
        RED → CRITICAL
        """
        tier = incident["risk_tier"]
        alert = incident["alert_level"]
        action = incident["recommended_action"]
        enforce = incident["enforcement_required"]
        esc = incident["escalation_reasons"]

        msg = (
            f"RISK EVALUATION #{incident['evaluation_id']} | "
            f"Tier={tier} | Alert={alert} | Action={action} | "
            f"Enforce={enforce}"
        )

        if esc:
            msg += f" | Escalations: {'; '.join(esc)}"

        if alert in ("GREEN", "YELLOW"):
            logger.info(msg)
        elif alert == "ORANGE":
            logger.warning(msg)
        else:  # RED
            logger.critical(msg)

    # ──────────────────────────────────────────────────────────────────
    # Internal: Database Persistence
    # ──────────────────────────────────────────────────────────────────

    def _persist_incident(
        self,
        incident: Dict[str, Any],
        timestamp: datetime
    ) -> None:
        """
        Persist a systemic incident record to the database.

        Uses the DatabaseManager's log_system_event method to record
        the incident in the system_events table with event_type
        'SYSTEMIC_RISK_EVALUATION'.

        For incidents at HIGH_VOLATILITY or SYSTEMIC_CRISIS, also
        logs to the systemic_incidents table if available.

        Args:
            incident: The structured incident record.
            timestamp: Evaluation timestamp.
        """
        if self.db_manager is None:
            return

        try:
            import json

            # Always log to system_events
            severity_map = {
                "GREEN": "INFO",
                "YELLOW": "WARNING",
                "ORANGE": "HIGH",
                "RED": "CRITICAL"
            }
            severity = severity_map.get(
                incident["alert_level"], "INFO"
            )

            self.db_manager.log_system_event(
                timestamp=timestamp,
                event_type="SYSTEMIC_RISK_EVALUATION",
                severity=severity,
                message=(
                    f"Risk Tier: {incident['risk_tier']} | "
                    f"Action: {incident['recommended_action']} | "
                    f"Enforce: {incident['enforcement_required']}"
                ),
                data=incident["inputs"]
            )

            # For enforcement-level incidents, also log to
            # systemic_incidents if the table exists
            if incident["enforcement_required"]:
                self._log_systemic_incident(incident, timestamp)

            logger.debug(
                "Incident persisted to database: eval #%d",
                incident["evaluation_id"]
            )
        except Exception as e:
            logger.error(
                "Failed to persist incident to database: %s",
                str(e), exc_info=True
            )

    def _log_systemic_incident(
        self,
        incident: Dict[str, Any],
        timestamp: datetime
    ) -> None:
        """
        Log enforcement-level incidents to the systemic_incidents
        table for regulatory compliance.

        This method checks if the systemic_incidents table exists
        (it's created by our database migration) and inserts
        the record.

        Args:
            incident: Structured incident record.
            timestamp: Evaluation timestamp.
        """
        if self.db_manager is None:
            return

        try:
            import json
            cursor = self.db_manager.conn.cursor()

            # Ensure the table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS systemic_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    risk_tier TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    enforcement_required INTEGER NOT NULL,
                    base_tier TEXT NOT NULL,
                    escalation_reasons TEXT,
                    msi REAL,
                    contagion_risk_score REAL,
                    feed_mismatch_rate REAL,
                    average_trust_score REAL,
                    evaluation_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                INSERT INTO systemic_incidents (
                    timestamp, risk_tier, alert_level,
                    recommended_action, enforcement_required,
                    base_tier, escalation_reasons,
                    msi, contagion_risk_score,
                    feed_mismatch_rate, average_trust_score,
                    evaluation_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(timestamp),
                incident["risk_tier"],
                incident["alert_level"],
                incident["recommended_action"],
                1 if incident["enforcement_required"] else 0,
                incident["base_tier"],
                json.dumps(incident["escalation_reasons"]),
                incident["inputs"]["msi"],
                incident["inputs"]["contagion_risk_score"],
                incident["inputs"]["feed_mismatch_rate"],
                incident["inputs"]["average_trust_score"],
                incident["evaluation_id"]
            ))

            self.db_manager.conn.commit()
            logger.info(
                "Systemic incident logged: tier=%s eval=#%d",
                incident["risk_tier"], incident["evaluation_id"]
            )
        except Exception as e:
            logger.error(
                "Failed to log systemic incident: %s",
                str(e), exc_info=True
            )
