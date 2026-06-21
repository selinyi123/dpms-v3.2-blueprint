from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, quantiles


@dataclass(frozen=True)
class LatencyStats:
    count: int
    mean_ms: float
    p95_ms: float
    max_ms: float
    valid: bool


class LatencyModel:
    def summarize(self, samples_ms: list[int | float]) -> LatencyStats:
        cleaned = [float(x) for x in samples_ms if x is not None and float(x) >= 0]
        if not cleaned:
            return LatencyStats(0, 0.0, 0.0, 0.0, False)
        p95 = max(cleaned) if len(cleaned) < 2 else quantiles(cleaned, n=20, method='inclusive')[18]
        return LatencyStats(
            count=len(cleaned),
            mean_ms=round(mean(cleaned), 4),
            p95_ms=round(p95, 4),
            max_ms=round(max(cleaned), 4),
            valid=True,
        )

    @staticmethod
    def should_cancel(expected_latency_ms: int, threshold_ms: int = 250) -> bool:
        return expected_latency_ms < 0 or expected_latency_ms > threshold_ms
