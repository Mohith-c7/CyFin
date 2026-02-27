"""
Feed Integrity & Validation Engine
====================================

Enterprise-grade, production-ready module for validating consistency across
multiple financial data feeds per asset and computing feed-level trust metrics.

Financial Significance:
    Modern financial infrastructure relies on multiple data feeds (exchanges,
    OTC desks, dark pools, aggregators) to determine fair asset prices.
    Discrepancies between feeds can indicate:
      - Market fragmentation or illiquidity
      - Stale or delayed data from a specific source
      - Data corruption in the feed pipeline
      - Intentional price manipulation or spoofing attacks

Cybersecurity Role:
    Feed manipulation is one of the most effective and hardest-to-detect
    attack vectors in financial systems. An attacker who can alter prices
    from a single feed source can:
      - Trigger automated trading algorithms to execute at incorrect prices
      - Manipulate risk calculations to circumvent position limits
      - Distort margin calculations leading to under-collateralization
      - Inject false arbitrage signals to drain capital

    This engine acts as a **Data Integrity Firewall** by continuously
    cross-validating all registered feed sources per symbol and flagging
    deviations before they propagate into downstream systems (trust scoring,
    MSI computation, trade execution).

Why Feed Validation is Critical Infrastructure:
    1. Single-source dependency creates a single point of failure
    2. Feed latency differences create temporary price inconsistencies
    3. Exchange outages may cause stale pricing from one or more sources
    4. Regulatory frameworks (MiFID II, Reg NMS) require best-execution
       obligations that depend on accurate multi-venue pricing
    5. Systemic risk can cascade from a single corrupted feed through
       interconnected trading systems

Design Principles:
    - Pluggable: Any feed source can be registered dynamically at runtime
    - Scalable: O(n²) pairwise comparison per symbol, manageable for
      real-world feed counts (typically 2-10 feeds per symbol)
    - Persistent: All mismatch events are logged to the database for
      forensic analysis and regulatory audit trails
    - Observable: Comprehensive metrics exported at per-feed, per-symbol,
      and global levels for dashboard integration
    - Configurable: All thresholds and tuning parameters exposed via
      constructor for deployment-specific calibration
    - Extensible: Designed so that real exchange feeds (Bloomberg, Reuters,
      direct exchange connections) can be plugged in as feed sources

Integration Points:
    - Outputs `feed_mismatch_rate` consumed by MarketStabilityIndex (MSI)
    - Per-feed reliability scores complement per-asset TrustScorer output
    - Mismatch events persisted via DatabaseManager for audit compliance
    - Global feed health metrics surfaced on the Streamlit dashboard

Author: CyFin Team
Version: 1.0.0
"""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from itertools import combinations

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure at least a NullHandler to prevent "No handler found" warnings
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


