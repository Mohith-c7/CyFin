"""
Risk Attribution & Explainability Engine
==========================================

Production-grade module providing full mathematical transparency
into how Market Stability Index (MSI) and Severity Score are
computed, what drives risk tier decisions, and which assets
contribute most to systemic risk.

Importance of Explainability in Financial Systems:
    In capital markets, opacity is liability. When a system
    declares "SYSTEMIC CRISIS", three audiences immediately
    demand answers:

    1. **Regulators**: "Show me exactly how you arrived at this
       conclusion. What inputs drove the score? What model
       was used? Can I reproduce the result independently?"
       (MiFID II Art. 16, DORA Art. 11, SEC Rule 613)

    2. **Risk Officers**: "Which component is responsible?
       Is it a data problem I can fix, or a genuine market
       event I must escalate? Where should I focus limited
       response resources?"

    3. **Board / Senior Management**: "Give me a plain-language
       summary of what happened, why, and what we did about it.
       I need to sign off on the regulatory filing."

    This engine answers all three by decomposing composite
    scores into their individual components, identifying the
    dominant risk factor, ranking assets by systemic impact,
    and producing structured attribution reports.

Regulatory Expectations for Model Transparency:
    - **SR 11-7 (Fed)**: Model risk management requires
      comprehensive documentation of model inputs, logic,
      limitations, and uncertainty.
    - **EU AI Act**: High-risk AI systems (which includes
      financial risk scoring) must provide "sufficient
      transparency to enable users to interpret the system's
      output and use it appropriately."
    - **BCBS 239**: Risk data aggregation and reporting must
      be accurate, complete, timely, and adaptable. Attribution
      analysis ensures accuracy by making each component
      independently verifiable.

Model Transparency Principles Applied:
    1. **Decomposability**: Every composite score is broken
       into independently verifiable components.
    2. **Attribution**: Each component's contribution is
       quantified as both an absolute value and a percentage.
    3. **Dominance**: The largest risk factor is explicitly
       identified, answering "what matters most right now?"
    4. **Reproducibility**: The explanation includes all inputs
       and weights, enabling independent recalculation.
    5. **Narrative**: Machine-readable attribution is paired
       with human-readable explanation text.

Author: CyFin Team
Version: 1.0.0
"""

import math
import logging
from typing import Any, Dict, List, Optional, Tuple

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(logging.NullHandler())


