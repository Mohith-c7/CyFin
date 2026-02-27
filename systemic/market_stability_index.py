"""
Market Stability Index (MSI) Module — V2
=========================================

This module computes a formal weighted Market Stability Index that aggregates
multiple market integrity signals into a single systemic risk indicator for
regulators and infrastructure operators.

The MSI is designed to provide early warning of market-wide instability by
combining trust metrics, anomaly rates, data feed quality, and cross-asset
contagion into a unified 0-100 score with clear risk classifications.

Version History:
    V1: Trust + Anomaly Rate + Anomaly Count + Feed Mismatch
    V2: Added Contagion Risk Score (CRS) component for truly
        systemic risk detection. Rebalanced weights to accommodate
        the new dimension while maintaining backward compatibility.

Mathematical Foundation (V2 — Calibrated):
    MSI = (
        1.00 * average_trust_score          [Trust: 0-100 points, full range]
        - 20 * market_anomaly_rate           [Anomaly rate penalty: 0-20 pts]
        - 4  * log(1 + total_anomalies)      [Volume penalty: logarithmic]
        - 25 * feed_mismatch_rate            [Feed quality penalty: 0-25 pts]
        - 0.30 * contagion_risk_score        [Contagion penalty: 0-30 pts]
    )

    Clamped to [0, 100] range.

    Calibration Rationale (V2 Calibrated):
    ─────────────────────────────────────────
    Trust:      1.00  → Full trust score maps directly to 0-100 contribution.
                        Perfect market (trust=100, zero penalties) → MSI=100.
                        Highly stressed market (trust=40, high penalties) → MSI=0.
    Anomaly:    20.0  → 20-point penalty at 100% anomaly rate.
    Log count:  4.0   → Logarithmic, stable for high-volume streams.
    Feed:       25.0  → 25-point penalty at 100% mismatch rate.
    Contagion:  0.30  → Up to 30-point penalty for max cross-asset contagion.

    Design Intent:
    The 1.0 trust weight ensures the STABLE threshold (≥80) is reachable
    for genuinely healthy markets (trust≈80-100, low anomalies/feed/contagion).
    With the previous 0.55 weight, the maximum achievable MSI was 55 — making
    STABLE permanently unreachable regardless of market conditions.
"""

import math
from typing import Dict, Union