class FeedIntegrityEngine:
    """
    Evaluates consistency between multiple data feeds per financial asset
    and computes feed-level trust metrics for systemic risk assessment.

    This engine maintains an in-memory registry of feed sources per symbol,
    tracks their latest prices and historical deviation metrics, and provides
    aggregated feed health indicators that feed into the Market Stability
    Index (MSI).

    Architecture Overview::

        ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
        │ Feed Source A │     │ Feed Source B │     │ Feed Source C │
        │  (Yahoo)     │     │  (Bloomberg) │     │  (Reuters)   │
        └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
               │                    │                    │
               └────────────┬───────┴────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Feed Integrity │
                    │     Engine      │
                    │                 │
                    │ • Cross-feed    │
                    │   validation    │
                    │ • Deviation     │
                    │   tracking      │
                    │ • Reliability   │
                    │   scoring       │
                    └───────┬────────┘
                            │
               ┌────────────┼────────────┐
               │            │            │
        ┌──────▼──────┐ ┌──▼────────┐ ┌─▼──────────┐
        │ Trust Scorer │ │    MSI    │ │  Database   │
        │ (per-asset)  │ │ (systemic)│ │  (audit)    │
        └─────────────┘ └───────────┘ └────────────┘

    Attributes:
        deviation_threshold (float): Maximum acceptable deviation between
            any two feeds before flagging a mismatch (default: 0.01 = 1%).
        severity_weight (float): Multiplier controlling how severely
            mismatches penalize feed reliability scores (default: 5.0).
        recovery_rate (float): Points recovered per price update cycle
            when no mismatches are detected (default: 0.5).
        min_feeds_for_validation (int): Minimum number of active feeds
            required to perform cross-feed validation (default: 2).
        db_manager: Optional DatabaseManager instance for persistent
            event logging.

    Thread Safety:
        All state mutations are protected by a threading.Lock to support
        concurrent feed updates from multiple data source threads.

    Usage Example::

        >>> from feed_validation.feed_integrity_engine import FeedIntegrityEngine
        >>> from database.db_manager import DatabaseManager
        >>>
        >>> db = DatabaseManager('feed_events.db')
        >>> engine = FeedIntegrityEngine(
        ...     deviation_threshold=0.01,
        ...     severity_weight=5.0,
        ...     recovery_rate=0.5,
        ...     db_manager=db
        ... )
        >>>
        >>> engine.register_feed('AAPL', 'yahoo_finance')
        >>> engine.register_feed('AAPL', 'bloomberg_terminal')
        >>> engine.register_feed('AAPL', 'reuters_eikon')
        >>>
        >>> from datetime import datetime
        >>> now = datetime.utcnow()
        >>> engine.update_price('AAPL', 'yahoo_finance', 178.50, now)
        >>> engine.update_price('AAPL', 'bloomberg_terminal', 178.55, now)
        >>> engine.update_price('AAPL', 'reuters_eikon', 178.48, now)
        >>>
        >>> summary = engine.get_symbol_feed_summary('AAPL')
        >>> print(f"Max Deviation: {summary['max_deviation_percent']:.4f}")
        >>> print(f"Feed Mismatch Rate: {summary['feed_mismatch_rate']:.4f}")
        >>>
        >>> health = engine.get_global_feed_health()
        >>> print(f"Global Mismatch Rate: {health['global_feed_mismatch_rate']:.4f}")
    """

    # ──────────────────────────────────────────────────────────────────────
    # Default configuration constants (overridable via constructor)
    # ──────────────────────────────────────────────────────────────────────
    DEFAULT_DEVIATION_THRESHOLD = 0.01     # 1% deviation triggers mismatch
    DEFAULT_SEVERITY_WEIGHT = 5.0          # Reliability penalty multiplier
    DEFAULT_RECOVERY_RATE = 0.5            # Reliability recovery per cycle
    DEFAULT_MIN_FEEDS = 2                  # Minimum feeds for validation
    DEFAULT_INITIAL_RELIABILITY = 100.0    # Starting reliability score
    RELIABILITY_MIN = 0.0                  # Floor for reliability score
    RELIABILITY_MAX = 100.0                # Ceiling for reliability score

    def __init__(
        self,
        deviation_threshold: float = DEFAULT_DEVIATION_THRESHOLD,
        severity_weight: float = DEFAULT_SEVERITY_WEIGHT,
        recovery_rate: float = DEFAULT_RECOVERY_RATE,
        min_feeds_for_validation: int = DEFAULT_MIN_FEEDS,
        db_manager: Optional[Any] = None
    ):
        """
        Initialize the Feed Integrity Engine with configurable thresholds.

        All parameters are tunable for deployment-specific calibration.
        For example, high-frequency trading infrastructure may use a
        tighter deviation_threshold (e.g., 0.001 = 0.1%), while
        end-of-day reconciliation systems may tolerate wider thresholds
        (e.g., 0.05 = 5%).

        Args:
            deviation_threshold (float): Maximum acceptable percentage
                deviation between any two feed prices before a mismatch
                is flagged. Expressed as a decimal fraction (0.01 = 1%).
                Must be in range (0, 1].
                Default: 0.01 (1%)

            severity_weight (float): Controls how aggressively feed
                reliability scores are penalized on mismatch. Higher
                values cause faster reliability degradation. The actual
                penalty is: severity_weight * deviation_percent * 100.
                Must be positive.
                Default: 5.0

            recovery_rate (float): Points added to a feed's reliability
                score per update cycle where no mismatches are detected.
                Controls how quickly feeds regain trust after past
                mismatches. Must be non-negative.
                Default: 0.5

            min_feeds_for_validation (int): Minimum number of feeds with
                current prices required to perform cross-feed validation.
                If fewer feeds have reported, validation is skipped.
                Must be >= 2.
                Default: 2

            db_manager: Optional DatabaseManager instance for persisting
                feed mismatch events and audit logs. If None, events are
                only logged via the Python logging module.
                Default: None

        Raises:
            ValueError: If any parameter is outside its valid range.
        """
        # ── Parameter validation ──────────────────────────────────────
        if not (0 < deviation_threshold <= 1.0):
            raise ValueError(
                f"deviation_threshold must be in (0, 1], got {deviation_threshold}"
            )
        if severity_weight <= 0:
            raise ValueError(
                f"severity_weight must be positive, got {severity_weight}"
            )
        if recovery_rate < 0:
            raise ValueError(
                f"recovery_rate must be non-negative, got {recovery_rate}"
            )
        if min_feeds_for_validation < 2:
            raise ValueError(
                f"min_feeds_for_validation must be >= 2, got {min_feeds_for_validation}"
            )

        # ── Configuration ─────────────────────────────────────────────
        self.deviation_threshold = deviation_threshold
        self.severity_weight = severity_weight
        self.recovery_rate = recovery_rate
        self.min_feeds_for_validation = min_feeds_for_validation
        self.db_manager = db_manager

        # ── Feed data structures ──────────────────────────────────────
        # Main registry: symbol -> { feed_name -> FeedState }
        self._feeds: Dict[str, Dict[str, '_FeedState']] = {}

        # Per-symbol aggregate counters
        self._symbol_stats: Dict[str, '_SymbolStats'] = {}

        # Global counters
        self._global_mismatch_count: int = 0
        self._global_update_count: int = 0

        # ── Thread safety ─────────────────────────────────────────────
        self._lock = threading.Lock()

        logger.info(
            "FeedIntegrityEngine initialized | "
            "deviation_threshold=%.4f | severity_weight=%.2f | "
            "recovery_rate=%.2f | min_feeds=%d | db_manager=%s",
            deviation_threshold, severity_weight, recovery_rate,
            min_feeds_for_validation,
            "connected" if db_manager else "disabled"
        )

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Feed Registration
    # ──────────────────────────────────────────────────────────────────────

    def register_feed(self, symbol: str, feed_name: str) -> None:
        """
        Register a new data feed source for a given symbol.

        This method is idempotent—calling it multiple times with the same
        symbol and feed_name has no additional effect.

        In production environments, feeds might be registered at system
        startup from a configuration file, or dynamically as new feed
        connections are established.

        Args:
            symbol (str): The financial instrument identifier (e.g., 'AAPL',
                'BTC-USD'). Case-sensitive.
            feed_name (str): Unique identifier for the feed source (e.g.,
                'yahoo_finance', 'bloomberg_terminal', 'exchange_direct').
                Case-sensitive.

        Raises:
            ValueError: If symbol or feed_name is empty.

        Example::

            >>> engine.register_feed('AAPL', 'yahoo_finance')
            >>> engine.register_feed('AAPL', 'bloomberg_terminal')
            >>> engine.register_feed('MSFT', 'yahoo_finance')
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be a non-empty string")
        if not feed_name or not isinstance(feed_name, str):
            raise ValueError("feed_name must be a non-empty string")

        with self._lock:
            # Initialize symbol entry if new
            if symbol not in self._feeds:
                self._feeds[symbol] = {}
                self._symbol_stats[symbol] = _SymbolStats()
                logger.info("New symbol registered: %s", symbol)

            # Register feed if new for this symbol
            if feed_name not in self._feeds[symbol]:
                self._feeds[symbol][feed_name] = _FeedState(
                    feed_name=feed_name,
                    initial_reliability=self.RELIABILITY_MAX
                )
                logger.info(
                    "Feed registered: symbol=%s feed=%s | "
                    "total_feeds_for_symbol=%d",
                    symbol, feed_name, len(self._feeds[symbol])
                )
            else:
                logger.debug(
                    "Feed already registered (idempotent): "
                    "symbol=%s feed=%s",
                    symbol, feed_name
                )

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Price Updates & Cross-Feed Validation
    # ──────────────────────────────────────────────────────────────────────

    def update_price(
        self,
        symbol: str,
        feed_name: str,
        price: float,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Submit a new price observation from a specific feed source.

        This method:
        1. Records the price and timestamp for the specified feed
        2. Triggers cross-feed validation across all feeds for that symbol
        3. Updates reliability scores based on validation results
        4. Persists mismatch events to the database if configured
        5. Returns the validation result for immediate consumption

        The cross-feed validation compares all active feed prices pairwise
        using the symmetric percentage deviation formula:

            deviation_pct = |p1 - p2| / ((p1 + p2) / 2)

        This formula is symmetric (order-independent) and handles the case
        where one price might be zero more gracefully than a simple
        percentage difference.

        Args:
            symbol (str): Financial instrument identifier.
            feed_name (str): Feed source identifier. Must have been
                previously registered via register_feed().
            price (float): The observed price. Must be positive.
            timestamp (datetime): When the price was observed. Should be
                a UTC timestamp for consistency.

        Returns:
            dict: Validation result containing:
                {
                    "symbol": str,
                    "feed_name": str,
                    "price": float,
                    "timestamp": str (ISO format),
                    "validation_performed": bool,
                    "mismatch_detected": bool,
                    "max_deviation_percent": float,
                    "deviations": list of dict (pairwise comparisons),
                    "feeds_validated": int
                }

        Raises:
            ValueError: If symbol/feed not registered, or price invalid.

        Example::

            >>> result = engine.update_price(
            ...     'AAPL', 'yahoo_finance', 178.50,
            ...     datetime.utcnow()
            ... )
            >>> if result['mismatch_detected']:
            ...     print(f"ALERT: Feed mismatch! "
            ...           f"Deviation: {result['max_deviation_percent']:.4f}")
        """
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")
        if not isinstance(timestamp, datetime):
            raise ValueError(
                f"timestamp must be a datetime instance, got {type(timestamp)}"
            )

        with self._lock:
            # Validate symbol and feed are registered
            if symbol not in self._feeds:
                raise ValueError(
                    f"Symbol '{symbol}' not registered. "
                    f"Call register_feed() first."
                )
            if feed_name not in self._feeds[symbol]:
                raise ValueError(
                    f"Feed '{feed_name}' not registered for symbol "
                    f"'{symbol}'. Call register_feed() first."
                )

            # ── Update feed state ─────────────────────────────────────
            feed_state = self._feeds[symbol][feed_name]
            feed_state.latest_price = price
            feed_state.last_updated = timestamp
            feed_state.total_updates += 1

            # Increment global update counter
            self._global_update_count += 1

            # ── Perform cross-feed validation ─────────────────────────
            validation_result = self._cross_validate_feeds(symbol, timestamp)

            logger.debug(
                "Price updated: symbol=%s feed=%s price=%.4f "
                "mismatch=%s deviation=%.6f",
                symbol, feed_name, price,
                validation_result['mismatch_detected'],
                validation_result['max_deviation_percent']
            )

            return validation_result

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Per-Symbol Feed Summary
    # ──────────────────────────────────────────────────────────────────────

    def get_symbol_feed_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Get a comprehensive feed integrity summary for a specific symbol.

        This provides a snapshot of all registered feeds for the symbol,
        their current prices, reliability scores, and aggregate deviation
        and mismatch metrics.

        Useful for:
        - Dashboard rendering of per-symbol feed health
        - Alerting systems monitoring individual assets
        - Regulatory audit reports on data quality
        - Input to per-asset trust scoring adjustments

        Args:
            symbol (str): Financial instrument identifier.

        Returns:
            dict: Feed summary with structure:
                {
                    "symbol": str,
                    "feeds": {
                        feed_name: {
                            "latest_price": float or None,
                            "reliability_score": float (0-100),
                            "last_updated": str (ISO) or None,
                            "total_updates": int,
                            "mismatch_count": int
                        }
                    },
                    "max_deviation_percent": float,
                    "mismatch_count": int,
                    "feed_mismatch_rate": float (0-1),
                    "total_updates": int,
                    "active_feeds": int,
                    "registered_feeds": int
                }

        Raises:
            ValueError: If symbol is not registered.

        Example::

            >>> summary = engine.get_symbol_feed_summary('AAPL')
            >>> for feed, info in summary['feeds'].items():
            ...     print(f"  {feed}: ${info['latest_price']:.2f} "
            ...           f"(reliability: {info['reliability_score']:.1f})")
        """
        with self._lock:
            if symbol not in self._feeds:
                raise ValueError(f"Symbol '{symbol}' not registered")

            feeds_dict = {}
            symbol_feeds = self._feeds[symbol]
            symbol_stats = self._symbol_stats[symbol]

            for fname, fstate in symbol_feeds.items():
                feeds_dict[fname] = {
                    "latest_price": fstate.latest_price,
                    "reliability_score": round(fstate.reliability_score, 2),
                    "last_updated": (
                        fstate.last_updated.isoformat()
                        if fstate.last_updated else None
                    ),
                    "total_updates": fstate.total_updates,
                    "mismatch_count": fstate.mismatch_count
                }

            # Compute current max deviation across active feeds
            max_deviation = self._compute_max_deviation(symbol)

            # Compute total updates for this symbol
            total_updates = sum(
                fs.total_updates for fs in symbol_feeds.values()
            )

            # Feed mismatch rate = mismatches / total validation cycles
            mismatch_rate = (
                symbol_stats.mismatch_count / symbol_stats.validation_cycles
                if symbol_stats.validation_cycles > 0
                else 0.0
            )

            # Count active feeds (those that have received at least one price)
            active_feeds = sum(
                1 for fs in symbol_feeds.values()
                if fs.latest_price is not None
            )

            return {
                "symbol": symbol,
                "feeds": feeds_dict,
                "max_deviation_percent": round(max_deviation, 6),
                "mismatch_count": symbol_stats.mismatch_count,
                "feed_mismatch_rate": round(mismatch_rate, 6),
                "total_updates": total_updates,
                "active_feeds": active_feeds,
                "registered_feeds": len(symbol_feeds)
            }

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Global Feed Health
    # ──────────────────────────────────────────────────────────────────────

    def get_global_feed_health(self) -> Dict[str, Any]:
        """
        Aggregate feed health metrics across all monitored symbols.

        This method provides the system-wide feed integrity overview that
        is consumed by the Market Stability Index (MSI) computation. The
        `global_feed_mismatch_rate` output maps directly to the MSI's
        `feed_mismatch_rate` input parameter.

        Returns:
            dict: Global feed health metrics:
                {
                    "total_symbols": int,
                    "total_feeds": int,
                    "total_mismatches": int,
                    "total_validation_cycles": int,
                    "total_price_updates": int,
                    "average_feed_reliability": float (0-100),
                    "global_feed_mismatch_rate": float (0-1),
                    "per_symbol_health": {
                        symbol: {
                            "mismatch_count": int,
                            "feed_mismatch_rate": float,
                            "avg_reliability": float,
                            "active_feeds": int
                        }
                    },
                    "lowest_reliability_feeds": list of dict
                        (bottom 5 feeds sorted by reliability)
                }

        Example::

            >>> health = engine.get_global_feed_health()
            >>> # Feed into MSI computation
            >>> from systemic.market_stability_index import MarketStabilityIndex
            >>> msi = MarketStabilityIndex()
            >>> result = msi.compute_msi(
            ...     average_trust_score=85.0,
            ...     market_anomaly_rate=0.02,
            ...     total_anomalies=5,
            ...     feed_mismatch_rate=health['global_feed_mismatch_rate']
            ... )
        """
        with self._lock:
            total_symbols = len(self._feeds)
            total_feeds = sum(
                len(feeds) for feeds in self._feeds.values()
            )

            # Aggregate mismatches and validation cycles across all symbols
            total_mismatches = sum(
                stats.mismatch_count
                for stats in self._symbol_stats.values()
            )
            total_validation_cycles = sum(
                stats.validation_cycles
                for stats in self._symbol_stats.values()
            )

            # Collect all reliability scores
            all_reliability_scores: List[float] = []
            all_feeds_info: List[Dict[str, Any]] = []
            per_symbol_health: Dict[str, Dict[str, Any]] = {}

            for symbol, feeds in self._feeds.items():
                symbol_reliabilities = []
                active = 0
                for fname, fstate in feeds.items():
                    all_reliability_scores.append(fstate.reliability_score)
                    symbol_reliabilities.append(fstate.reliability_score)
                    all_feeds_info.append({
                        "symbol": symbol,
                        "feed_name": fname,
                        "reliability_score": round(
                            fstate.reliability_score, 2
                        ),
                        "mismatch_count": fstate.mismatch_count,
                        "total_updates": fstate.total_updates
                    })
                    if fstate.latest_price is not None:
                        active += 1

                stats = self._symbol_stats[symbol]
                sym_mismatch_rate = (
                    stats.mismatch_count / stats.validation_cycles
                    if stats.validation_cycles > 0
                    else 0.0
                )
                per_symbol_health[symbol] = {
                    "mismatch_count": stats.mismatch_count,
                    "feed_mismatch_rate": round(sym_mismatch_rate, 6),
                    "avg_reliability": round(
                        sum(symbol_reliabilities) / len(symbol_reliabilities)
                        if symbol_reliabilities else 100.0,
                        2
                    ),
                    "active_feeds": active
                }

            # Global averages
            avg_reliability = (
                sum(all_reliability_scores) / len(all_reliability_scores)
                if all_reliability_scores else 100.0
            )
            global_mismatch_rate = (
                total_mismatches / total_validation_cycles
                if total_validation_cycles > 0
                else 0.0
            )

            # Bottom 5 feeds by reliability (early warning)
            lowest_feeds = sorted(
                all_feeds_info,
                key=lambda x: x['reliability_score']
            )[:5]

            return {
                "total_symbols": total_symbols,
                "total_feeds": total_feeds,
                "total_mismatches": total_mismatches,
                "total_validation_cycles": total_validation_cycles,
                "total_price_updates": self._global_update_count,
                "average_feed_reliability": round(avg_reliability, 2),
                "global_feed_mismatch_rate": round(global_mismatch_rate, 6),
                "per_symbol_health": per_symbol_health,
                "lowest_reliability_feeds": lowest_feeds
            }

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Feed Deregistration
    # ──────────────────────────────────────────────────────────────────────

    def deregister_feed(self, symbol: str, feed_name: str) -> bool:
        """
        Remove a feed source from the engine.

        Used when a feed source is decommissioned, becomes permanently
        unavailable, or is replaced by a new provider.

        Args:
            symbol (str): Financial instrument identifier.
            feed_name (str): Feed source identifier to remove.

        Returns:
            bool: True if the feed was found and removed, False otherwise.
        """
        with self._lock:
            if (symbol in self._feeds and
                    feed_name in self._feeds[symbol]):
                del self._feeds[symbol][feed_name]
                logger.info(
                    "Feed deregistered: symbol=%s feed=%s",
                    symbol, feed_name
                )
                # Clean up symbol if no feeds remain
                if not self._feeds[symbol]:
                    del self._feeds[symbol]
                    del self._symbol_stats[symbol]
                    logger.info(
                        "Symbol removed (no remaining feeds): %s", symbol
                    )
                return True
            return False

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Symbol Listing & Status
    # ──────────────────────────────────────────────────────────────────────

    def get_registered_symbols(self) -> List[str]:
        """
        Return a list of all registered symbols.

        Returns:
            list[str]: Symbol identifiers currently tracked.
        """
        with self._lock:
            return list(self._feeds.keys())

    def get_registered_feeds(self, symbol: str) -> List[str]:
        """
        Return a list of all registered feed names for a symbol.

        Args:
            symbol (str): Financial instrument identifier.

        Returns:
            list[str]: Feed source names registered for this symbol.

        Raises:
            ValueError: If symbol is not registered.
        """
        with self._lock:
            if symbol not in self._feeds:
                raise ValueError(f"Symbol '{symbol}' not registered")
            return list(self._feeds[symbol].keys())

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Reset / Clear
    # ──────────────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """
        Clear all engine state (feeds, stats, counters).

        Used for testing or when restarting monitoring from a clean state.
        Does not affect database records already persisted.
        """
        with self._lock:
            self._feeds.clear()
            self._symbol_stats.clear()
            self._global_mismatch_count = 0
            self._global_update_count = 0
            logger.info("FeedIntegrityEngine state reset")

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Cross-Feed Validation
    # ──────────────────────────────────────────────────────────────────────

    def _cross_validate_feeds(
        self,
        symbol: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Perform pairwise cross-feed deviation analysis for a symbol.

        Compares all feeds that have a current price, flags mismatches
        when deviation exceeds the configured threshold, and updates
        reliability scores accordingly.

        The deviation formula uses the symmetric percentage deviation:

            deviation_pct = |p1 - p2| / ((p1 + p2) / 2)

        This is preferred over simple percentage difference because:
        1. It is symmetric: deviation(A,B) == deviation(B,A)
        2. It averages both prices to avoid base-reference bias
        3. It handles cases where one feed might be significantly
           higher or lower more fairly

        Args:
            symbol: Symbol to validate.
            timestamp: Timestamp of the triggering price update.

        Returns:
            dict: Validation result (see update_price return type).
        """
        feeds = self._feeds[symbol]
        symbol_stats = self._symbol_stats[symbol]

        # Collect feeds with valid (non-None) prices
        active_feeds: List[Tuple[str, float]] = [
            (fname, fstate.latest_price)
            for fname, fstate in feeds.items()
            if fstate.latest_price is not None
        ]

        result = {
            "symbol": symbol,
            "validation_performed": False,
            "mismatch_detected": False,
            "max_deviation_percent": 0.0,
            "deviations": [],
            "feeds_validated": len(active_feeds)
        }

        # Need at least min_feeds_for_validation to compare
        if len(active_feeds) < self.min_feeds_for_validation:
            logger.debug(
                "Validation skipped for %s: only %d active feeds "
                "(minimum %d required)",
                symbol, len(active_feeds), self.min_feeds_for_validation
            )
            return result

        # ── Pairwise comparison ───────────────────────────────────────
        result["validation_performed"] = True
        symbol_stats.validation_cycles += 1
        max_deviation = 0.0
        mismatch_this_cycle = False
        deviations_list: List[Dict[str, Any]] = []

        for (name_a, price_a), (name_b, price_b) in combinations(
            active_feeds, 2
        ):
            # Symmetric percentage deviation
            avg_price = (price_a + price_b) / 2.0
            if avg_price == 0:
                # Guard against division by zero (both prices zero)
                deviation_pct = 0.0
            else:
                deviation_pct = abs(price_a - price_b) / avg_price

            deviation_record = {
                "feed_a": name_a,
                "price_a": price_a,
                "feed_b": name_b,
                "price_b": price_b,
                "deviation_percent": round(deviation_pct, 8),
                "exceeds_threshold": deviation_pct > self.deviation_threshold
            }
            deviations_list.append(deviation_record)

            if deviation_pct > max_deviation:
                max_deviation = deviation_pct

            # ── Mismatch handling ─────────────────────────────────────
            if deviation_pct > self.deviation_threshold:
                mismatch_this_cycle = True

                # Penalize both feeds involved in the mismatch
                penalty = (
                    self.severity_weight * deviation_pct * 100
                )
                feeds[name_a].reliability_score = max(
                    self.RELIABILITY_MIN,
                    feeds[name_a].reliability_score - penalty
                )
                feeds[name_b].reliability_score = max(
                    self.RELIABILITY_MIN,
                    feeds[name_b].reliability_score - penalty
                )
                feeds[name_a].mismatch_count += 1
                feeds[name_b].mismatch_count += 1

                logger.warning(
                    "FEED MISMATCH DETECTED | symbol=%s | "
                    "%s=%.4f vs %s=%.4f | deviation=%.6f (%.4f%%) | "
                    "threshold=%.4f%% | "
                    "penalty=%.2f applied to both feeds",
                    symbol, name_a, price_a, name_b, price_b,
                    deviation_pct, deviation_pct * 100,
                    self.deviation_threshold * 100,
                    penalty
                )

                # Persist to database if available
                self._persist_mismatch_event(
                    symbol=symbol,
                    feed_a=name_a,
                    price_a=price_a,
                    feed_b=name_b,
                    price_b=price_b,
                    deviation_pct=deviation_pct,
                    timestamp=timestamp
                )

        # ── Update mismatch counters ──────────────────────────────────
        if mismatch_this_cycle:
            symbol_stats.mismatch_count += 1
            self._global_mismatch_count += 1
        else:
            # No mismatch: recover reliability for all active feeds
            for fname, _ in active_feeds:
                feeds[fname].reliability_score = min(
                    self.RELIABILITY_MAX,
                    feeds[fname].reliability_score + self.recovery_rate
                )

        # Track historical max deviation
        symbol_stats.deviation_history.append(max_deviation)
        # Keep history bounded (last 1000 samples)
        if len(symbol_stats.deviation_history) > 1000:
            symbol_stats.deviation_history = (
                symbol_stats.deviation_history[-1000:]
            )

        result["mismatch_detected"] = mismatch_this_cycle
        result["max_deviation_percent"] = round(max_deviation, 8)
        result["deviations"] = deviations_list

        return result

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Deviation Computation
    # ──────────────────────────────────────────────────────────────────────

    def _compute_max_deviation(self, symbol: str) -> float:
        """
        Compute the current maximum pairwise deviation for a symbol.

        Examines the latest prices from all active feeds and returns
        the largest symmetric percentage deviation found.

        Args:
            symbol: Symbol to analyze.

        Returns:
            float: Maximum deviation as a decimal fraction.
        """
        feeds = self._feeds.get(symbol, {})
        active_prices = [
            fstate.latest_price
            for fstate in feeds.values()
            if fstate.latest_price is not None
        ]

        if len(active_prices) < 2:
            return 0.0

        max_dev = 0.0
        for p1, p2 in combinations(active_prices, 2):
            avg = (p1 + p2) / 2.0
            if avg == 0:
                continue
            dev = abs(p1 - p2) / avg
            if dev > max_dev:
                max_dev = dev

        return max_dev

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Database Persistence
    # ──────────────────────────────────────────────────────────────────────

    def _persist_mismatch_event(
        self,
        symbol: str,
        feed_a: str,
        price_a: float,
        feed_b: str,
        price_b: float,
        deviation_pct: float,
        timestamp: datetime
    ) -> None:
        """
        Persist a feed mismatch event to the database for audit.

        Uses the DatabaseManager's system_events table to log mismatch
        details including both feed names, prices, and the computed
        deviation. This provides a complete forensic trail for:
        - Post-incident investigation
        - Regulatory audit compliance
        - Historical feed reliability analysis
        - Pattern recognition of systematic feed issues

        Args:
            symbol: Affected symbol.
            feed_a: First feed in the mismatch pair.
            price_a: Price from feed_a.
            feed_b: Second feed in the mismatch pair.
            price_b: Price from feed_b.
            deviation_pct: Computed deviation as decimal fraction.
            timestamp: When the mismatch was detected.
        """
        if self.db_manager is None:
            return

        try:
            event_data = {
                "symbol": symbol,
                "feed_a": feed_a,
                "price_a": price_a,
                "feed_b": feed_b,
                "price_b": price_b,
                "deviation_percent": round(deviation_pct * 100, 4),
                "threshold_percent": round(
                    self.deviation_threshold * 100, 4
                )
            }

            self.db_manager.log_system_event(
                timestamp=timestamp,
                event_type="FEED_MISMATCH",
                severity="WARNING",
                message=(
                    f"Feed mismatch for {symbol}: "
                    f"{feed_a}={price_a:.4f} vs {feed_b}={price_b:.4f} "
                    f"(deviation: {deviation_pct * 100:.4f}%)"
                ),
                data=event_data
            )
            logger.debug(
                "Mismatch event persisted to database for %s", symbol
            )
        except Exception as e:
            logger.error(
                "Failed to persist mismatch event to database: %s", str(e),
                exc_info=True
            )