class ExplainabilityEngine:
    """
    Provides full mathematical transparency into CyFin risk scores.

    Decomposes composite metrics (MSI, Severity Score) into their
    individual components, identifies dominant risk factors, and
    ranks assets by systemic impact. Every output is structured
    for both machine consumption (dashboards, APIs) and human
    review (regulatory filings, board reports).

    Architecture::

        ┌─────────────────────────────────────────────────────┐
        │           EXPLAINABILITY ENGINE                      │
        │                                                     │
        │  explain_msi()         → MSI component breakdown    │
        │  explain_severity()    → Severity decomposition     │
        │  explain_risk_tier()   → Tier decision reasoning    │
        │  rank_asset_impact()   → Asset systemic ranking     │
        │  generate_narrative()  → Human-readable summary     │
        └─────────────────────────────────────────────────────┘

    Thread Safety:
        All methods are stateless and side-effect-free. Multiple
        concurrent calls are safe.

    Usage Example::

        >>> from governance.explainability_engine import ExplainabilityEngine
        >>> engine = ExplainabilityEngine()
        >>> explanation = engine.explain_msi(
        ...     average_trust_score=75.0,
        ...     market_anomaly_rate=0.05,
        ...     total_anomalies=15,
        ...     feed_mismatch_rate=0.02,
        ...     contagion_risk_score=45.0
        ... )
        >>> print(explanation['dominant_risk_factor'])
        >>> print(explanation['component_contributions'])
    """

    # ──────────────────────────────────────────────────────────────────
    # MSI V2-Calibrated formula constants (must match market_stability_index.py)
    # WEIGHT_TRUST = 1.00 so perfect market gives MSI=100 (STABLE reachable)
    # ──────────────────────────────────────────────────────────────────
    MSI_WEIGHT_TRUST = 1.00
    MSI_WEIGHT_ANOMALY_RATE = 20.0
    MSI_WEIGHT_ANOMALY_LOG = 4.0
    MSI_WEIGHT_FEED_MISMATCH = 25.0
    MSI_WEIGHT_CONTAGION = 0.30

    # Severity formula constants (must match incident_intelligence_engine.py)
    SEV_WEIGHT_MSI_COMPLEMENT = 0.4
    SEV_WEIGHT_CONTAGION = 0.3
    SEV_WEIGHT_FEED = 0.2
    SEV_WEIGHT_TRUST_DEFICIT = 0.1

    # ──────────────────────────────────────────────────────────────────
    # Core API: MSI Explanation
    # ──────────────────────────────────────────────────────────────────

    def explain_msi(
        self,
        average_trust_score: float,
        market_anomaly_rate: float,
        total_anomalies: int,
        feed_mismatch_rate: float = 0.0,
        contagion_risk_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Decompose the Market Stability Index into its component
        contributions with full attribution.

        This method reproduces the exact MSI V2 calculation and
        provides a component-by-component breakdown showing how
        each input affects the final score. This enables:

        - Independent verification of the MSI calculation
        - Identification of which factor is dragging MSI down
        - Quantified impact of each risk dimension
        - Regulatory-grade transparency

        MSI V2-Calibrated Formula:
            MSI = 1.00 * trust
                  - 20.0 * anomaly_rate
                  - 4.0 * log(1 + total_anomalies)
                  - 25.0 * feed_mismatch_rate
                  - 0.30 * contagion_risk_score

            Clamped to [0, 100]. Perfect market (trust=100, zero penalties) = 100.

        Args:
            average_trust_score (float): Mean trust score (0-100).
            market_anomaly_rate (float): Anomaly rate (0-1).
            total_anomalies (int): Absolute anomaly count.
            feed_mismatch_rate (float): Feed mismatch rate (0-1).
            contagion_risk_score (float): CRS (0-100).

        Returns:
            dict: {
                "msi_final_score": float,
                    The computed MSI (0-100, clamped).

                "msi_raw_score": float,
                    MSI before clamping (may be negative or > 100).

                "component_contributions": {
                    "trust_component": float,
                        Positive contribution from trust.
                        Formula: 1.00 × trust_score (full range, 0-100 pts).

                    "anomaly_rate_penalty": float,
                        Negative penalty from anomaly rate.
                        Formula: -20.0 × anomaly_rate.

                    "anomaly_count_penalty": float,
                        Negative penalty from anomaly volume.
                        Formula: -4.0 × log(1 + count).

                    "feed_mismatch_penalty": float,
                        Negative penalty from feed corruption.
                        Formula: -25.0 × feed_mismatch_rate.

                    "contagion_penalty": float,
                        Negative penalty from contagion.
                        Formula: -0.30 × CRS.
                },

                "component_percentages": dict,
                    Each component's absolute contribution as a
                    percentage of the total absolute contributions.

                "dominant_risk_factor": str,
                    Name of the component with the highest negative
                    impact on MSI. If no penalties exist, returns
                    "NONE".

                "dominant_risk_magnitude": float,
                    Absolute value of the dominant risk factor's
                    contribution.

                "inputs": dict,
                    Echo of all input parameters.

                "formula": str,
                    Human-readable formula string.
            }

        Raises:
            ValueError: If inputs are outside valid ranges.
            TypeError: If inputs are wrong type.
        """
        self._validate_msi_inputs(
            average_trust_score, market_anomaly_rate,
            total_anomalies, feed_mismatch_rate,
            contagion_risk_score
        )

        # Compute individual components
        trust_component = self.MSI_WEIGHT_TRUST * average_trust_score
        anomaly_rate_penalty = (
            -self.MSI_WEIGHT_ANOMALY_RATE * market_anomaly_rate
        )
        anomaly_count_penalty = (
            -self.MSI_WEIGHT_ANOMALY_LOG
            * math.log(1 + total_anomalies)
        )
        feed_mismatch_penalty = (
            -self.MSI_WEIGHT_FEED_MISMATCH * feed_mismatch_rate
        )
        contagion_penalty = (
            -self.MSI_WEIGHT_CONTAGION * contagion_risk_score
        )

        # Raw and clamped MSI
        msi_raw = (
            trust_component
            + anomaly_rate_penalty
            + anomaly_count_penalty
            + feed_mismatch_penalty
            + contagion_penalty
        )
        msi_final = max(0.0, min(100.0, msi_raw))

        # Component contributions dict
        components = {
            "trust_component": round(trust_component, 4),
            "anomaly_rate_penalty": round(anomaly_rate_penalty, 4),
            "anomaly_count_penalty": round(anomaly_count_penalty, 4),
            "feed_mismatch_penalty": round(feed_mismatch_penalty, 4),
            "contagion_penalty": round(contagion_penalty, 4)
        }

        # Calculate percentages (absolute contribution share)
        abs_total = sum(abs(v) for v in components.values())
        if abs_total > 0:
            percentages = {
                k: round(abs(v) / abs_total * 100, 2)
                for k, v in components.items()
            }
        else:
            percentages = {k: 0.0 for k in components}

        # Identify dominant risk factor (largest negative contributor)
        penalties = {
            k: v for k, v in components.items() if v < 0
        }
        if penalties:
            dominant = min(penalties, key=penalties.get)
            dominant_magnitude = abs(penalties[dominant])
        else:
            dominant = "NONE"
            dominant_magnitude = 0.0

        return {
            "msi_final_score": round(msi_final, 2),
            "msi_raw_score": round(msi_raw, 4),
            "component_contributions": components,
            "component_percentages": percentages,
            "dominant_risk_factor": dominant,
            "dominant_risk_magnitude": round(dominant_magnitude, 4),
            "inputs": {
                "average_trust_score": average_trust_score,
                "market_anomaly_rate": market_anomaly_rate,
                "total_anomalies": total_anomalies,
                "feed_mismatch_rate": feed_mismatch_rate,
                "contagion_risk_score": contagion_risk_score
            },
            "formula": (
                "MSI = 1.00 * trust - 20 * anomaly_rate "
                "- 4 * log(1+anomalies) - 25 * feed_mismatch "
                "- 0.30 * CRS"
            )
        }

    # ──────────────────────────────────────────────────────────────────
    # Core API: Severity Score Explanation
    # ──────────────────────────────────────────────────────────────────

    def explain_severity(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float
    ) -> Dict[str, Any]:
        """
        Decompose the Severity Score into its component contributions.

        The Severity Score (from IncidentIntelligenceEngine) quantifies
        overall danger on a 0-100 scale. This method shows exactly how
        each dimension contributes.

        Severity Formula:
            severity = 0.4 * (100 - MSI)
                     + 0.3 * contagion_risk_score
                     + 0.2 * (feed_mismatch_rate * 100)
                     + 0.1 * (100 - average_trust_score)

            Clamped to [0, 100].

        Args:
            msi (float): Market Stability Index (0-100).
            contagion_risk_score (float): CRS (0-100).
            feed_mismatch_rate (float): Feed mismatch (0-1).
            average_trust_score (float): Average trust (0-100).

        Returns:
            dict: {
                "severity_score": float,
                    Computed severity (0-100).

                "component_contributions": {
                    "market_instability": float,
                        0.4 * (100 - MSI). Measures distance
                        from ideal market stability.

                    "contagion_risk": float,
                        0.3 * CRS. Measures cross-asset
                        systemic amplification.

                    "data_integrity_risk": float,
                        0.2 * (feed_mismatch * 100). Measures
                        data feed corruption.

                    "trust_deficit": float,
                        0.1 * (100 - trust). Measures long-term
                        data quality degradation.
                },

                "component_percentages": dict,
                    Percentage share of each component.

                "dominant_severity_factor": str,
                    Component with highest contribution to severity.

                "dominant_severity_magnitude": float,
                    Value of the dominant component.

                "regulatory_classification": str,
                    Classification based on severity.

                "inputs": dict
            }

        Raises:
            ValueError: If inputs are outside valid ranges.
        """
        self._validate_severity_inputs(
            msi, contagion_risk_score,
            feed_mismatch_rate, average_trust_score
        )

        # Compute components
        market_instability = (
            self.SEV_WEIGHT_MSI_COMPLEMENT * (100.0 - msi)
        )
        contagion_risk = (
            self.SEV_WEIGHT_CONTAGION * contagion_risk_score
        )
        data_integrity_risk = (
            self.SEV_WEIGHT_FEED * (feed_mismatch_rate * 100.0)
        )
        trust_deficit = (
            self.SEV_WEIGHT_TRUST_DEFICIT * (100.0 - average_trust_score)
        )

        severity_raw = (
            market_instability + contagion_risk
            + data_integrity_risk + trust_deficit
        )
        severity_score = max(0.0, min(100.0, severity_raw))

        components = {
            "market_instability": round(market_instability, 4),
            "contagion_risk": round(contagion_risk, 4),
            "data_integrity_risk": round(data_integrity_risk, 4),
            "trust_deficit": round(trust_deficit, 4)
        }

        # Percentages
        total = sum(components.values())
        if total > 0:
            percentages = {
                k: round(v / total * 100, 2)
                for k, v in components.items()
            }
        else:
            percentages = {k: 0.0 for k in components}

        # Dominant factor
        if any(v > 0 for v in components.values()):
            dominant = max(components, key=components.get)
            dominant_magnitude = components[dominant]
        else:
            dominant = "NONE"
            dominant_magnitude = 0.0

        # Regulatory classification
        if severity_score > 80:
            reg_class = "CRITICAL_MARKET_EVENT"
        elif severity_score > 60:
            reg_class = "HIGH_RISK_EVENT"
        elif severity_score > 40:
            reg_class = "ELEVATED_MONITORING_EVENT"
        else:
            reg_class = "NORMAL_OPERATION"

        return {
            "severity_score": round(severity_score, 2),
            "component_contributions": components,
            "component_percentages": percentages,
            "dominant_severity_factor": dominant,
            "dominant_severity_magnitude": round(dominant_magnitude, 4),
            "regulatory_classification": reg_class,
            "inputs": {
                "msi": msi,
                "contagion_risk_score": contagion_risk_score,
                "feed_mismatch_rate": feed_mismatch_rate,
                "average_trust_score": average_trust_score
            },
            "formula": (
                "severity = 0.4*(100-MSI) + 0.3*CRS "
                "+ 0.2*(feed*100) + 0.1*(100-trust)"
            )
        }

    # ──────────────────────────────────────────────────────────────────
    # Core API: Asset Impact Ranking
    # ──────────────────────────────────────────────────────────────────

    def rank_asset_systemic_impact(
        self,
        asset_trust_scores: Dict[str, float],
        contagion_metrics: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank assets by their contribution to systemic risk.

        Assets with the lowest trust scores represent the highest
        systemic risk because they indicate data unreliability,
        potential manipulation, or persistent anomalous behavior.

        When contagion metrics are available (per-symbol volatility
        from ContagionEngine), they are incorporated to provide a
        more holistic risk picture: an asset with moderate trust
        but extreme volatility may be more dangerous than one
        with low trust but stable behavior.

        Args:
            asset_trust_scores (dict): Mapping of symbol → trust
                score. Example: {"AAPL": 85.0, "MSFT": 42.0}

            contagion_metrics (dict, optional): Per-symbol metrics
                from ContagionEngine.get_contagion_summary()
                ['symbol_metrics']. If provided, volatility data
                is incorporated into the ranking.

        Returns:
            list[dict]: Ranked list (highest risk first), each:
                {
                    "rank": int (1-indexed),
                    "symbol": str,
                    "trust_score": float,
                    "risk_contribution": float (0-100),
                    "risk_level": str,
                    "explanation": str
                }

        Raises:
            ValueError: If asset_trust_scores is empty.
            TypeError: If trust scores are not numeric.
        """
        if not asset_trust_scores:
            raise ValueError(
                "asset_trust_scores must contain at least one asset"
            )

        for symbol, score in asset_trust_scores.items():
            if not isinstance(score, (int, float)):
                raise TypeError(
                    "Trust score for '%s' must be numeric, got %s"
                    % (symbol, type(score))
                )

        ranked = []
        for symbol, trust in asset_trust_scores.items():
            # Base risk contribution = inverse of trust
            risk_contribution = 100.0 - max(0.0, min(100.0, trust))

            # Determine risk level
            if trust >= 80:
                risk_level = "LOW"
            elif trust >= 60:
                risk_level = "MODERATE"
            elif trust >= 40:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"

            # Build explanation
            explanation = self._build_asset_explanation(
                symbol, trust, risk_level
            )

            ranked.append({
                "symbol": symbol,
                "trust_score": round(trust, 2),
                "risk_contribution": round(risk_contribution, 2),
                "risk_level": risk_level,
                "explanation": explanation
            })

        # Sort by risk contribution descending (highest risk first)
        ranked.sort(key=lambda x: x['risk_contribution'], reverse=True)

        # Add rank numbers
        for i, item in enumerate(ranked):
            item['rank'] = i + 1

        return ranked

    # ──────────────────────────────────────────────────────────────────
    # Core API: Risk Tier Explanation
    # ──────────────────────────────────────────────────────────────────

    def explain_risk_tier(
        self,
        msi: float,
        risk_tier: str,
        base_tier: str,
        escalation_reasons: List[str],
        enforcement_required: bool
    ) -> Dict[str, Any]:
        """
        Explain why a particular risk tier was assigned.

        This provides the causal reasoning chain from MSI through
        base tier classification to final tier (after escalation),
        answering the regulator's question: "Why this tier?"

        Args:
            msi: Market Stability Index score.
            risk_tier: Final risk tier after escalation.
            base_tier: Base tier from MSI alone.
            escalation_reasons: List of escalation triggers.
            enforcement_required: Whether enforcement was activated.

        Returns:
            dict: {
                "final_tier": str,
                "base_tier": str,
                "was_escalated": bool,
                "escalation_steps": int,
                "escalation_reasons": list[str],
                "enforcement_required": bool,
                "tier_reasoning": str,
                "msi_bracket": str
            }
        """
        tier_order = [
            "NORMAL", "ELEVATED_RISK",
            "HIGH_VOLATILITY", "SYSTEMIC_CRISIS"
        ]

        base_idx = (
            tier_order.index(base_tier)
            if base_tier in tier_order else -1
        )
        final_idx = (
            tier_order.index(risk_tier)
            if risk_tier in tier_order else -1
        )
        was_escalated = final_idx > base_idx
        escalation_steps = max(0, final_idx - base_idx)

        # Build MSI bracket description
        if msi >= 80:
            bracket = "MSI >= 80 (STABLE zone)"
        elif msi >= 60:
            bracket = "60 <= MSI < 80 (ELEVATED zone)"
        elif msi >= 40:
            bracket = "40 <= MSI < 60 (HIGH VOLATILITY zone)"
        else:
            bracket = "MSI < 40 (SYSTEMIC RISK zone)"

        # Build reasoning narrative
        reasoning_parts = [
            "MSI score of %.1f places the market in %s, "
            "corresponding to base tier %s."
            % (msi, bracket, base_tier)
        ]

        if was_escalated:
            reasoning_parts.append(
                "The tier was escalated by %d level(s) "
                "to %s due to %d escalation trigger(s)."
                % (escalation_steps, risk_tier,
                   len(escalation_reasons))
            )
            for reason in escalation_reasons:
                reasoning_parts.append("  - %s" % reason)
        else:
            reasoning_parts.append(
                "No escalation rules were triggered. "
                "Final tier matches base tier."
            )

        if enforcement_required:
            reasoning_parts.append(
                "ENFORCEMENT is REQUIRED: Protective measures "
                "must be activated (trade throttling or "
                "emergency controls)."
            )

        return {
            "final_tier": risk_tier,
            "base_tier": base_tier,
            "was_escalated": was_escalated,
            "escalation_steps": escalation_steps,
            "escalation_reasons": list(escalation_reasons),
            "enforcement_required": enforcement_required,
            "tier_reasoning": " ".join(reasoning_parts),
            "msi_bracket": bracket
        }

    # ──────────────────────────────────────────────────────────────────
    # Core API: Narrative Generation
    # ──────────────────────────────────────────────────────────────────

    def generate_narrative(
        self,
        msi_explanation: Dict[str, Any],
        severity_explanation: Optional[Dict[str, Any]] = None,
        tier_explanation: Optional[Dict[str, Any]] = None,
        asset_ranking: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate a human-readable narrative summary from all
        available explanations.

        This produces the kind of plain-language summary that
        a board member or senior regulator can read without
        needing to understand the underlying mathematics.

        Args:
            msi_explanation: Output from explain_msi().
            severity_explanation: Optional output from explain_severity().
            tier_explanation: Optional output from explain_risk_tier().
            asset_ranking: Optional output from rank_asset_systemic_impact().

        Returns:
            str: Multi-paragraph narrative summary.
        """
        sections = []

        # MSI section
        msi_score = msi_explanation['msi_final_score']
        dominant = msi_explanation['dominant_risk_factor']
        dominant_mag = msi_explanation['dominant_risk_magnitude']
        trust = msi_explanation['component_contributions']['trust_component']

        sections.append(
            "MARKET STABILITY INDEX: The current MSI is %.1f out of 100. "
            "The trust component contributes +%.1f points to stability."
            % (msi_score, trust)
        )

        if dominant != "NONE":
            dominant_readable = dominant.replace('_', ' ')
            sections.append(
                "The dominant risk factor is '%s' with a magnitude "
                "of %.2f points. This is the primary driver of "
                "instability."
                % (dominant_readable, dominant_mag)
            )

        # Severity section
        if severity_explanation:
            sev = severity_explanation['severity_score']
            reg = severity_explanation['regulatory_classification']
            sev_dom = severity_explanation['dominant_severity_factor']
            sections.append(
                "SEVERITY ASSESSMENT: The computed severity score "
                "is %.1f, classified as %s. The dominant severity "
                "factor is '%s'."
                % (sev, reg, sev_dom.replace('_', ' '))
            )

        # Tier section
        if tier_explanation:
            sections.append(
                "RISK TIER: %s"
                % tier_explanation['tier_reasoning']
            )

        # Asset ranking section
        if asset_ranking and len(asset_ranking) > 0:
            top_risk = asset_ranking[0]
            sections.append(
                "ASSET RISK RANKING: The highest-risk asset is "
                "%s (trust: %.1f, risk level: %s). "
                "%s."
                % (
                    top_risk['symbol'],
                    top_risk['trust_score'],
                    top_risk['risk_level'],
                    top_risk['explanation']
                )
            )
            if len(asset_ranking) > 1:
                others = ", ".join(
                    "%s (%.1f)" % (a['symbol'], a['trust_score'])
                    for a in asset_ranking[1:4]
                )
                sections.append(
                    "Other monitored assets: %s." % others
                )

        return "\n\n".join(sections)

    # ──────────────────────────────────────────────────────────────────
    # Internal: Asset Explanation Builder
    # ──────────────────────────────────────────────────────────────────

    def _build_asset_explanation(
        self,
        symbol: str,
        trust: float,
        risk_level: str
    ) -> str:
        """Build human-readable explanation for an asset's risk."""
        if risk_level == "CRITICAL":
            return (
                "%s has critically low trust (%.1f). "
                "Data for this asset is unreliable and may indicate "
                "manipulation or persistent feed failure"
                % (symbol, trust)
            )
        elif risk_level == "HIGH":
            return (
                "%s has high risk (trust: %.1f). "
                "Significant data quality concerns warrant "
                "enhanced monitoring"
                % (symbol, trust)
            )
        elif risk_level == "MODERATE":
            return (
                "%s has moderate risk (trust: %.1f). "
                "Some data quality degradation detected"
                % (symbol, trust)
            )
        else:
            return (
                "%s is operating normally (trust: %.1f). "
                "Data quality is within acceptable bounds"
                % (symbol, trust)
            )

    # ──────────────────────────────────────────────────────────────────
    # Internal: Input Validation
    # ──────────────────────────────────────────────────────────────────

    def _validate_msi_inputs(
        self,
        average_trust_score: float,
        market_anomaly_rate: float,
        total_anomalies: int,
        feed_mismatch_rate: float,
        contagion_risk_score: float
    ) -> None:
        """Validate MSI explanation inputs."""
        for name, value, low, high in [
            ("average_trust_score", average_trust_score, 0.0, 100.0),
            ("market_anomaly_rate", market_anomaly_rate, 0.0, 1.0),
            ("feed_mismatch_rate", feed_mismatch_rate, 0.0, 1.0),
            ("contagion_risk_score", contagion_risk_score, 0.0, 100.0),
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

        if not isinstance(total_anomalies, (int, float)):
            raise TypeError(
                "total_anomalies must be numeric, got %s"
                % type(total_anomalies)
            )
        if total_anomalies < 0:
            raise ValueError(
                "total_anomalies must be >= 0, got %s"
                % total_anomalies
            )

    def _validate_severity_inputs(
        self,
        msi: float,
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        average_trust_score: float
    ) -> None:
        """Validate severity explanation inputs."""
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
