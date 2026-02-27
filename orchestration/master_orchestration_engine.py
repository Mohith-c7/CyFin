"""
Master Orchestration Engine
=============================

The unified intelligence pipeline that coordinates ALL CyFin modules
into a single, production-grade monitoring loop.

Pipeline Architecture (strict execution order):

    FOR each market tick:
        ┌───────────────────────────────────────────────┐
        │  LAYER 1: DATA ACQUISITION                     │
        │    1. Fetch price from Feed A (Yahoo)          │
        │    2. Fetch price from Feed B (simulated)      │
        ├───────────────────────────────────────────────┤
        │  LAYER 2: DATA INTEGRITY                       │
        │    3. Update FeedIntegrityEngine                │
        │    4. Get feed validation status               │
        ├───────────────────────────────────────────────┤
        │  LAYER 3: ASSET INTELLIGENCE                   │
        │    5. Run anomaly detection (Z-score)           │
        │    6. Update per-asset trust scores             │
        ├───────────────────────────────────────────────┤
        │  LAYER 4: SYSTEMIC RISK                        │
        │    7. Update ContagionEngine                    │
        │    8. Compute MSI                              │
        ├───────────────────────────────────────────────┤
        │  LAYER 5: RISK ORCHESTRATION                   │
        │    9. Evaluate SystemicActionEngine             │
        │   10. Generate incident if tier escalated       │
        ├───────────────────────────────────────────────┤
        │  LAYER 6: INTELLIGENCE                         │
        │   11. Run ExplainabilityEngine                 │
        │   12. Log complete cycle                       │
        │   13. Update dashboard state                   │
        └───────────────────────────────────────────────┘

Why Orchestration Matters:
    Without a unified loop, modules become islands. Detection
    cannot inform protection, feed integrity cannot influence
    MSI, and contagion cannot trigger governance. The
    orchestrator is the nervous system that connects every
    capability into a coherent intelligence platform.

Design Principles:
    - **Strict Order**: Feed validation → Detection → Trust →
      Contagion → MSI → Action → Governance → Explainability.
      This is non-negotiable.
    - **No Skipping**: Every module runs on every cycle. Silent
      results are still logged.
    - **State Isolation**: Each module owns its state. The
      orchestrator passes data between them, never shares state.
    - **Cycle Atomicity**: Each tick produces one complete
      CycleResult, enabling full audit trail.
    - **Resilience**: If a module fails, the cycle logs the
      error and continues with degraded data rather than halting.

Author: CyFin Team
Version: 1.0.0
"""

import logging
import math
import time
from collections import deque
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ─── Internal Modules ────────────────────────────────────────────────
from data_stream.data_loader import load_market_data
from data_stream.replay_engine import stream_market_data
from detection.anomaly_engine import AnomalyDetector
from trust.trust_engine import TrustScoreEngine
from feed_validation.feed_integrity_engine import FeedIntegrityEngine
from systemic.contagion_engine import ContagionEngine
from systemic.market_stability_index import MarketStabilityIndex
from systemic.systemic_action_engine import SystemicActionEngine
from governance.incident_intelligence_engine import IncidentIntelligenceEngine
from governance.explainability_engine import ExplainabilityEngine
from resilience.stress_simulation_engine import StressSimulationEngine

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [ORCHESTRATOR] %(levelname)s: %(message)s'
    ))
    logger.addHandler(handler)


# ══════════════════════════════════════════════════════════════════════
# Feed Simulation Layer
# ══════════════════════════════════════════════════════════════════════