# ══════════════════════════════════════════════════════════════════════════
# Internal Data Structures
# ══════════════════════════════════════════════════════════════════════════

class _FeedState:
    """
    Internal state container for a single feed source.

    Tracks the latest price, reliability score, update history,
    and mismatch count for one feed-symbol combination.

    This is an internal implementation detail and should not be
    accessed directly by external code.
    """

    __slots__ = [
        'feed_name', 'latest_price', 'last_updated',
        'reliability_score', 'total_updates', 'mismatch_count'
    ]

    def __init__(
        self,
        feed_name: str,
        initial_reliability: float = 100.0
    ):
        self.feed_name: str = feed_name
        self.latest_price: Optional[float] = None
        self.last_updated: Optional[datetime] = None
        self.reliability_score: float = initial_reliability
        self.total_updates: int = 0
        self.mismatch_count: int = 0

    def __repr__(self) -> str:
        return (
            f"_FeedState(feed={self.feed_name}, "
            f"price={self.latest_price}, "
            f"reliability={self.reliability_score:.2f}, "
            f"mismatches={self.mismatch_count})"
        )


class _SymbolStats:
    """
    Internal aggregate statistics for a symbol across all its feeds.

    Tracks validation cycle counts, mismatch counts, and historical
    deviation data for trend analysis.
    """

    __slots__ = [
        'mismatch_count', 'validation_cycles', 'deviation_history'
    ]

    def __init__(self):
        self.mismatch_count: int = 0
        self.validation_cycles: int = 0
        self.deviation_history: List[float] = []

    def __repr__(self) -> str:
        return (
            f"_SymbolStats(mismatches={self.mismatch_count}, "
            f"cycles={self.validation_cycles}, "
            f"history_len={len(self.deviation_history)})"
        )
