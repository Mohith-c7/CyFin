"""
Trust Score Engine Module
Evaluates market data reliability and converts anomalies into trust scores.

Design:
    Trust starts at 100 and degrades when anomalies are detected.
    It slowly recovers when clean ticks are seen, modelling the
    natural return of confidence after a period of stability.

    Recovery rate: +0.5 per clean tick (takes ~40 clean ticks to
    recover from a single moderate anomaly penalty of -20).

    This prevents trust from permanently collapsing after a brief
    spike in real market data, which would crater the MSI even in
    an otherwise healthy market.
"""

from trust.trust_config import SAFE_THRESHOLD, CAUTION_THRESHOLD

# Penalty per anomaly severity tier
PENALTY_CATASTROPHIC = 60  # z > 15 (market manipulation or crash)
PENALTY_CRITICAL  = 30   # z > 8  (extreme statistical outlier)
PENALTY_SEVERE    = 20   # z > 5  (severe anomaly)
PENALTY_MODERATE  = 10   # z > 3  (moderate anomaly)

# Recovery per clean (non-anomaly) tick
# 10-point penalty takes ~20 clean ticks to recover — realistic
RECOVERY_PER_CLEAN_TICK = 0.5


class TrustScoreEngine:
    """
    Evaluates data trustworthiness and maintains a dynamic reliability score.

    Trust is a smoothed signal:
    - It drops sharply on anomalous ticks (severity-scaled penalty)
    - It recovers slowly on clean ticks (small positive increment)

    This models real-world confidence dynamics:
    - One bad data point doesn't permanently destroy trust
    - Sustained anomalies accumulate into low trust
    - Sustained clean data restores trust over time

    Score range: [0, 100]
    """

    def __init__(self):
        """Initialize trust score engine with maximum trust."""
        self.trust_score = 100.0

    def update_score(self, z_score: float) -> None:
        """
        Degrade trust score based on anomaly severity.

        Penalties (scaled down from original to allow recovery):
            z > 15: -60 pts (catastrophic spike, instantly dangerous)
            z > 8: -30 pts  (critical spike)
            z > 5: -20 pts  (severe)
            z > 3: -10 pts  (moderate)

        Args:
            z_score: Z-score magnitude from anomaly detection.
        """
        if z_score > 15:
            self.trust_score -= PENALTY_CATASTROPHIC
        elif z_score > 8:
            self.trust_score -= PENALTY_CRITICAL
        elif z_score > 5:
            self.trust_score -= PENALTY_SEVERE
        elif z_score > 3:
            self.trust_score -= PENALTY_MODERATE

        # Clamp to [0, 100]
        self.trust_score = max(0.0, min(100.0, self.trust_score))

    def recover(self) -> None:
        """
        Slowly recover trust on a clean (non-anomaly) tick.

        Recovery prevents permanent trust collapse from brief market
        volatility. The recovery rate is deliberately slow so that
        sustained anomalies still suppress trust significantly.
        """
        self.trust_score = min(100.0, self.trust_score + RECOVERY_PER_CLEAN_TICK)

    def classify(self) -> str:
        """
        Classify current trust level.

        Returns:
            str: "SAFE", "CAUTION", or "DANGEROUS"
        """
        if self.trust_score >= SAFE_THRESHOLD:
            return "SAFE"
        elif self.trust_score >= CAUTION_THRESHOLD:
            return "CAUTION"
        else:
            return "DANGEROUS"

    def process_tick(self, tick: dict) -> dict:
        """
        Process a market tick and evaluate trust.

        On anomalous ticks: degrade trust by severity-based penalty.
        On clean ticks: recover trust by a small fixed increment.

        Args:
            tick: Market data dict with 'anomaly' (bool) and 'z_score' (float).

        Returns:
            dict: Tick with 'trust_score' and 'trust_level' added.
        """
        if tick.get("anomaly", False):
            self.update_score(tick.get("z_score", 0.0))
        else:
            self.recover()

        tick["trust_score"] = round(self.trust_score, 2)
        tick["trust_level"] = self.classify()

        return tick