class SimulatedSecondaryFeed:
    """
    Generates a simulated secondary feed with configurable
    deviation from the primary feed.

    In production, this would be replaced by a real secondary
    data provider (Bloomberg, Refinitiv, etc.). For development
    and demonstration, it applies controlled noise to model
    realistic cross-feed divergence.

    The deviation follows a normal distribution centered at 0
    with configurable standard deviation, modeling the natural
    micro-differences between market data vendors.
    """

    def __init__(
        self,
        base_deviation_bps: float = 2.0,
        corruption_probability: float = 0.0,
        corruption_magnitude_pct: float = 5.0
    ):
        """
        Args:
            base_deviation_bps: Normal deviation in basis points
                (1 bp = 0.01%). Default: 2 bps (~typical vendor
                difference for liquid equities).

            corruption_probability: Probability [0-1] of
                injecting a large deviation (simulates feed
                malfunction). Default: 0 (no corruption).

            corruption_magnitude_pct: Size of corruption
                deviation as percentage. Default: 5%.
        """
        self.base_deviation_bps = base_deviation_bps
        self.corruption_probability = corruption_probability
        self.corruption_magnitude_pct = corruption_magnitude_pct

    def get_price(self, primary_price: float) -> float:
        """
        Generate secondary feed price from primary.

        Returns:
            float: Secondary price with realistic deviation.
        """
        # Normal micro-deviation (basis points)
        deviation_bps = random.gauss(0, self.base_deviation_bps)
        deviation_pct = deviation_bps / 10000.0

        # Occasional large deviation (feed corruption)
        if random.random() < self.corruption_probability:
            corruption = random.choice([-1, 1]) * (
                self.corruption_magnitude_pct / 100.0
            )
            deviation_pct += corruption

        return primary_price * (1.0 + deviation_pct)


# ══════════════════════════════════════════════════════════════════════
# Cycle Result
# ══════════════════════════════════════════════════════════════════════

