"""
Systemic Stress Simulation & Resilience Engine
=================================================

Production-grade engine for simulating structured financial shock
scenarios and measuring projected Market Stability Index (MSI)
degradation, crisis sensitivity, and systemic resilience.

Stress Testing Philosophy:
    Financial system resilience cannot be assessed from
    steady-state observation alone. The 2008 Global Financial
    Crisis, the 2020 COVID shock, and the 2022 Gilt crisis all
    demonstrated that systems which appeared robust in normal
    conditions can shatter under stress.

    Stress testing answers the forward-looking question:

        "If X happens, how badly would our stability degrade,
         and would our protective controls be sufficient?"

    This is fundamentally different from detection (what IS
    happening) or forensics (what DID happen). Stress testing
    is about preparation and resilience.

Financial Regulatory Parallels:
    - **Basel III Stress Testing (BCBS 239)**: Banks must conduct
      regular stress tests to assess capital adequacy under
      adverse scenarios. Our engine performs analogous stress
      tests on market data integrity infrastructure.

    - **EU-wide Stress Tests (EBA)**: The European Banking
      Authority mandates institution-wide scenario analysis.
      Our StressSimulationEngine operates the same way—applying
      shocks and measuring downstream degradation.

    - **Fed DFAST/CCAR**: The Federal Reserve's Dodd-Frank Act
      Stress Tests require scenarios including severe economic
      downturn, market disruption, and operational failures.
      Our scenario types (asset shock, volatility amplification,
      feed corruption) map to these categories.

    - **Bank of England ACS**: Annual Cyclical Scenario stress
      tests measure bank resilience to hypothetical but
      plausible adverse scenarios. Our fragility classifications
      (ROBUST → CRISIS_PRONE) provide equivalent categorization.

Importance of Resilience Modeling:
    1. **Early Warning**: Stress tests reveal hidden fragilities
       BEFORE real crises expose them. A system classified as
       FRAGILE under moderate shock should trigger preemptive
       hardening measures.

    2. **Capacity Planning**: If MSI drops 40 points under a -5%
       asset shock, the protective control infrastructure (trade
       throttling, emergency halts) must be tested to handle
       that scenario.

    3. **Regulatory Confidence**: Demonstrating stress test
       capability signals institutional maturity. Regulators
       distinguish between firms that merely detect risk and
       firms that actively prepare for it.

    4. **Threshold Calibration**: Stress test results inform
       calibration of action engine thresholds. If the system
       over-reacts to mild shocks, thresholds need loosening.
       If it under-reacts to severe shocks, they need tightening.

Design Principles:
    - **Isolation**: Simulations never mutate live system state.
      All computations use sandboxed copies or fresh engines.
    - **Determinism**: Given identical inputs and scenario
      parameters, results are exactly reproducible.
    - **Composability**: Scenarios can be layered (e.g., asset
      shock + feed corruption simultaneously).
    - **Auditability**: Full input/output records for every
      simulation, enabling regulatory review.

Author: CyFin Team
Version: 1.0.0
"""

import copy
import math
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
# Fragility Classification Constants
# ══════════════════════════════════════════════════════════════════════════

FRAGILITY_ROBUST = "ROBUST"
FRAGILITY_MODERATE = "MODERATE_SENSITIVITY"
FRAGILITY_FRAGILE = "FRAGILE"
FRAGILITY_CRISIS_PRONE = "CRISIS_PRONE"

FRAGILITY_MODERATE_THRESHOLD = 10.0
FRAGILITY_FRAGILE_THRESHOLD = 25.0
FRAGILITY_CRISIS_THRESHOLD = 40.0


