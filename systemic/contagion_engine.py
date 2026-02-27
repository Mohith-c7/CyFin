"""
Cross-Asset Contagion & Correlation Engine
===========================================

Production-grade module for detecting systemic risk through cross-asset
correlation analysis and synchronized volatility monitoring.

Financial Contagion Theory:
    Financial contagion refers to the phenomenon where distress in one
    market or asset class spreads to others through interconnected
    channels. The 2008 Global Financial Crisis demonstrated that
    correlations between seemingly unrelated assets can spike
    dramatically during crises, creating cascading failures.

    Key mechanisms of financial contagion include:

    1. **Information Contagion**: Bad news about one asset causes
       investors to reassess correlated assets, leading to synchronized
       sell-offs even when fundamentals differ.

    2. **Liquidity Contagion**: Margin calls and forced liquidations
       in one asset force selling in others, creating artificial
       correlation spikes.

    3. **Portfolio Rebalancing**: Risk parity and mean-variance
       strategies respond to volatility changes by rebalancing,
       amplifying cross-asset movements.

    4. **Herding Behavior**: In stress periods, market participants
       converge on similar strategies (flight to quality, risk-off),
       driving all risky assets in the same direction.

Why Correlation Spikes Signal Systemic Risk:
    Under normal market conditions, assets maintain idiosyncratic
    behavior—their price movements are partially independent. A
    sudden increase in cross-asset correlation indicates that
    idiosyncratic factors are being overwhelmed by a common
    systematic factor (e.g., credit crisis, liquidity freeze).

    This "correlation convergence" is a hallmark of market stress:
    - During the 2008 crisis, equity correlations rose from ~0.3 to ~0.8
    - During COVID-19 in March 2020, cross-asset correlations spiked
      as indiscriminate selling hit all asset classes
    - Flash crashes show extreme short-lived correlation spikes

    High correlation implies reduced diversification benefits,
    meaning portfolios believed to be hedged are actually
    concentrated in a single risk factor.

How Synchronized Volatility Amplifies Instability:
    Volatility is the standard deviation of returns and measures
    uncertainty. When multiple assets exhibit elevated volatility
    simultaneously, it indicates:

    - Market-wide uncertainty (not just single-asset events)
    - Potential breakdown of market microstructure
    - Increased probability of margin breaches and forced liquidation
    - Positive feedback loops as volatility begets more volatility

    A single asset with high volatility is an anomaly.
    Multiple assets with synchronized high volatility is a systemic event.

Contagion Risk Score (CRS):
    The CRS quantifies the degree of cross-asset contagion on a
    0-100 scale by combining three orthogonal risk dimensions:

    CRS = (
        50 × normalized_avg_correlation     [Correlation component]
      + 30 × volatility_sync_ratio          [Synchronized vol component]
      + 20 × correlation_spike_ratio         [Spike detection component]
    )

    Component Rationale:
    - Correlation (50%): Strongest signal of contagion; high average
      pairwise correlation means assets are co-moving excessively.
    - Volatility Sync (30%): Concurrent high volatility across assets
      signals systemic stress, not just co-movement.
    - Correlation Spike (20%): Rapid correlation increases (delta)
      detect emerging contagion before it fully manifests.

    CRS feeds directly into the Market Stability Index (MSI) to
    provide a truly systemic risk assessment.

Integration Points:
    - CRS output consumed by MarketStabilityIndex.compute_msi()
    - Complements per-asset TrustScorer and feed-level integrity
    - Dashboard-ready summary via get_contagion_summary()

Author: CyFin Team
Version: 1.0.0
"""

import logging
import threading
from collections import deque
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(logging.NullHandler())