class MarketStabilityIndex:
    """
    Computes Market Stability Index (MSI) for systemic risk assessment.

    The MSI is a composite metric that quantifies overall market health by
    integrating multiple data integrity, trust, and contagion signals. It
    serves as a macro-level indicator for:

    - Regulatory oversight and intervention decisions
    - Infrastructure health monitoring
    - Systemic risk early warning
    - Market-wide stability assessment

    The index ranges from 0 (critical systemic risk) to 100 (fully stable)
    and provides categorical risk classifications for operational
    decision-making.

    Mathematical Foundation (V2 — Calibrated):
    -------------------------------------------
    MSI = (
        1.00 * average_trust_score           [Trust: 0-100 points, full range]
        - 20 * market_anomaly_rate            [Anomaly penalty: 0-20 points]
        - 4  * log(1 + total_anomalies)       [Volume penalty: logarithmic]
        - 25 * feed_mismatch_rate             [Feed quality: 0-25 points]
        - 0.30 * contagion_risk_score         [Contagion: 0-30 points]
    )

    Clamped to [0, 100] range.

    Component Rationale:
    -------------------
    1. Trust Score (55% weight):
       - Primary indicator of data reliability
       - Reflects real-time confidence in market data
       - Highest weight as it directly measures integrity

    2. Anomaly Rate (20-point penalty):
       - Proportion of anomalous data points
       - Linear penalty for widespread anomalies
       - Indicates systematic data quality issues

    3. Total Anomalies (logarithmic penalty):
       - Absolute count of anomalies detected
       - Logarithmic to prevent domination by high-volume markets
       - Captures cumulative risk exposure

    4. Feed Mismatch Rate (25-point penalty):
       - Cross-feed validation failures
       - Critical for multi-source infrastructure
       - High weight due to systemic implications

    5. Contagion Risk Score (30% penalty):
       - Cross-asset correlation and volatility synchronization
       - Detects market-wide contagion dynamics
       - Most critical systemic risk signal

    Risk Classifications:
    --------------------
    MSI >= 80:  STABLE           - Normal operations, low intervention
    60-79:      ELEVATED RISK    - Increased monitoring, prepare response
    40-59:      HIGH VOLATILITY  - Active intervention, restrict operations
    < 40:       SYSTEMIC RISK    - Emergency protocols, halt if necessary

    Usage Example:
    -------------
    >>> msi_calculator = MarketStabilityIndex()
    >>> result = msi_calculator.compute_msi(
    ...     average_trust_score=85.0,
    ...     market_anomaly_rate=0.02,
    ...     total_anomalies=5,
    ...     feed_mismatch_rate=0.01,
    ...     contagion_risk_score=15.0
    ... )
    >>> print(f"MSI: {result['msi_score']:.2f} - {result['market_state']}")
    """

    # ──────────────────────────────────────────────────────────────────
    # MSI component weights V2-Calibrated (documented for regulatory transparency)
    # WEIGHT_TRUST = 1.00 ensures perfect market (trust=100, zero penalties)
    # gives MSI=100, making STABLE threshold (80) genuinely achievable.
    # ──────────────────────────────────────────────────────────────────
    WEIGHT_TRUST = 1.00               # Trust contribution (0-100 pts, full range)
    WEIGHT_ANOMALY_RATE = 20.0        # 20-point penalty at 100% anomaly rate
    WEIGHT_ANOMALY_LOG = 4.0          # Logarithmic scaling for anomaly count
    WEIGHT_FEED_MISMATCH = 25.0       # 25-point penalty at 100% mismatch rate
    WEIGHT_CONTAGION = 0.30           # 30-point penalty at CRS=100

    # MSI bounds
    MSI_MIN = 0.0
    MSI_MAX = 100.0

    # Risk classification thresholds
    THRESHOLD_STABLE = 80.0
    THRESHOLD_ELEVATED = 60.0
    THRESHOLD_HIGH_VOLATILITY = 40.0

    def __init__(self):
        """
        Initialize Market Stability Index calculator.

        No configuration required - uses standardized weights designed
        for regulatory and infrastructure monitoring use cases.
        """
        pass

    def compute_msi(
        self,
        average_trust_score: float,
        market_anomaly_rate: float,
        total_anomalies: int,
        feed_mismatch_rate: float = 0.0,
        contagion_risk_score: float = 0.0
    ) -> Dict[str, Union[float, str, Dict]]:
        """
        Compute Market Stability Index from market integrity metrics.

        This method aggregates multiple market health signals into a single
        MSI score with categorical risk classification. Designed for use by
        regulators, infrastructure operators, and risk management systems.

        Args:
            average_trust_score (float):
                Mean trust score across all monitored symbols.
                Range: 0-100, where 100 = fully trusted data.
                Typically computed as average of per-symbol trust scores.

            market_anomaly_rate (float):
                Proportion of data points flagged as anomalous.
                Range: 0-1, where 0 = no anomalies, 1 = all anomalous.
                Computed as: total_anomalies / total_data_points.

            total_anomalies (int):
                Absolute count of anomalies detected across all symbols.
                Range: 0+, unbounded integer.
                Provides volume context beyond rate.

            feed_mismatch_rate (float, optional):
                Proportion of cross-feed validation failures.
                Range: 0-1, where 0 = perfect agreement, 1 = total mismatch.
                Defaults to 0.0 if cross-feed validation not implemented.
                Sourced from FeedIntegrityEngine.get_global_feed_health().

            contagion_risk_score (float, optional):
                Cross-asset contagion risk score from the ContagionEngine.
                Range: 0-100, where 0 = no contagion, 100 = max contagion.
                Defaults to 0.0 if contagion engine not active.
                Sourced from ContagionEngine.get_contagion_summary().

        Returns:
            dict: Structured MSI result containing:
                {
                    "msi_score": float,
                        The computed Market Stability Index (0-100).
                        Higher values indicate greater stability.

                    "market_state": str,
                        Categorical classification of market condition:
                        - "STABLE": MSI >= 80
                        - "ELEVATED RISK": 60 <= MSI < 80
                        - "HIGH VOLATILITY": 40 <= MSI < 60
                        - "SYSTEMIC RISK": MSI < 40

                    "risk_level": str,
                        Simplified risk indicator for operational use:
                        - "LOW": STABLE state
                        - "MEDIUM": ELEVATED RISK state
                        - "HIGH": HIGH VOLATILITY state
                        - "CRITICAL": SYSTEMIC RISK state

                    "inputs_used": dict,
                        Echo of all input parameters for audit trail.
                }

        Raises:
            ValueError: If inputs are outside valid ranges.
            TypeError: If inputs are wrong type.

        Mathematical Formula (V2-Calibrated):
        ----------------------------------------
        MSI = (
            1.00 * average_trust_score
            - 20  * market_anomaly_rate
            - 4   * log(1 + total_anomalies)
            - 25  * feed_mismatch_rate
            - 0.30 * contagion_risk_score
        )

        Then clamped to [0, 100].
        Perfect market (trust=100, all penalties=0) → MSI=100 (STABLE).

        Integration Example::

            >>> from systemic.contagion_engine import ContagionEngine
            >>> from feed_validation import FeedIntegrityEngine
            >>> from systemic.market_stability_index import MarketStabilityIndex
            >>>
            >>> contagion = ContagionEngine()
            >>> feed_engine = FeedIntegrityEngine()
            >>> msi_calc = MarketStabilityIndex()
            >>>
            >>> # ... process data through engines ...
            >>>
            >>> contagion_summary = contagion.get_contagion_summary()
            >>> feed_health = feed_engine.get_global_feed_health()
            >>>
            >>> result = msi_calc.compute_msi(
            ...     average_trust_score=85.0,
            ...     market_anomaly_rate=0.02,
            ...     total_anomalies=5,
            ...     feed_mismatch_rate=feed_health['global_feed_mismatch_rate'],
            ...     contagion_risk_score=contagion_summary['contagion_risk_score']
            ... )
        """
        # Input validation
        self._validate_inputs(
            average_trust_score,
            market_anomaly_rate,
            total_anomalies,
            feed_mismatch_rate,
            contagion_risk_score
        )

        # Compute MSI components
        trust_component = self.WEIGHT_TRUST * average_trust_score
        anomaly_rate_penalty = self.WEIGHT_ANOMALY_RATE * market_anomaly_rate
        anomaly_count_penalty = self.WEIGHT_ANOMALY_LOG * math.log(
            1 + total_anomalies
        )
        feed_mismatch_penalty = self.WEIGHT_FEED_MISMATCH * feed_mismatch_rate
        contagion_penalty = self.WEIGHT_CONTAGION * contagion_risk_score

        # Aggregate MSI
        msi_raw = (
            trust_component
            - anomaly_rate_penalty
            - anomaly_count_penalty
            - feed_mismatch_penalty
            - contagion_penalty
        )

        # Clamp to valid range
        msi_score = max(self.MSI_MIN, min(self.MSI_MAX, msi_raw))

        # Classify market state
        market_state = self._classify_market_state(msi_score)
        risk_level = self._determine_risk_level(market_state)

        # Structure output
        result = {
            "msi_score": round(msi_score, 2),
            "market_state": market_state,
            "risk_level": risk_level,
            "inputs_used": {
                "average_trust_score": average_trust_score,
                "market_anomaly_rate": market_anomaly_rate,
                "total_anomalies": total_anomalies,
                "feed_mismatch_rate": feed_mismatch_rate,
                "contagion_risk_score": contagion_risk_score
            }
        }

        return result

    def _validate_inputs(
        self,
        average_trust_score: float,
        market_anomaly_rate: float,
        total_anomalies: int,
        feed_mismatch_rate: float,
        contagion_risk_score: float = 0.0
    ) -> None:
        """
        Validate input parameters for MSI computation.

        Ensures all inputs are within valid ranges and of correct types
        to prevent computation errors and maintain data integrity.

        Args:
            average_trust_score: Must be float in [0, 100]
            market_anomaly_rate: Must be float in [0, 1]
            total_anomalies: Must be non-negative integer
            feed_mismatch_rate: Must be float in [0, 1]
            contagion_risk_score: Must be float in [0, 100]

        Raises:
            ValueError: If any input is invalid
            TypeError: If any input is wrong type
        """
        # Type validation
        if not isinstance(average_trust_score, (int, float)):
            raise TypeError(
                f"average_trust_score must be numeric, "
                f"got {type(average_trust_score)}"
            )

        if not isinstance(market_anomaly_rate, (int, float)):
            raise TypeError(
                f"market_anomaly_rate must be numeric, "
                f"got {type(market_anomaly_rate)}"
            )

        if not isinstance(total_anomalies, int):
            raise TypeError(
                f"total_anomalies must be integer, "
                f"got {type(total_anomalies)}"
            )

        if not isinstance(feed_mismatch_rate, (int, float)):
            raise TypeError(
                f"feed_mismatch_rate must be numeric, "
                f"got {type(feed_mismatch_rate)}"
            )

        if not isinstance(contagion_risk_score, (int, float)):
            raise TypeError(
                f"contagion_risk_score must be numeric, "
                f"got {type(contagion_risk_score)}"
            )

        # Range validation
        if not (0 <= average_trust_score <= 100):
            raise ValueError(
                f"average_trust_score must be in [0, 100], "
                f"got {average_trust_score}"
            )

        if not (0 <= market_anomaly_rate <= 1):
            raise ValueError(
                f"market_anomaly_rate must be in [0, 1], "
                f"got {market_anomaly_rate}"
            )

        if total_anomalies < 0:
            raise ValueError(
                f"total_anomalies must be non-negative, "
                f"got {total_anomalies}"
            )

        if not (0 <= feed_mismatch_rate <= 1):
            raise ValueError(
                f"feed_mismatch_rate must be in [0, 1], "
                f"got {feed_mismatch_rate}"
            )

        if not (0 <= contagion_risk_score <= 100):
            raise ValueError(
                f"contagion_risk_score must be in [0, 100], "
                f"got {contagion_risk_score}"
            )

    def _classify_market_state(self, msi_score: float) -> str:
        """
        Classify market state based on MSI score.

        Uses regulatory-defined thresholds to categorize market condition
        into one of four states for operational decision-making.

        Args:
            msi_score: Computed MSI value (0-100)

        Returns:
            str: Market state classification
                - "STABLE": Normal operations
                - "ELEVATED RISK": Increased monitoring
                - "HIGH VOLATILITY": Active intervention
                - "SYSTEMIC RISK": Emergency protocols
        """
        if msi_score >= self.THRESHOLD_STABLE:
            return "STABLE"
        elif msi_score >= self.THRESHOLD_ELEVATED:
            return "ELEVATED RISK"
        elif msi_score >= self.THRESHOLD_HIGH_VOLATILITY:
            return "HIGH VOLATILITY"
        else:
            return "SYSTEMIC RISK"

    def _determine_risk_level(self, market_state: str) -> str:
        """
        Map market state to simplified risk level.

        Provides a simplified risk indicator for systems that need
        basic LOW/MEDIUM/HIGH/CRITICAL classification.

        Args:
            market_state: Market state classification

        Returns:
            str: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        risk_mapping = {
            "STABLE": "LOW",
            "ELEVATED RISK": "MEDIUM",
            "HIGH VOLATILITY": "HIGH",
            "SYSTEMIC RISK": "CRITICAL"
        }
        return risk_mapping.get(market_state, "UNKNOWN")

    def get_component_breakdown(
        self,
        average_trust_score: float,
        market_anomaly_rate: float,
        total_anomalies: int,
        feed_mismatch_rate: float = 0.0,
        contagion_risk_score: float = 0.0
    ) -> Dict[str, float]:
        """
        Get detailed breakdown of MSI components for analysis.

        Useful for understanding which factors are driving MSI changes
        and for regulatory reporting requirements.

        Args:
            Same as compute_msi()

        Returns:
            dict: Component contributions to MSI
                {
                    "trust_contribution": float,
                    "anomaly_rate_penalty": float,
                    "anomaly_count_penalty": float,
                    "feed_mismatch_penalty": float,
                    "contagion_penalty": float,
                    "raw_msi": float,
                    "clamped_msi": float
                }
        """
        self._validate_inputs(
            average_trust_score,
            market_anomaly_rate,
            total_anomalies,
            feed_mismatch_rate,
            contagion_risk_score
        )

        trust_contribution = self.WEIGHT_TRUST * average_trust_score
        anomaly_rate_penalty = self.WEIGHT_ANOMALY_RATE * market_anomaly_rate
        anomaly_count_penalty = self.WEIGHT_ANOMALY_LOG * math.log(
            1 + total_anomalies
        )
        feed_mismatch_penalty = self.WEIGHT_FEED_MISMATCH * feed_mismatch_rate
        contagion_penalty = self.WEIGHT_CONTAGION * contagion_risk_score

        raw_msi = (
            trust_contribution
            - anomaly_rate_penalty
            - anomaly_count_penalty
            - feed_mismatch_penalty
            - contagion_penalty
        )

        clamped_msi = max(self.MSI_MIN, min(self.MSI_MAX, raw_msi))

        return {
            "trust_contribution": round(trust_contribution, 2),
            "anomaly_rate_penalty": round(anomaly_rate_penalty, 2),
            "anomaly_count_penalty": round(anomaly_count_penalty, 2),
            "feed_mismatch_penalty": round(feed_mismatch_penalty, 2),
            "contagion_penalty": round(contagion_penalty, 2),
            "raw_msi": round(raw_msi, 2),
            "clamped_msi": round(clamped_msi, 2)
        }