class StressSimulationEngine:
    """
    Simulates structured financial shock scenarios and measures
    projected MSI degradation and systemic resilience.

    This engine is the forward-looking complement to CyFin's
    real-time detection and governance capabilities. While other
    modules answer "what IS the risk?", this module answers
    "what WOULD the risk be if...?"

    Architecture::

        ┌──────────────────────────────────────────────────────────┐
        │            STRESS SIMULATION ENGINE                       │
        │                                                          │
        │  Scenarios:              Outputs:                        │
        │  ──────────              ────────                        │
        │  Single-asset shock      Baseline MSI                    │
        │  Multi-asset shock       Post-shock MSI                  │
        │  Volatility amplify      Delta MSI                       │
        │  Feed corruption         Resilience Score                │
        │  Composite scenario      Fragility Classification        │
        │                          Stress Report                   │
        │                                                          │
        │  ⚠ All simulations are sandboxed                        │
        │  ⚠ Live system state is NEVER modified                  │
        └──────────────────────────────────────────────────────────┘

    The engine maintains a baseline snapshot of current market
    conditions. When a scenario is executed, it:
    1. Clones the baseline (deep copy)
    2. Applies the specified shock to the clone
    3. Recomputes MSI, contagion, risk tier on the clone
    4. Measures the delta from baseline
    5. Returns a structured stress report

    Attributes:
        baseline_msi (float): Current MSI score (unchanged).
        baseline_trust_scores (dict): Per-asset trust scores.
        baseline_contagion_risk_score (float): Current CRS.
        baseline_feed_mismatch_rate (float): Current feed rate.
        baseline_market_anomaly_rate (float): Current anomaly rate.
        baseline_total_anomalies (int): Current anomaly count.

    Usage Example::

        >>> from resilience import StressSimulationEngine
        >>> engine = StressSimulationEngine(
        ...     baseline_msi=75.0,
        ...     baseline_trust_scores={"AAPL": 85, "MSFT": 80},
        ...     baseline_contagion_risk_score=20.0,
        ...     baseline_feed_mismatch_rate=0.01,
        ...     baseline_market_anomaly_rate=0.02,
        ...     baseline_total_anomalies=5
        ... )
        >>> report = engine.simulate_single_asset_shock("AAPL", -30.0)
        >>> print(report['post_shock_msi'])
        >>> print(report['system_fragility_level'])
    """

    def __init__(
        self,
        baseline_msi: float,
        baseline_trust_scores: Dict[str, float],
        baseline_contagion_risk_score: float = 0.0,
        baseline_feed_mismatch_rate: float = 0.0,
        baseline_market_anomaly_rate: float = 0.0,
        baseline_total_anomalies: int = 0
    ):
        """
        Initialize the Stress Simulation Engine with a snapshot
        of current market conditions.

        This snapshot forms the baseline against which all shock
        scenarios are measured. The baseline should be refreshed
        periodically (e.g., every evaluation cycle) to reflect
        current market state.

        The engine does NOT hold references to live engine
        instances. Instead, it takes a static snapshot of their
        outputs. This is a deliberate design choice:
        - Eliminates risk of accidental live state mutation
        - Makes simulations reproducible
        - Allows simulations to run concurrently
        - Enables historical scenario re-play

        Args:
            baseline_msi (float): Current MSI score (0-100).

            baseline_trust_scores (dict): Per-symbol trust scores.
                Example: {"AAPL": 85.0, "MSFT": 72.0, "GOOGL": 90.0}

            baseline_contagion_risk_score (float): Current CRS (0-100).
                Default: 0.0.

            baseline_feed_mismatch_rate (float): Current feed
                mismatch rate (0-1). Default: 0.0.

            baseline_market_anomaly_rate (float): Current market
                anomaly rate (0-1). Default: 0.0.

            baseline_total_anomalies (int): Current anomaly count.
                Default: 0.

        Raises:
            ValueError: If inputs are outside valid ranges.
        """
        self._validate_baseline(
            baseline_msi, baseline_trust_scores,
            baseline_contagion_risk_score,
            baseline_feed_mismatch_rate,
            baseline_market_anomaly_rate,
            baseline_total_anomalies
        )

        self.baseline_trust_scores = dict(baseline_trust_scores)
        self.baseline_contagion_risk_score = baseline_contagion_risk_score
        self.baseline_feed_mismatch_rate = baseline_feed_mismatch_rate
        self.baseline_market_anomaly_rate = baseline_market_anomaly_rate
        self.baseline_total_anomalies = baseline_total_anomalies

        # Derived baseline
        self.baseline_avg_trust = (
            sum(baseline_trust_scores.values())
            / len(baseline_trust_scores)
            if baseline_trust_scores else 0.0
        )

        # Store the user-provided MSI for reference, but also
        # compute the internally-consistent MSI from the same
        # metrics. Delta calculations use the internal MSI to
        # ensure comparability with post-shock recomputation.
        self.provided_baseline_msi = baseline_msi
        self.baseline_msi = self._compute_msi(
            self.baseline_trust_scores,
            self.baseline_contagion_risk_score,
            self.baseline_feed_mismatch_rate,
            self.baseline_market_anomaly_rate,
            self.baseline_total_anomalies
        )

        # Simulation history
        self._simulation_history: List[Dict[str, Any]] = []
        self._simulation_count: int = 0

        logger.info(
            "StressSimulationEngine initialized | "
            "provided_msi=%.1f | computed_msi=%.1f | assets=%d | "
            "baseline_trust=%.1f | baseline_crs=%.1f",
            baseline_msi, self.baseline_msi,
            len(baseline_trust_scores),
            self.baseline_avg_trust,
            baseline_contagion_risk_score
        )

    # ──────────────────────────────────────────────────────────────────
    # Scenario 1: Single-Asset Shock
    # ──────────────────────────────────────────────────────────────────

    def simulate_single_asset_shock(
        self,
        symbol: str,
        shock_percent: float
    ) -> Dict[str, Any]:
        """
        Simulate a price shock to a single asset and measure
        systemic impact on MSI.

        A single-asset shock models scenarios such as:
        - Flash crash in one security
        - Sudden fraud revelation (e.g., Wirecard)
        - Regulatory action against one issuer
        - Exchange-specific technical failure

        The shock propagates through the trust scoring mechanism:
        a -30% price shock reduces the asset's trust score
        proportionally (capped at floor of 0), which reduces
        the average trust, which reduces MSI.

        Additionally, a sharp single-asset shock increases the
        contagion risk score as it indicates potential for
        cross-asset contagion (other correlated assets may
        follow).

        Args:
            symbol (str): Asset symbol to shock.
                Must exist in baseline_trust_scores.

            shock_percent (float): Magnitude of the shock as
                a percentage. Negative = price drop (e.g., -30.0).
                Positive = price spike (e.g., +20.0).
                Range: [-100, 100].

        Returns:
            dict: Structured stress report (see _build_report).

        Raises:
            ValueError: If symbol not found or shock out of range.
        """
        if symbol not in self.baseline_trust_scores:
            raise ValueError(
                "Symbol '%s' not found in baseline. "
                "Available: %s" % (symbol, list(self.baseline_trust_scores.keys()))
            )
        if not (-100.0 <= shock_percent <= 100.0):
            raise ValueError(
                "shock_percent must be in [-100, 100], got %s"
                % shock_percent
            )

        # Clone trust scores
        shocked_trust = dict(self.baseline_trust_scores)

        # Apply trust degradation proportional to shock
        shock_magnitude = abs(shock_percent)
        trust_impact = shock_magnitude * 0.8  # 80% of shock transfers to trust
        original_trust = shocked_trust[symbol]
        shocked_trust[symbol] = max(
            0.0, original_trust - trust_impact
        )

        # Contagion increases with magnitude of single-asset shock
        contagion_boost = shock_magnitude * 0.3
        shocked_crs = min(
            100.0,
            self.baseline_contagion_risk_score + contagion_boost
        )

        # Anomaly rate slightly increases
        shocked_anomaly_rate = min(
            1.0,
            self.baseline_market_anomaly_rate + shock_magnitude * 0.002
        )

        # Recompute MSI
        post_shock_msi = self._compute_msi(
            shocked_trust, shocked_crs,
            self.baseline_feed_mismatch_rate,
            shocked_anomaly_rate,
            self.baseline_total_anomalies + int(shock_magnitude / 5)
        )

        # Build report
        report = self._build_report(
            scenario_type="SINGLE_ASSET_SHOCK",
            post_shock_msi=post_shock_msi,
            shocked_crs=shocked_crs,
            shocked_feed=self.baseline_feed_mismatch_rate,
            shocked_avg_trust=self._avg_trust(shocked_trust),
            scenario_params={
                "symbol": symbol,
                "shock_percent": shock_percent,
                "original_trust": original_trust,
                "post_shock_trust": shocked_trust[symbol],
                "trust_impact": trust_impact
            },
            shocked_trust_scores=shocked_trust
        )

        return report

    # ──────────────────────────────────────────────────────────────────
    # Scenario 2: Multi-Asset Synchronized Shock
    # ──────────────────────────────────────────────────────────────────

    def simulate_multi_asset_shock(
        self,
        symbols: List[str],
        shock_percent: float
    ) -> Dict[str, Any]:
        """
        Simulate a synchronized shock across multiple assets.

        Multi-asset shocks model systemic scenarios:
        - Sector-wide selloff (e.g., all tech stocks drop)
        - Market-wide panic (e.g., flash crash 2010)
        - Correlated liquidation event
        - Geopolitical shock affecting multiple markets

        Synchronized shocks are particularly dangerous because
        they trigger contagion amplification: when multiple assets
        move together, correlation spikes, which elevates CRS,
        which further degrades MSI—a positive feedback loop.

        The contagion amplifier scales with the number of affected
        assets relative to the total monitored universe.

        Args:
            symbols (list): Asset symbols to shock.
            shock_percent (float): Magnitude (-100 to 100).

        Returns:
            dict: Structured stress report.

        Raises:
            ValueError: If any symbol not found or list empty.
        """
        if not symbols:
            raise ValueError("symbols list cannot be empty")

        for s in symbols:
            if s not in self.baseline_trust_scores:
                raise ValueError(
                    "Symbol '%s' not found in baseline" % s
                )

        if not (-100.0 <= shock_percent <= 100.0):
            raise ValueError(
                "shock_percent must be in [-100, 100], got %s"
                % shock_percent
            )

        # Clone trust scores
        shocked_trust = dict(self.baseline_trust_scores)

        shock_magnitude = abs(shock_percent)
        trust_impact = shock_magnitude * 0.8

        for symbol in symbols:
            original = shocked_trust[symbol]
            shocked_trust[symbol] = max(0.0, original - trust_impact)

        # Contagion amplification: scales with breadth of shock
        total_assets = len(self.baseline_trust_scores)
        affected_ratio = len(symbols) / total_assets if total_assets > 0 else 0
        contagion_boost = (
            shock_magnitude * 0.3
            + shock_magnitude * affected_ratio * 0.5
        )
        shocked_crs = min(
            100.0,
            self.baseline_contagion_risk_score + contagion_boost
        )

        # Anomaly rate increases more with multi-asset shock
        shocked_anomaly_rate = min(
            1.0,
            self.baseline_market_anomaly_rate
            + shock_magnitude * 0.003 * len(symbols)
        )

        # Recompute
        post_shock_msi = self._compute_msi(
            shocked_trust, shocked_crs,
            self.baseline_feed_mismatch_rate,
            shocked_anomaly_rate,
            self.baseline_total_anomalies + int(shock_magnitude / 3)
        )

        report = self._build_report(
            scenario_type="MULTI_ASSET_SHOCK",
            post_shock_msi=post_shock_msi,
            shocked_crs=shocked_crs,
            shocked_feed=self.baseline_feed_mismatch_rate,
            shocked_avg_trust=self._avg_trust(shocked_trust),
            scenario_params={
                "symbols": list(symbols),
                "shock_percent": shock_percent,
                "affected_assets": len(symbols),
                "total_assets": total_assets,
                "affected_ratio": round(affected_ratio, 4),
                "contagion_amplifier": round(contagion_boost, 2)
            },
            shocked_trust_scores=shocked_trust
        )

        return report

    # ──────────────────────────────────────────────────────────────────
    # Scenario 3: Volatility Amplification
    # ──────────────────────────────────────────────────────────────────

    def simulate_volatility_amplification(
        self,
        factor: float
    ) -> Dict[str, Any]:
        """
        Simulate a market-wide volatility amplification event.

        Volatility amplification models scenarios where market
        uncertainty spikes without a specific directional move:
        - VIX spike / volatility regime change
        - Central bank surprise announcement
        - Major geopolitical uncertainty
        - Liquidity dry-up

        Unlike price shocks, volatility amplification doesn't
        directly reduce trust scores. Instead, it:
        - Dramatically increases the Contagion Risk Score
          (correlation and vol sync both spike during high-vol)
        - Moderately increases the anomaly rate (more data
          points breach statistical thresholds)
        - Slightly reduces average trust (wider spreads signal
          data uncertainty)

        Args:
            factor (float): Volatility amplification multiplier.
                Must be >= 1.0.
                1.0 = no change (baseline)
                2.0 = double volatility
                5.0 = extreme (comparable to March 2020)

        Returns:
            dict: Structured stress report.

        Raises:
            ValueError: If factor < 1.0.
        """
        if factor < 1.0:
            raise ValueError(
                "Volatility factor must be >= 1.0, got %s" % factor
            )

        # CRS increases strongly with volatility
        vol_impact_on_crs = (factor - 1.0) * 30.0
        shocked_crs = min(
            100.0,
            self.baseline_contagion_risk_score + vol_impact_on_crs
        )

        # Anomaly rate increases with volatility
        vol_impact_on_anomalies = (factor - 1.0) * 0.05
        shocked_anomaly_rate = min(
            1.0,
            self.baseline_market_anomaly_rate + vol_impact_on_anomalies
        )

        # Trust degrades slightly (wider spreads, more uncertainty)
        trust_degradation = (factor - 1.0) * 3.0
        shocked_trust = {
            s: max(0.0, t - trust_degradation)
            for s, t in self.baseline_trust_scores.items()
        }

        # Additional anomalies from vol expansion
        extra_anomalies = int((factor - 1.0) * 10)

        # Recompute
        post_shock_msi = self._compute_msi(
            shocked_trust, shocked_crs,
            self.baseline_feed_mismatch_rate,
            shocked_anomaly_rate,
            self.baseline_total_anomalies + extra_anomalies
        )

        report = self._build_report(
            scenario_type="VOLATILITY_AMPLIFICATION",
            post_shock_msi=post_shock_msi,
            shocked_crs=shocked_crs,
            shocked_feed=self.baseline_feed_mismatch_rate,
            shocked_avg_trust=self._avg_trust(shocked_trust),
            scenario_params={
                "volatility_factor": factor,
                "crs_impact": round(vol_impact_on_crs, 2),
                "anomaly_rate_impact": round(vol_impact_on_anomalies, 4),
                "trust_degradation_per_asset": round(trust_degradation, 2)
            },
            shocked_trust_scores=shocked_trust
        )

        return report

    # ──────────────────────────────────────────────────────────────────
    # Scenario 4: Feed Corruption Simulation
    # ──────────────────────────────────────────────────────────────────

    def simulate_feed_corruption(
        self,
        symbol: str,
        deviation_percent: float
    ) -> Dict[str, Any]:
        """
        Simulate feed data corruption for a specific asset.

        Feed corruption models scenarios where data integrity
        is compromised:
        - Exchange data feed malfunction
        - Market data vendor outage
        - Man-in-the-middle data attack
        - Stale price propagation
        - Cross-feed divergence

        Unlike market shocks, feed corruption affects data
        RELIABILITY rather than actual market conditions. This
        is distinct because:
        - The underlying market may be perfectly healthy
        - But our ability to OBSERVE it is compromised
        - Which makes ALL downstream analytics unreliable

        This is particularly insidious because a feed corruption
        event can make the system think there's a market crisis
        when there isn't one, or miss a real crisis because
        corrupted data masks it.

        Args:
            symbol (str): Asset whose feed is corrupted.
            deviation_percent (float): Magnitude of corruption
                as a percentage. Higher = more divergent feeds.
                Range: [0, 100].

        Returns:
            dict: Structured stress report.

        Raises:
            ValueError: If symbol not found or deviation invalid.
        """
        if symbol not in self.baseline_trust_scores:
            raise ValueError(
                "Symbol '%s' not found in baseline" % symbol
            )
        if not (0.0 <= deviation_percent <= 100.0):
            raise ValueError(
                "deviation_percent must be in [0, 100], got %s"
                % deviation_percent
            )

        # Feed mismatch rate increases with corruption
        deviation_fraction = deviation_percent / 100.0
        total_assets = len(self.baseline_trust_scores)
        feed_impact = deviation_fraction / max(total_assets, 1)
        shocked_feed = min(
            1.0,
            self.baseline_feed_mismatch_rate + feed_impact
        )

        # Trust for corrupted asset degrades significantly
        shocked_trust = dict(self.baseline_trust_scores)
        trust_impact = deviation_percent * 0.6
        original_trust = shocked_trust[symbol]
        shocked_trust[symbol] = max(
            0.0, original_trust - trust_impact
        )

        # CRS slightly increases (feed corruption can cause
        # apparent correlation changes)
        crs_impact = deviation_percent * 0.1
        shocked_crs = min(
            100.0,
            self.baseline_contagion_risk_score + crs_impact
        )

        # Anomaly rate increases from feed corruption artifacts
        shocked_anomaly_rate = min(
            1.0,
            self.baseline_market_anomaly_rate
            + deviation_percent * 0.003
        )

        # Recompute
        post_shock_msi = self._compute_msi(
            shocked_trust, shocked_crs,
            shocked_feed, shocked_anomaly_rate,
            self.baseline_total_anomalies + int(deviation_percent / 10)
        )

        report = self._build_report(
            scenario_type="FEED_CORRUPTION",
            post_shock_msi=post_shock_msi,
            shocked_crs=shocked_crs,
            shocked_feed=shocked_feed,
            shocked_avg_trust=self._avg_trust(shocked_trust),
            scenario_params={
                "symbol": symbol,
                "deviation_percent": deviation_percent,
                "original_trust": original_trust,
                "post_corruption_trust": shocked_trust[symbol],
                "feed_mismatch_impact": round(feed_impact, 6),
                "post_feed_mismatch_rate": round(shocked_feed, 6)
            },
            shocked_trust_scores=shocked_trust
        )

        return report

    # ──────────────────────────────────────────────────────────────────
    # Scenario 5: Composite Scenario
    # ──────────────────────────────────────────────────────────────────

    def simulate_composite_scenario(
        self,
        asset_shocks: Optional[Dict[str, float]] = None,
        volatility_factor: float = 1.0,
        feed_corruption: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Simulate a composite scenario combining multiple shock types.

        Composite scenarios model the realistic condition where
        multiple adverse events occur simultaneously:
        - Asset price crash + volatility spike (March 2020)
        - Feed corruption + market selloff (operational risk)
        - Sector shock + contagion + data integrity failure

        This is the most realistic and most severe type of stress
        test, because real crises rarely involve a single factor.

        Args:
            asset_shocks (dict, optional): Symbol → shock_percent.
                Example: {"AAPL": -30.0, "MSFT": -20.0}

            volatility_factor (float): Volatility multiplier.
                Default: 1.0 (no extra volatility).

            feed_corruption (dict, optional): Symbol → deviation_percent.
                Example: {"GOOGL": 15.0}

        Returns:
            dict: Structured stress report.
        """
        if asset_shocks is None:
            asset_shocks = {}
        if feed_corruption is None:
            feed_corruption = {}

        if volatility_factor < 1.0:
            raise ValueError(
                "volatility_factor must be >= 1.0, got %s"
                % volatility_factor
            )

        # Start from baseline
        shocked_trust = dict(self.baseline_trust_scores)
        shocked_crs = self.baseline_contagion_risk_score
        shocked_feed = self.baseline_feed_mismatch_rate
        shocked_anomaly_rate = self.baseline_market_anomaly_rate
        extra_anomalies = 0

        # Apply asset shocks
        for symbol, shock_pct in asset_shocks.items():
            if symbol not in self.baseline_trust_scores:
                raise ValueError(
                    "Symbol '%s' not found in baseline" % symbol
                )
            shock_mag = abs(shock_pct)
            trust_impact = shock_mag * 0.8
            shocked_trust[symbol] = max(
                0.0, shocked_trust[symbol] - trust_impact
            )
            shocked_crs = min(100.0, shocked_crs + shock_mag * 0.2)
            shocked_anomaly_rate = min(
                1.0, shocked_anomaly_rate + shock_mag * 0.002
            )
            extra_anomalies += int(shock_mag / 5)

        # Apply volatility amplification
        if volatility_factor > 1.0:
            vol_impact = (volatility_factor - 1.0) * 30.0
            shocked_crs = min(100.0, shocked_crs + vol_impact)
            shocked_anomaly_rate = min(
                1.0,
                shocked_anomaly_rate + (volatility_factor - 1.0) * 0.05
            )
            trust_deg = (volatility_factor - 1.0) * 3.0
            shocked_trust = {
                s: max(0.0, t - trust_deg)
                for s, t in shocked_trust.items()
            }
            extra_anomalies += int((volatility_factor - 1.0) * 10)

        # Apply feed corruption
        total_assets = max(len(self.baseline_trust_scores), 1)
        for symbol, dev_pct in feed_corruption.items():
            if symbol not in self.baseline_trust_scores:
                raise ValueError(
                    "Symbol '%s' not found in baseline" % symbol
                )
            dev_frac = dev_pct / 100.0
            shocked_feed = min(
                1.0, shocked_feed + dev_frac / total_assets
            )
            trust_impact = dev_pct * 0.6
            shocked_trust[symbol] = max(
                0.0, shocked_trust[symbol] - trust_impact
            )
            shocked_crs = min(100.0, shocked_crs + dev_pct * 0.1)
            extra_anomalies += int(dev_pct / 10)

        # Recompute
        post_shock_msi = self._compute_msi(
            shocked_trust, shocked_crs, shocked_feed,
            shocked_anomaly_rate,
            self.baseline_total_anomalies + extra_anomalies
        )

        report = self._build_report(
            scenario_type="COMPOSITE_SCENARIO",
            post_shock_msi=post_shock_msi,
            shocked_crs=shocked_crs,
            shocked_feed=shocked_feed,
            shocked_avg_trust=self._avg_trust(shocked_trust),
            scenario_params={
                "asset_shocks": asset_shocks,
                "volatility_factor": volatility_factor,
                "feed_corruption": feed_corruption,
                "components_active": sum([
                    len(asset_shocks) > 0,
                    volatility_factor > 1.0,
                    len(feed_corruption) > 0
                ])
            },
            shocked_trust_scores=shocked_trust
        )

        return report

    # ──────────────────────────────────────────────────────────────────
    # Public API: History & Batch
    # ──────────────────────────────────────────────────────────────────

    def get_simulation_history(self) -> List[Dict[str, Any]]:
        """Return all simulation reports, newest first."""
        return list(reversed(self._simulation_history))

    def get_simulation_count(self) -> int:
        """Return total number of simulations run."""
        return self._simulation_count

    def run_standard_battery(self) -> List[Dict[str, Any]]:
        """
        Run a standard battery of stress tests.

        This is the equivalent of the EBA / Fed standard battery:
        a predefined set of scenarios ranging from mild to extreme.

        Returns:
            list[dict]: List of stress reports, one per scenario.
        """
        results = []
        symbols = list(self.baseline_trust_scores.keys())

        if not symbols:
            return results

        # 1. Mild single-asset shock (-10%)
        results.append(
            self.simulate_single_asset_shock(symbols[0], -10.0)
        )

        # 2. Moderate single-asset shock (-30%)
        results.append(
            self.simulate_single_asset_shock(symbols[0], -30.0)
        )

        # 3. Severe single-asset crash (-50%)
        results.append(
            self.simulate_single_asset_shock(symbols[0], -50.0)
        )

        # 4. Multi-asset mild shock (-15%)
        if len(symbols) >= 2:
            results.append(
                self.simulate_multi_asset_shock(symbols[:2], -15.0)
            )

        # 5. Market-wide shock (all assets -20%)
        results.append(
            self.simulate_multi_asset_shock(symbols, -20.0)
        )

        # 6. Mild volatility (2x)
        results.append(
            self.simulate_volatility_amplification(2.0)
        )

        # 7. Extreme volatility (5x)
        results.append(
            self.simulate_volatility_amplification(5.0)
        )

        # 8. Feed corruption (moderate)
        results.append(
            self.simulate_feed_corruption(symbols[0], 20.0)
        )

        # 9. Composite crisis
        composite_shocks = {s: -25.0 for s in symbols[:2]} if len(symbols) >= 2 else {symbols[0]: -25.0}
        results.append(
            self.simulate_composite_scenario(
                asset_shocks=composite_shocks,
                volatility_factor=3.0,
                feed_corruption={symbols[-1]: 15.0}
            )
        )

        return results

    # ──────────────────────────────────────────────────────────────────
    # Internal: MSI Recomputation
    # ──────────────────────────────────────────────────────────────────

    def _compute_msi(
        self,
        trust_scores: Dict[str, float],
        contagion_risk_score: float,
        feed_mismatch_rate: float,
        market_anomaly_rate: float,
        total_anomalies: int
    ) -> float:
        """
        Recompute MSI V2 from shocked parameters.

        Uses the exact same formula as MarketStabilityIndex to
        ensure mathematical consistency.

        Formula:
            MSI = 1.00 * avg_trust
                  - 20 * anomaly_rate
                  - 4 * log(1 + anomalies)
                  - 25 * feed_mismatch
                  - 0.30 * CRS

        Returns:
            float: Computed MSI clamped to [0, 100].
        """
        avg_trust = self._avg_trust(trust_scores)

        msi_raw = (
            1.00 * avg_trust
            - 20.0 * market_anomaly_rate
            - 4.0 * math.log(1 + max(0, total_anomalies))
            - 25.0 * feed_mismatch_rate
            - 0.30 * contagion_risk_score
        )

        return round(max(0.0, min(100.0, msi_raw)), 2)

    # ──────────────────────────────────────────────────────────────────
    # Internal: Risk Tier Classification
    # ──────────────────────────────────────────────────────────────────

    def _classify_risk_tier(self, msi: float) -> str:
        """Classify risk tier from MSI (matches SystemicActionEngine)."""
        if msi >= 80.0:
            return "NORMAL"
        elif msi >= 60.0:
            return "ELEVATED_RISK"
        elif msi >= 40.0:
            return "HIGH_VOLATILITY"
        else:
            return "SYSTEMIC_CRISIS"

    # ──────────────────────────────────────────────────────────────────
    # Internal: Fragility Classification
    # ──────────────────────────────────────────────────────────────────

    def _classify_fragility(self, delta_msi: float) -> str:
        """
        Classify system fragility from MSI delta.

        The delta measures how much MSI drops under stress.
        Larger drops indicate more fragile systems.

        Classifications:
        - ROBUST (< 10): System absorbs the shock well.
        - MODERATE_SENSITIVITY (10-25): Notable but manageable.
        - FRAGILE (25-40): System is vulnerable. Hardening needed.
        - CRISIS_PRONE (> 40): System would enter crisis.
          Immediate infrastructure strengthening required.
        """
        if delta_msi < FRAGILITY_MODERATE_THRESHOLD:
            return FRAGILITY_ROBUST
        elif delta_msi < FRAGILITY_FRAGILE_THRESHOLD:
            return FRAGILITY_MODERATE
        elif delta_msi < FRAGILITY_CRISIS_THRESHOLD:
            return FRAGILITY_FRAGILE
        else:
            return FRAGILITY_CRISIS_PRONE

    # ──────────────────────────────────────────────────────────────────
    # Internal: Report Builder
    # ──────────────────────────────────────────────────────────────────

    def _build_report(
        self,
        scenario_type: str,
        post_shock_msi: float,
        shocked_crs: float,
        shocked_feed: float,
        shocked_avg_trust: float,
        scenario_params: Dict[str, Any],
        shocked_trust_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Build structured stress test report."""
        self._simulation_count += 1

        delta_msi = self.baseline_msi - post_shock_msi
        resilience_score = max(0.0, delta_msi)
        fragility = self._classify_fragility(resilience_score)

        baseline_tier = self._classify_risk_tier(self.baseline_msi)
        post_shock_tier = self._classify_risk_tier(post_shock_msi)

        report = {
            "simulation_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scenario_type": scenario_type,
            "baseline_msi": self.baseline_msi,
            "post_shock_msi": post_shock_msi,
            "delta_msi": round(delta_msi, 2),
            "resilience_score": round(resilience_score, 2),
            "baseline_risk_tier": baseline_tier,
            "post_shock_risk_tier": post_shock_tier,
            "tier_changed": baseline_tier != post_shock_tier,
            "system_fragility_level": fragility,
            "post_shock_metrics": {
                "contagion_risk_score": round(shocked_crs, 2),
                "feed_mismatch_rate": round(shocked_feed, 6),
                "average_trust_score": round(shocked_avg_trust, 2),
                "trust_scores": {
                    s: round(t, 2)
                    for s, t in shocked_trust_scores.items()
                }
            },
            "scenario_params": scenario_params,
            "simulation_number": self._simulation_count
        }

        self._simulation_history.append(report)

        # Log
        log_msg = (
            "STRESS TEST #%d [%s] | MSI: %.1f -> %.1f "
            "(delta=%.1f) | Fragility: %s"
            % (
                self._simulation_count, scenario_type,
                self.baseline_msi, post_shock_msi,
                delta_msi, fragility
            )
        )
        if fragility in (FRAGILITY_FRAGILE, FRAGILITY_CRISIS_PRONE):
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return report

    # ──────────────────────────────────────────────────────────────────
    # Internal: Utilities
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _avg_trust(trust_scores: Dict[str, float]) -> float:
        """Compute average trust score."""
        if not trust_scores:
            return 0.0
        return sum(trust_scores.values()) / len(trust_scores)

    def _validate_baseline(
        self,
        baseline_msi: float,
        baseline_trust_scores: Dict[str, float],
        baseline_crs: float,
        baseline_feed: float,
        baseline_anomaly_rate: float,
        baseline_total_anomalies: int
    ) -> None:
        """Validate baseline inputs."""
        if not isinstance(baseline_msi, (int, float)):
            raise TypeError("baseline_msi must be numeric")
        if not (0.0 <= baseline_msi <= 100.0):
            raise ValueError(
                "baseline_msi must be in [0, 100], got %s"
                % baseline_msi
            )
        if not isinstance(baseline_trust_scores, dict):
            raise TypeError("baseline_trust_scores must be a dict")
        if not baseline_trust_scores:
            raise ValueError(
                "baseline_trust_scores must contain at least one asset"
            )
        for sym, score in baseline_trust_scores.items():
            if not isinstance(score, (int, float)):
                raise TypeError(
                    "Trust score for '%s' must be numeric" % sym
                )
        if not (0.0 <= baseline_crs <= 100.0):
            raise ValueError(
                "baseline_contagion_risk_score must be in [0, 100]"
            )
        if not (0.0 <= baseline_feed <= 1.0):
            raise ValueError(
                "baseline_feed_mismatch_rate must be in [0, 1]"
            )
        if not (0.0 <= baseline_anomaly_rate <= 1.0):
            raise ValueError(
                "baseline_market_anomaly_rate must be in [0, 1]"
            )
        if baseline_total_anomalies < 0:
            raise ValueError(
                "baseline_total_anomalies must be >= 0"
            )