class ContagionEngine:
    """
    Detects systemic risk through cross-asset correlation analysis
    and synchronized volatility monitoring.

    This engine maintains rolling price histories for multiple
    financial assets, computes rolling returns, builds a rolling
    correlation matrix, and produces a Contagion Risk Score (CRS)
    that quantifies the degree of market-wide contagion.

    The CRS is designed to complement asset-level anomaly detection
    and feed-level integrity scoring, providing the missing
    systemic/macro dimension of market risk.

    Architecture Overview::

        ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
        │  AAPL   │  │  MSFT   │  │  GOOGL  │  │  AMZN   │
        │ prices  │  │ prices  │  │ prices  │  │ prices  │
        └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
             │            │            │            │
             └──────┬─────┴────────────┴─────┬──────┘
                    │                        │
            ┌───────▼────────┐      ┌────────▼───────┐
            │   Rolling      │      │   Rolling      │
            │  Correlation   │      │  Volatility    │
            │   Matrix       │      │   Per-Asset    │
            └───────┬────────┘      └────────┬───────┘
                    │                        │
            ┌───────▼────────────────────────▼───────┐
            │         Contagion Risk Score (CRS)      │
            │                                         │
            │  50 × avg_corr + 30 × vol_sync          │
            │  + 20 × corr_spike                      │
            └─────────────────┬───────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Market Stability  │
                    │      Index (MSI)   │
                    └────────────────────┘

    Thread Safety:
        All state mutations are protected by a threading.Lock.

    Scalability Notes:
        - Correlation matrix is O(n²) where n = number of symbols;
          practical for n < 100 (typical institutional portfolio size).
        - Rolling window bounds memory to O(n × window_size).
        - Returns and volatility are computed incrementally on each
          update, not recomputed from scratch.

    Attributes:
        window_size (int): Rolling window for correlation and
            volatility computations (number of price observations).
        correlation_spike_threshold (float): Average pairwise
            correlation above which a contagion alert is raised.
        volatility_sync_threshold (float): Multiplier of baseline
            volatility above which an asset is considered to have
            "elevated" volatility.

    Usage Example::

        >>> from systemic.contagion_engine import ContagionEngine
        >>> engine = ContagionEngine(
        ...     window_size=30,
        ...     correlation_spike_threshold=0.8,
        ...     volatility_sync_threshold=2.0
        ... )
        >>>
        >>> # Register symbols and feed prices
        >>> for symbol in ['AAPL', 'MSFT', 'GOOGL']:
        ...     for price in price_history[symbol]:
        ...         engine.update_price(symbol, price)
        >>>
        >>> summary = engine.get_contagion_summary()
        >>> print(f"CRS: {summary['contagion_risk_score']:.2f}")
        >>> print(f"Contagion Flag: {summary['systemic_contagion_flag']}")
    """

    # ──────────────────────────────────────────────────────────────────────
    # Default configuration constants
    # ──────────────────────────────────────────────────────────────────────
    DEFAULT_WINDOW_SIZE = 30
    DEFAULT_CORRELATION_SPIKE_THRESHOLD = 0.8
    DEFAULT_VOLATILITY_SYNC_THRESHOLD = 2.0
    CRS_MIN = 0.0
    CRS_MAX = 100.0

    # CRS component weights
    WEIGHT_CORRELATION = 50.0
    WEIGHT_VOLATILITY_SYNC = 30.0
    WEIGHT_CORRELATION_SPIKE = 20.0

    # Systemic contagion flag threshold
    CONTAGION_FLAG_THRESHOLD = 60.0

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        correlation_spike_threshold: float = DEFAULT_CORRELATION_SPIKE_THRESHOLD,
        volatility_sync_threshold: float = DEFAULT_VOLATILITY_SYNC_THRESHOLD
    ):
        """
        Initialize the Cross-Asset Contagion & Correlation Engine.

        Args:
            window_size (int): Number of price observations in the
                rolling window used for correlation and volatility
                calculations. Larger windows smooth out noise but
                are slower to detect regime changes. Smaller windows
                are more responsive but noisier.
                Must be >= 5.
                Default: 30

            correlation_spike_threshold (float): The average pairwise
                Pearson correlation level above which the system flags
                a potential contagion event. In normal markets, average
                pairwise correlation is typically 0.2-0.5 for equities.
                During crises, it can rise above 0.8.
                Must be in (0, 1].
                Default: 0.8

            volatility_sync_threshold (float): Multiplier of baseline
                (rolling) volatility. If an asset's current realized
                volatility exceeds baseline × this threshold, it is
                classified as having "elevated" volatility. When ≥50%
                of assets are elevated simultaneously, a volatility
                synchronization event is flagged.
                Must be > 1.0.
                Default: 2.0

        Raises:
            ValueError: If any parameter is outside its valid range.
        """
        # ── Parameter validation ──────────────────────────────────────
        if window_size < 5:
            raise ValueError(
                f"window_size must be >= 5, got {window_size}"
            )
        if not (0 < correlation_spike_threshold <= 1.0):
            raise ValueError(
                f"correlation_spike_threshold must be in (0, 1], "
                f"got {correlation_spike_threshold}"
            )
        if volatility_sync_threshold <= 1.0:
            raise ValueError(
                f"volatility_sync_threshold must be > 1.0, "
                f"got {volatility_sync_threshold}"
            )

        # ── Configuration ─────────────────────────────────────────────
        self.window_size = window_size
        self.correlation_spike_threshold = correlation_spike_threshold
        self.volatility_sync_threshold = volatility_sync_threshold

        # ── Per-symbol data structures ────────────────────────────────
        # Price histories: symbol -> deque of floats (bounded)
        self._prices: Dict[str, deque] = {}
        # Return histories: symbol -> deque of floats (bounded)
        self._returns: Dict[str, deque] = {}

        # ── Correlation tracking ──────────────────────────────────────
        # Historical average correlations for spike detection
        self._correlation_history: deque = deque(maxlen=window_size)
        self._previous_avg_correlation: Optional[float] = None

        # ── Thread safety ─────────────────────────────────────────────
        self._lock = threading.Lock()

        logger.info(
            "ContagionEngine initialized | window=%d | "
            "corr_threshold=%.2f | vol_sync_threshold=%.2f",
            window_size, correlation_spike_threshold,
            volatility_sync_threshold
        )

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Price Updates
    # ──────────────────────────────────────────────────────────────────────

    def update_price(self, symbol: str, price: float) -> Dict[str, Any]:
        """
        Submit a new price observation for a symbol.

        The engine automatically:
        1. Registers the symbol if it is new
        2. Appends the price to the rolling window
        3. Computes the log return from the previous price
        4. Triggers cross-asset correlation and volatility analysis
           if sufficient data is available

        Using log returns rather than simple returns because:
        - Log returns are additive over time (important for rolling windows)
        - Log returns are approximately normally distributed
        - Log returns handle compounding correctly
        - Standard in quantitative finance and risk management

        Args:
            symbol (str): Financial instrument identifier (e.g., 'AAPL').
            price (float): The observed price. Must be positive.

        Returns:
            dict: Update result containing:
                {
                    "symbol": str,
                    "price": float,
                    "return": float or None,
                    "data_points": int,
                    "sufficient_data": bool
                }

        Raises:
            ValueError: If symbol is empty or price is non-positive.
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be a non-empty string")
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")

        with self._lock:
            # Register symbol on first observation
            if symbol not in self._prices:
                self._prices[symbol] = deque(maxlen=self.window_size)
                self._returns[symbol] = deque(maxlen=self.window_size)
                logger.info("New symbol registered in ContagionEngine: %s",
                            symbol)

            prices = self._prices[symbol]
            returns = self._returns[symbol]

            # Compute log return from previous price
            log_return = None
            if len(prices) > 0:
                prev_price = prices[-1]
                if prev_price > 0:
                    log_return = np.log(price / prev_price)
                    returns.append(log_return)

            prices.append(price)

            result = {
                "symbol": symbol,
                "price": price,
                "return": float(log_return) if log_return is not None else None,
                "data_points": len(prices),
                "sufficient_data": self._has_sufficient_data()
            }

            logger.debug(
                "Price update: symbol=%s price=%.4f return=%s "
                "data_points=%d",
                symbol, price,
                f"{log_return:.6f}" if log_return is not None else "N/A",
                len(prices)
            )

            return result

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Contagion Summary
    # ──────────────────────────────────────────────────────────────────────

    def get_contagion_summary(self) -> Dict[str, Any]:
        """
        Get the comprehensive contagion analysis summary.

        This is the primary output method, producing all metrics needed
        for MSI integration and dashboard rendering.

        The Contagion Risk Score (CRS) is computed as:

            CRS = (
                50 × normalized_avg_correlation
              + 30 × volatility_sync_ratio
              + 20 × correlation_spike_ratio
            )

        Where:
        - normalized_avg_correlation: Average pairwise Pearson
          correlation, clamped to [0, 1]. Values near 1.0 mean all
          assets are moving together (maximum contagion).
        - volatility_sync_ratio: Fraction of assets with elevated
          volatility (> threshold × baseline). A ratio of 1.0 means
          all assets are in high-vol regime simultaneously.
        - correlation_spike_ratio: Measures how quickly correlation
          is increasing relative to the spike threshold. Rapid
          increases signal emerging contagion.

        Returns:
            dict: Contagion summary:
                {
                    "average_correlation": float (-1 to 1),
                    "volatility_sync_ratio": float (0 to 1),
                    "correlation_spike_ratio": float (0 to 1),
                    "contagion_risk_score": float (0 to 100),
                    "systemic_contagion_flag": bool,
                    "symbols_tracked": int,
                    "data_sufficient": bool,
                    "correlation_matrix": dict (pairwise correlations),
                    "per_symbol_volatility": dict,
                    "elevated_volatility_symbols": list
                }

        Example::

            >>> summary = engine.get_contagion_summary()
            >>> # Feed CRS into MSI
            >>> msi_result = msi.compute_msi(
            ...     average_trust_score=85.0,
            ...     market_anomaly_rate=0.02,
            ...     total_anomalies=5,
            ...     feed_mismatch_rate=0.01,
            ...     contagion_risk_score=summary['contagion_risk_score']
            ... )
        """
        with self._lock:
            symbols = list(self._prices.keys())
            n_symbols = len(symbols)

            # ── Default values for insufficient data ──────────────────
            if not self._has_sufficient_data() or n_symbols < 2:
                return {
                    "average_correlation": 0.0,
                    "volatility_sync_ratio": 0.0,
                    "correlation_spike_ratio": 0.0,
                    "contagion_risk_score": 0.0,
                    "systemic_contagion_flag": False,
                    "symbols_tracked": n_symbols,
                    "data_sufficient": False,
                    "correlation_matrix": {},
                    "per_symbol_volatility": {},
                    "elevated_volatility_symbols": []
                }

            # ── Compute correlation matrix ────────────────────────────
            corr_matrix, avg_correlation = self._compute_correlation_matrix(
                symbols
            )

            # ── Compute volatility metrics ────────────────────────────
            vol_metrics = self._compute_volatility_metrics(symbols)
            vol_sync_ratio = vol_metrics["sync_ratio"]
            elevated_symbols = vol_metrics["elevated_symbols"]
            per_symbol_vol = vol_metrics["per_symbol"]

            # ── Compute correlation spike ─────────────────────────────
            corr_spike_ratio = self._compute_correlation_spike(
                avg_correlation
            )

            # ── Compute Contagion Risk Score (CRS) ────────────────────
            # Normalize avg correlation to [0, 1] range
            # Pearson correlation ranges [-1, 1]; for contagion,
            # we care about positive correlation (co-movement)
            normalized_corr = max(0.0, avg_correlation)

            crs_raw = (
                self.WEIGHT_CORRELATION * normalized_corr
                + self.WEIGHT_VOLATILITY_SYNC * vol_sync_ratio
                + self.WEIGHT_CORRELATION_SPIKE * corr_spike_ratio
            )

            crs = max(self.CRS_MIN, min(self.CRS_MAX, crs_raw))

            # ── Systemic contagion flag ───────────────────────────────
            contagion_flag = (
                crs >= self.CONTAGION_FLAG_THRESHOLD
                or (avg_correlation >= self.correlation_spike_threshold
                    and vol_sync_ratio >= 0.5)
            )

            if contagion_flag:
                logger.warning(
                    "SYSTEMIC CONTAGION DETECTED | CRS=%.2f | "
                    "avg_corr=%.4f | vol_sync=%.4f | "
                    "corr_spike=%.4f | elevated_symbols=%s",
                    crs, avg_correlation, vol_sync_ratio,
                    corr_spike_ratio, elevated_symbols
                )

            # ── Format correlation matrix for output ──────────────────
            corr_dict = {}
            for i, sym_a in enumerate(symbols):
                for j, sym_b in enumerate(symbols):
                    if i < j:
                        key = f"{sym_a}_{sym_b}"
                        corr_dict[key] = round(corr_matrix[i, j], 6)

            return {
                "average_correlation": round(avg_correlation, 6),
                "volatility_sync_ratio": round(vol_sync_ratio, 6),
                "correlation_spike_ratio": round(corr_spike_ratio, 6),
                "contagion_risk_score": round(crs, 2),
                "systemic_contagion_flag": contagion_flag,
                "symbols_tracked": n_symbols,
                "data_sufficient": True,
                "correlation_matrix": corr_dict,
                "per_symbol_volatility": per_symbol_vol,
                "elevated_volatility_symbols": elevated_symbols
            }

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Per-Symbol Metrics
    # ──────────────────────────────────────────────────────────────────────

    def get_symbol_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific symbol.

        Args:
            symbol: Financial instrument identifier.

        Returns:
            dict: Symbol-level metrics:
                {
                    "symbol": str,
                    "price_count": int,
                    "return_count": int,
                    "latest_price": float or None,
                    "rolling_volatility": float or None,
                    "baseline_volatility": float or None,
                    "is_elevated_volatility": bool,
                    "average_return": float or None
                }

        Raises:
            ValueError: If symbol is not tracked.
        """
        with self._lock:
            if symbol not in self._prices:
                raise ValueError(f"Symbol '{symbol}' not tracked")

            prices = self._prices[symbol]
            returns = self._returns[symbol]

            latest_price = prices[-1] if prices else None
            returns_arr = np.array(returns) if len(returns) >= 2 else None

            rolling_vol = None
            baseline_vol = None
            is_elevated = False
            avg_return = None

            if returns_arr is not None and len(returns_arr) >= 2:
                rolling_vol = float(np.std(returns_arr, ddof=1))
                avg_return = float(np.mean(returns_arr))

                # Baseline: use full window volatility as baseline
                half = max(2, len(returns_arr) // 2)
                baseline_arr = returns_arr[:half]
                if len(baseline_arr) >= 2:
                    baseline_vol = float(np.std(baseline_arr, ddof=1))
                    if baseline_vol > 0:
                        is_elevated = (
                            rolling_vol >
                            baseline_vol * self.volatility_sync_threshold
                        )

            return {
                "symbol": symbol,
                "price_count": len(prices),
                "return_count": len(returns),
                "latest_price": float(latest_price) if latest_price else None,
                "rolling_volatility": (
                    round(rolling_vol, 8) if rolling_vol is not None
                    else None
                ),
                "baseline_volatility": (
                    round(baseline_vol, 8) if baseline_vol is not None
                    else None
                ),
                "is_elevated_volatility": is_elevated,
                "average_return": (
                    round(avg_return, 8) if avg_return is not None
                    else None
                )
            }

    # ──────────────────────────────────────────────────────────────────────
    # Public API: Symbol Management
    # ──────────────────────────────────────────────────────────────────────

    def get_tracked_symbols(self) -> List[str]:
        """Return list of all symbols being tracked."""
        with self._lock:
            return list(self._prices.keys())

    def reset(self) -> None:
        """Clear all engine state."""
        with self._lock:
            self._prices.clear()
            self._returns.clear()
            self._correlation_history.clear()
            self._previous_avg_correlation = None
            logger.info("ContagionEngine state reset")

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Correlation Matrix Computation
    # ──────────────────────────────────────────────────────────────────────

    def _compute_correlation_matrix(
        self,
        symbols: List[str]
    ) -> Tuple[np.ndarray, float]:
        """
        Compute the rolling Pearson correlation matrix across all
        tracked symbols using their return histories.

        Pearson correlation measures linear co-movement between
        -1 (perfect inverse) and +1 (perfect co-movement). For
        contagion detection:
        - Values near 0: Independent movement (healthy diversification)
        - Values near +1: Synchronized movement (contagion risk)
        - Values near -1: Inverse movement (hedging relationship)

        The method uses the minimum common return window length across
        all symbols to ensure consistent comparison.

        Args:
            symbols: List of symbol identifiers.

        Returns:
            tuple: (correlation_matrix as numpy array, average pairwise
                    correlation as float)
        """
        n = len(symbols)

        # Find minimum common length of return series
        min_len = min(len(self._returns[s]) for s in symbols)
        if min_len < 3:
            return np.eye(n), 0.0

        # Build return matrix: each row is a symbol's return series
        return_matrix = np.zeros((n, min_len))
        for i, sym in enumerate(symbols):
            returns_list = list(self._returns[sym])
            return_matrix[i, :] = returns_list[-min_len:]

        # Compute correlation matrix
        # Handle constant series (zero variance) gracefully
        corr_matrix = np.corrcoef(return_matrix)

        # Replace NaN with 0 (happens when a series has zero variance)
        corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)

        # Compute average pairwise correlation (upper triangle only)
        if n < 2:
            avg_corr = 0.0
        else:
            upper_triangle = corr_matrix[np.triu_indices(n, k=1)]
            avg_corr = float(np.mean(upper_triangle))

        # Track correlation history for spike detection
        self._correlation_history.append(avg_corr)

        return corr_matrix, avg_corr

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Volatility Synchronization
    # ──────────────────────────────────────────────────────────────────────

    def _compute_volatility_metrics(
        self,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """
        Compute per-symbol volatility and detect synchronized
        elevated volatility across assets.

        Volatility synchronization occurs when multiple assets
        simultaneously exhibit volatility significantly above their
        historical baseline. This is distinct from correlation—assets
        can have low correlation but high synchronized volatility
        (e.g., during a broad market panic where direction is mixed
        but magnitude is extreme for all assets).

        The detection algorithm:
        1. For each symbol, compute rolling standard deviation of
           returns (realized volatility).
        2. Compute a baseline volatility from the first half of the
           rolling window.
        3. If current volatility > baseline × volatility_sync_threshold,
           the asset is flagged as "elevated."
        4. The sync ratio = (elevated count) / (total symbols).
        5. If sync ratio ≥ 0.5, a synchronization event is detected.

        Args:
            symbols: List of symbol identifiers.

        Returns:
            dict: {
                "sync_ratio": float (0 to 1),
                "elevated_symbols": list of str,
                "per_symbol": dict of {symbol: {"volatility": float,
                    "baseline": float, "ratio": float, "elevated": bool}}
            }
        """
        n_symbols = len(symbols)
        elevated_count = 0
        elevated_symbols: List[str] = []
        per_symbol: Dict[str, Dict[str, Any]] = {}

        for sym in symbols:
            returns = list(self._returns[sym])

            if len(returns) < 5:
                per_symbol[sym] = {
                    "volatility": 0.0,
                    "baseline": 0.0,
                    "ratio": 0.0,
                    "elevated": False
                }
                continue

            returns_arr = np.array(returns)

            # Current rolling volatility (full window)
            current_vol = float(np.std(returns_arr, ddof=1))

            # Baseline volatility: first half of window
            # This provides a "calm period" reference
            half = max(2, len(returns_arr) // 2)
            baseline_arr = returns_arr[:half]
            baseline_vol = float(np.std(baseline_arr, ddof=1))

            # Compute volatility ratio
            if baseline_vol > 1e-10:  # Avoid division by near-zero
                vol_ratio = current_vol / baseline_vol
            else:
                # If baseline is essentially zero, any positive vol
                # is "elevated" — use a large ratio
                vol_ratio = (
                    10.0 if current_vol > 1e-10 else 0.0
                )

            is_elevated = vol_ratio > self.volatility_sync_threshold

            if is_elevated:
                elevated_count += 1
                elevated_symbols.append(sym)

            per_symbol[sym] = {
                "volatility": round(current_vol, 8),
                "baseline": round(baseline_vol, 8),
                "ratio": round(vol_ratio, 4),
                "elevated": is_elevated
            }

        # Sync ratio: fraction of assets with elevated volatility
        sync_ratio = (
            elevated_count / n_symbols if n_symbols > 0 else 0.0
        )

        return {
            "sync_ratio": sync_ratio,
            "elevated_symbols": elevated_symbols,
            "per_symbol": per_symbol
        }

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Correlation Spike Detection
    # ──────────────────────────────────────────────────────────────────────

    def _compute_correlation_spike(
        self,
        current_avg_correlation: float
    ) -> float:
        """
        Detect rapid increases in cross-asset correlation.

        A correlation spike indicates that contagion is actively
        propagating—assets that were previously uncorrelated are
        suddenly moving together. This is often the first observable
        signal of a developing financial crisis.

        The spike ratio measures how much the current correlation
        exceeds the recent historical average, normalized by the
        spike threshold:

            If correlation is increasing:
                spike_ratio = delta_correlation / spike_threshold
            Else:
                spike_ratio = 0 (no spike when correlation is falling)

        Args:
            current_avg_correlation: The current average pairwise
                Pearson correlation.

        Returns:
            float: Correlation spike ratio, clamped to [0, 1].
        """
        if self._previous_avg_correlation is None:
            self._previous_avg_correlation = current_avg_correlation
            return 0.0

        # Compute correlation delta
        delta = current_avg_correlation - self._previous_avg_correlation

        # Update previous for next cycle
        self._previous_avg_correlation = current_avg_correlation

        if delta <= 0:
            # Correlation is stable or decreasing — no spike
            return 0.0

        # Normalize delta relative to the spike threshold
        # A delta equal to the threshold = 1.0 (maximum spike)
        spike_ratio = delta / self.correlation_spike_threshold

        return min(1.0, max(0.0, spike_ratio))

    # ──────────────────────────────────────────────────────────────────────
    # Internal: Data Sufficiency Check
    # ──────────────────────────────────────────────────────────────────────

    def _has_sufficient_data(self) -> bool:
        """
        Check if there is enough data to perform meaningful analysis.

        Requires at least 2 symbols, each with at least 5 return
        observations (i.e., 6 prices).

        Returns:
            bool: True if sufficient data is available.
        """
        if len(self._prices) < 2:
            return False

        min_returns = min(
            len(self._returns[s]) for s in self._returns
        )
        return min_returns >= 5