class CycleResult:
    """
    Complete result of one orchestration cycle.

    Contains the output of every module for one market tick,
    providing a full audit trail of the system's processing.
    """

    def __init__(self):
        self.cycle_id: str = str(uuid.uuid4())
        self.timestamp: str = datetime.now(timezone.utc).isoformat()
        self.tick_number: int = 0

        # Layer 1: Data
        self.symbol: str = ""
        self.primary_price: float = 0.0
        self.secondary_price: float = 0.0

        # Layer 2: Feed Integrity
        self.feed_deviation: float = 0.0
        self.feed_mismatch_rate: float = 0.0
        self.feed_health: Dict[str, Any] = {}

        # Layer 3: Asset Intelligence
        self.is_anomaly: bool = False
        self.z_score: float = 0.0
        self.trust_score: float = 100.0
        self.trust_level: str = "SAFE"

        # Layer 4: Systemic Risk
        self.contagion_summary: Dict[str, Any] = {}
        self.contagion_risk_score: float = 0.0
        self.msi_result: Dict[str, Any] = {}
        self.msi_score: float = 100.0

        # Layer 5: Risk Orchestration
        self.action_result: Dict[str, Any] = {}
        self.risk_tier: str = "NORMAL"
        self.recommended_action: str = "CONTINUE_MONITORING"
        self.enforcement_required: bool = False
        self.incident: Optional[Dict[str, Any]] = None

        # Layer 6: Intelligence
        self.msi_explanation: Dict[str, Any] = {}
        self.severity_explanation: Optional[Dict[str, Any]] = None
        self.dominant_risk_factor: str = "NONE"

        # Meta
        self.errors: List[str] = []
        self.processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for logging/dashboard."""
        return {
            "cycle_id": self.cycle_id,
            "timestamp": self.timestamp,
            "tick_number": self.tick_number,
            "symbol": self.symbol,
            "primary_price": self.primary_price,
            "secondary_price": self.secondary_price,
            "feed_mismatch_rate": round(self.feed_mismatch_rate, 6),
            "is_anomaly": self.is_anomaly,
            "z_score": round(self.z_score, 4),
            "trust_score": round(self.trust_score, 2),
            "trust_level": self.trust_level,
            "contagion_risk_score": round(self.contagion_risk_score, 2),
            "msi_score": round(self.msi_score, 2),
            "risk_tier": self.risk_tier,
            "recommended_action": self.recommended_action,
            "enforcement_required": self.enforcement_required,
            "dominant_risk_factor": self.dominant_risk_factor,
            "has_incident": self.incident is not None,
            "errors": self.errors,
            "processing_time_ms": round(self.processing_time_ms, 2)
        }


# ══════════════════════════════════════════════════════════════════════
# Master Orchestration Engine
# ══════════════════════════════════════════════════════════════════════

class MasterOrchestrationEngine:
    """
    Unified intelligence pipeline coordinating all CyFin modules.

    This is the central nervous system of the platform. Every
    market tick flows through the complete pipeline in strict
    order, ensuring:

    - Feed validation happens BEFORE anomaly detection
    - Trust scores are updated BEFORE MSI computation
    - Contagion is assessed BEFORE systemic risk evaluation
    - Governance runs AFTER action decisions
    - Explainability is computed on EVERY cycle

    Usage::

        >>> engine = MasterOrchestrationEngine(
        ...     symbols=["AAPL", "MSFT", "GOOGL"]
        ... )
        >>> engine.run_live(period="1d", interval="1m")

    Or process a single tick manually::

        >>> result = engine.process_tick("AAPL", 178.50)
        >>> print(result.msi_score, result.risk_tier)
    """

    def __init__(
        self,
        symbols: List[str],
        feed_deviation_bps: float = 2.0,
        feed_corruption_prob: float = 0.0,
        contagion_window: int = 30,
        z_threshold: float = 3.0
    ):
        """
        Initialize all modules in the correct dependency order.

        Args:
            symbols: List of asset symbols to monitor.
            feed_deviation_bps: Normal cross-feed deviation (basis points).
            feed_corruption_prob: Probability of feed corruption injection.
            contagion_window: Rolling window for contagion engine.
            z_threshold: Z-score threshold for anomaly detection.
        """
        self.symbols = list(symbols)

        # ── Layer 2: Feed Integrity ──────────────────────────────
        self.feed_engine = FeedIntegrityEngine(
            deviation_threshold=0.01
        )
        self.secondary_feeds: Dict[str, SimulatedSecondaryFeed] = {}

        for sym in symbols:
            self.feed_engine.register_feed(sym, 'yahoo')
            self.feed_engine.register_feed(sym, 'secondary')
            self.secondary_feeds[sym] = SimulatedSecondaryFeed(
                base_deviation_bps=feed_deviation_bps,
                corruption_probability=feed_corruption_prob
            )

        # ── Layer 3: Asset Intelligence ──────────────────────────
        self.anomaly_detectors: Dict[str, AnomalyDetector] = {
            sym: AnomalyDetector() for sym in symbols
        }
        self.trust_engines: Dict[str, TrustScoreEngine] = {
            sym: TrustScoreEngine() for sym in symbols
        }

        # ── Layer 4: Systemic Risk ───────────────────────────────
        self.contagion_engine = ContagionEngine(
            window_size=contagion_window
        )
        self.msi_engine = MarketStabilityIndex()

        # ── Layer 5: Risk Orchestration ──────────────────────────
        self.action_engine = SystemicActionEngine()

        # ── Layer 6: Governance & Intelligence ───────────────────
        self.incident_engine = IncidentIntelligenceEngine()
        self.explainability_engine = ExplainabilityEngine()

        # ── Tracking ─────────────────────────────────────────────
        self._tick_count: int = 0
        self._total_anomalies: int = 0
        # Rolling anomaly window: MSI uses recent count, not all-time
        # This prevents MSI from permanently crashing to 0 as anomalies
        # accumulate over hundreds of ticks.
        self._anomaly_window_size: int = 50
        self._recent_anomalies: deque = deque(maxlen=self._anomaly_window_size)
        self._cycle_history: List[CycleResult] = []
        self._incidents: List[Dict[str, Any]] = []
        self._previous_tier: str = "NORMAL"

        logger.info(
            "MasterOrchestrationEngine initialized | "
            "symbols=%s | feeds=yahoo+secondary",
            symbols
        )

    # ══════════════════════════════════════════════════════════════
    # Core: Process One Tick Through Entire Pipeline
    # ══════════════════════════════════════════════════════════════

    def process_tick(
        self,
        symbol: str,
        primary_price: float,
        tick_timestamp: Optional[datetime] = None
    ) -> CycleResult:
        """
        Process a single market tick through the complete pipeline.

        This is the atomic unit of the orchestration engine.
        One call = one complete cycle through all 7 modules.

        Pipeline (strict order):
            1. Feed Integrity Engine (validate data sources)
            2. Anomaly Detection (statistical outlier check)
            3. Trust Scoring (asset reliability metric)
            4. Contagion Engine (cross-asset correlation)
            5. MSI Computation (composite stability index)
            6. Systemic Action Engine (risk classification)
            7. Incident Intelligence (governance, if triggered)
            8. Explainability (attribution for every cycle)

        Args:
            symbol: Asset symbol (must be in self.symbols).
            primary_price: Price from primary feed (Yahoo).
            tick_timestamp: Timestamp of the tick.

        Returns:
            CycleResult: Complete cycle output with all layers.
        """
        start_time = time.perf_counter()
        result = CycleResult()
        result.tick_number = self._tick_count + 1
        result.symbol = symbol

        ts = tick_timestamp or datetime.now(timezone.utc)

        # ── LAYER 1: DATA ACQUISITION ────────────────────────────
        result.primary_price = primary_price

        # Generate secondary feed price
        if symbol in self.secondary_feeds:
            result.secondary_price = self.secondary_feeds[
                symbol
            ].get_price(primary_price)
        else:
            result.secondary_price = primary_price

        # ── LAYER 2: FEED INTEGRITY (FIRST!) ─────────────────────
        try:
            self.feed_engine.update_price(
                symbol, 'yahoo', primary_price, ts
            )
            self.feed_engine.update_price(
                symbol, 'secondary', result.secondary_price, ts
            )

            result.feed_health = self.feed_engine.get_global_feed_health()
            result.feed_mismatch_rate = result.feed_health.get(
                'global_feed_mismatch_rate', 0.0
            )
            result.feed_deviation = abs(
                primary_price - result.secondary_price
            )
        except Exception as e:
            result.errors.append("FeedIntegrity: %s" % str(e))
            logger.error("Layer 2 (FeedIntegrity) error: %s", e)

        # ── LAYER 3: ASSET INTELLIGENCE ──────────────────────────
        try:
            # Anomaly detection
            tick_dict = {
                "symbol": symbol,
                "price": primary_price,
                "timestamp": str(ts)
            }

            if symbol in self.anomaly_detectors:
                tick_dict = self.anomaly_detectors[symbol].process_tick(
                    tick_dict
                )
            result.is_anomaly = tick_dict.get("anomaly", False)
            result.z_score = tick_dict.get("z_score", 0.0)

            if result.is_anomaly:
                self._total_anomalies += 1
                self._recent_anomalies.append(1)
            else:
                self._recent_anomalies.append(0)

            # Trust scoring
            if symbol in self.trust_engines:
                tick_dict = self.trust_engines[symbol].process_tick(
                    tick_dict
                )
            result.trust_score = tick_dict.get("trust_score", 100.0)
            result.trust_level = tick_dict.get("trust_level", "SAFE")
        except Exception as e:
            result.errors.append("AssetIntelligence: %s" % str(e))
            logger.error("Layer 3 (AssetIntelligence) error: %s", e)

        # ── LAYER 4: SYSTEMIC RISK ───────────────────────────────
        try:
            # Update contagion engine
            self.contagion_engine.update_price(symbol, primary_price)
            result.contagion_summary = (
                self.contagion_engine.get_contagion_summary()
            )
            result.contagion_risk_score = result.contagion_summary.get(
                'contagion_risk_score', 0.0
            )

            # Compute aggregate trust
            avg_trust = self._compute_average_trust()

            # Compute rolling anomaly rate (recent window, not all-time)
            # This ensures MSI reflects CURRENT market conditions,
            # not ancient history from ticks long ago.
            rolling_anomalies = sum(self._recent_anomalies)
            window_filled = len(self._recent_anomalies)
            rolling_rate = (
                rolling_anomalies / window_filled
                if window_filled > 0 else 0.0
            )

            # Compute MSI — both anomaly inputs come from same rolling
            # window so they are consistent and mean the same period.
            result.msi_result = self.msi_engine.compute_msi(
                average_trust_score=avg_trust,
                market_anomaly_rate=rolling_rate,
                total_anomalies=rolling_anomalies,
                feed_mismatch_rate=result.feed_mismatch_rate,
                contagion_risk_score=result.contagion_risk_score
            )
            result.msi_score = result.msi_result.get('msi_score', 100.0)
        except Exception as e:
            result.errors.append("SystemicRisk: %s" % str(e))
            logger.error("Layer 4 (SystemicRisk) error: %s", e)

        # ── LAYER 5: RISK ORCHESTRATION ──────────────────────────
        try:
            result.action_result = self.action_engine.evaluate_systemic_risk(
                msi=result.msi_score,
                contagion_risk_score=result.contagion_risk_score,
                feed_mismatch_rate=result.feed_mismatch_rate,
                average_trust_score=avg_trust
            )
            result.risk_tier = result.action_result.get(
                'risk_tier', 'NORMAL'
            )
            result.recommended_action = result.action_result.get(
                'recommended_action', 'CONTINUE_MONITORING'
            )
            result.enforcement_required = result.action_result.get(
                'enforcement_required', False
            )

            # Generate incident if tier changed or high severity
            tier_escalated = (
                result.risk_tier != self._previous_tier
                and result.risk_tier in (
                    "HIGH_VOLATILITY", "SYSTEMIC_CRISIS"
                )
            )

            if tier_escalated or result.enforcement_required:
                result.incident = (
                    self.incident_engine.create_systemic_incident(
                        msi=result.msi_score,
                        contagion_risk_score=result.contagion_risk_score,
                        feed_mismatch_rate=result.feed_mismatch_rate,
                        average_trust_score=avg_trust,
                        risk_tier=result.risk_tier,
                        recommended_action=result.recommended_action,
                        escalation_reasons=result.action_result.get(
                            'escalation_reasons', []
                        )
                    )
                )
                self._incidents.append(result.incident)
                logger.warning(
                    "INCIDENT GENERATED | tier=%s | msi=%.1f | "
                    "severity=%.1f",
                    result.risk_tier, result.msi_score,
                    result.incident.get('severity_score', 0)
                )

            self._previous_tier = result.risk_tier

        except Exception as e:
            result.errors.append("RiskOrchestration: %s" % str(e))
            logger.error("Layer 5 (RiskOrchestration) error: %s", e)

        # ── LAYER 6: EXPLAINABILITY ──────────────────────────────
        try:
            result.msi_explanation = (
                self.explainability_engine.explain_msi(
                    average_trust_score=avg_trust,
                    market_anomaly_rate=rolling_rate,
                    total_anomalies=rolling_anomalies,
                    feed_mismatch_rate=result.feed_mismatch_rate,
                    contagion_risk_score=result.contagion_risk_score
                )
            )
            result.dominant_risk_factor = result.msi_explanation.get(
                'dominant_risk_factor', 'NONE'
            )

            # Severity explanation if incident
            if result.incident:
                result.severity_explanation = (
                    self.explainability_engine.explain_severity(
                        msi=result.msi_score,
                        contagion_risk_score=result.contagion_risk_score,
                        feed_mismatch_rate=result.feed_mismatch_rate,
                        average_trust_score=avg_trust
                    )
                )
        except Exception as e:
            result.errors.append("Explainability: %s" % str(e))
            logger.error("Layer 6 (Explainability) error: %s", e)

        # ── FINALIZE ─────────────────────────────────────────────
        self._tick_count += 1
        elapsed = (time.perf_counter() - start_time) * 1000
        result.processing_time_ms = elapsed

        self._cycle_history.append(result)

        return result

    # ══════════════════════════════════════════════════════════════
    # Live Streaming: Unified Monitoring Loop
    # ══════════════════════════════════════════════════════════════

    def run_live(
        self,
        period: str = "1d",
        interval: str = "1m",
        delay: float = 0.5,
        max_ticks: int = 100,
        callback=None
    ) -> List[CycleResult]:
        """
        Run the complete unified monitoring loop on live market
        data from Yahoo Finance.

        This is the production entry point. It:
        1. Loads market data for all configured symbols
        2. Streams each tick through the complete pipeline
        3. Logs every cycle
        4. Returns complete results

        Args:
            period: Historical window (e.g., "1d", "5d").
            interval: Data resolution (e.g., "1m", "5m").
            delay: Seconds between ticks.
            max_ticks: Maximum ticks per symbol.
            callback: Optional function called with each
                CycleResult for real-time processing
                (e.g., dashboard updates).

        Returns:
            list[CycleResult]: All cycle results.
        """
        logger.info(
            "Starting live monitoring | symbols=%s | "
            "period=%s | interval=%s",
            self.symbols, period, interval
        )

        all_results: List[CycleResult] = []

        for symbol in self.symbols:
            try:
                data = load_market_data(
                    symbol=symbol, period=period, interval=interval
                )

                tick_count = 0
                for tick in stream_market_data(
                    data, symbol=symbol, delay=delay
                ):
                    tick_count += 1
                    if tick_count > max_ticks:
                        break

                    result = self.process_tick(
                        symbol=tick['symbol'],
                        primary_price=tick['price']
                    )

                    all_results.append(result)

                    if callback:
                        callback(result)

            except Exception as e:
                logger.error(
                    "Error streaming %s: %s", symbol, e
                )

        logger.info(
            "Live monitoring complete | total_ticks=%d | "
            "total_anomalies=%d | incidents=%d",
            self._tick_count, self._total_anomalies,
            len(self._incidents)
        )

        return all_results

    # ══════════════════════════════════════════════════════════════
    # Public API: System State
    # ══════════════════════════════════════════════════════════════

    def get_system_state(self) -> Dict[str, Any]:
        """
        Get the current state of the entire system.

        Returns:
            dict: Complete system state snapshot.
        """
        avg_trust = self._compute_average_trust()
        asset_trusts = {
            sym: eng.trust_score
            for sym, eng in self.trust_engines.items()
        }

        # Rolling metrics — reflects only the recent window, not all-time
        rolling_anomalies = sum(self._recent_anomalies)
        window_filled = len(self._recent_anomalies)
        rolling_rate = (
            rolling_anomalies / window_filled if window_filled > 0 else 0.0
        )

        return {
            "tick_count": self._tick_count,
            "total_anomalies": self._total_anomalies,
            "anomaly_rate": rolling_rate,          # rolling, not all-time
            "rolling_anomalies": rolling_anomalies,  # for MSI log penalty
            "average_trust_score": round(avg_trust, 2),
            "asset_trust_scores": asset_trusts,
            "feed_mismatch_rate": (
                self.feed_engine.get_global_feed_health()
                .get('global_feed_mismatch_rate', 0.0)
            ),
            "contagion_risk_score": (
                self.contagion_engine.get_contagion_summary()
                .get('contagion_risk_score', 0.0)
            ),
            "current_risk_tier": self._previous_tier,
            "total_incidents": len(self._incidents),
            "symbols_monitored": list(self.symbols)
        }

    def get_latest_cycle(self) -> Optional[CycleResult]:
        """Get the most recent cycle result."""
        if self._cycle_history:
            return self._cycle_history[-1]
        return None

    def get_cycle_history(
        self,
        last_n: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent cycle history as dicts."""
        return [
            c.to_dict() for c in self._cycle_history[-last_n:]
        ]

    def get_incidents(self) -> List[Dict[str, Any]]:
        """Get all generated incidents."""
        return list(self._incidents)

    def get_asset_rankings(self) -> List[Dict[str, Any]]:
        """Get asset systemic impact rankings."""
        asset_trusts = {
            sym: eng.trust_score
            for sym, eng in self.trust_engines.items()
        }
        return self.explainability_engine.rank_asset_systemic_impact(
            asset_trusts
        )

    def run_stress_battery(self) -> List[Dict[str, Any]]:
        """
        Run a standard stress test battery using current
        system state as baseline.

        Returns:
            list[dict]: Stress test reports.
        """
        state = self.get_system_state()
        rolling_anomalies = state.get('rolling_anomalies', 0)

        stress_engine = StressSimulationEngine(
            baseline_msi=self.msi_engine.compute_msi(
                average_trust_score=state['average_trust_score'],
                market_anomaly_rate=state['anomaly_rate'],
                total_anomalies=rolling_anomalies,
                feed_mismatch_rate=state['feed_mismatch_rate'],
                contagion_risk_score=state['contagion_risk_score']
            ).get('msi_score', 50.0),
            baseline_trust_scores=state['asset_trust_scores'],
            baseline_contagion_risk_score=state[
                'contagion_risk_score'
            ],
            baseline_feed_mismatch_rate=state['feed_mismatch_rate'],
            baseline_market_anomaly_rate=state['anomaly_rate'],
            baseline_total_anomalies=rolling_anomalies
        )

        return stress_engine.run_standard_battery()

    # ══════════════════════════════════════════════════════════════
    # Internal: Metrics Computation
    # ══════════════════════════════════════════════════════════════

    def _compute_average_trust(self) -> float:
        """Compute average trust across all monitored assets."""
        if not self.trust_engines:
            return 100.0
        total = sum(
            eng.trust_score for eng in self.trust_engines.values()
        )
        return total / len(self.trust_engines)

    def _compute_anomaly_rate(self) -> float:
        """Compute anomaly rate (anomalies / total ticks)."""
        if self._tick_count == 0:
            return 0.0
        return min(
            1.0,
            self._total_anomalies / self._tick_count
        )
