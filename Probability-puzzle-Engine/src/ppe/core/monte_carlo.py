from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ppe.core.exact import _eval_constraint
from ppe.dsl.schema import PuzzleSpec


def _sample_state(puzzle: PuzzleSpec, rng: random.Random) -> Dict[str, str]:
    """Sample one state according to each variable's weight distribution."""
    assign: Dict[str, str] = {}
    for var in puzzle.variables:
        if var.weights is not None:
            (val,) = rng.choices(var.domain, weights=var.weights, k=1)
        else:
            val = rng.choice(var.domain)
        assign[var.name] = val
    return assign


def _wilson_ci(hits: int, trials: int, confidence: float) -> Tuple[float, float]:
    """Wilson score confidence interval for a proportion."""
    if trials == 0:
        return (0.0, 1.0)
    z = _z_score(confidence)
    p_hat = hits / trials
    denom = 1 + z * z / trials
    centre = (p_hat + z * z / (2 * trials)) / denom
    margin = z * math.sqrt(p_hat * (1 - p_hat) / trials + z * z / (4 * trials * trials)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def _z_score(confidence: float) -> float:
    """Approximate z-score for common confidence levels."""
    table = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
    if confidence in table:
        return table[confidence]
    # Fallback: normal approximation via Abramowitz & Stegun 26.2.17
    p = (1 + confidence) / 2
    t = math.sqrt(-2 * math.log(1 - p))
    c = (2.515517, 0.802853, 0.010328)
    d = (1.432788, 0.189269, 0.001308)
    return t - (c[0] + c[1] * t + c[2] * t * t) / (1 + d[0] * t + d[1] * t * t + d[2] * t ** 3)


@dataclass(frozen=True)
class MonteCarloResult:
    probability: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    counts: Dict[str, int]  # trials, given_hits, query_hits


def solve_monte_carlo(
    puzzle: PuzzleSpec,
    n_samples: int = 10_000,
    confidence: float = 0.95,
    seed: Optional[int] = None,
) -> MonteCarloResult:
    """
    Estimates P(query | constraints) by rejection sampling.

    Samples states according to variable weights (uniform if none specified).
    Counts states satisfying constraints (given_hits) and those also satisfying
    the query (query_hits). Returns estimate with Wilson confidence interval.

    Note: if constraints are very restrictive, many samples are rejected;
    increase n_samples for better estimates in low-probability conditioning regions.
    """
    rng = random.Random(seed)

    trials = 0
    given_hits = 0
    query_hits = 0

    for _ in range(n_samples):
        assign = _sample_state(puzzle, rng)
        trials += 1

        ok_given = all(_eval_constraint(assign, c) for c in puzzle.constraints)
        if not ok_given:
            continue

        given_hits += 1
        if _eval_constraint(assign, puzzle.query):
            query_hits += 1

    prob = (query_hits / given_hits) if given_hits > 0 else 0.0
    ci = _wilson_ci(query_hits, given_hits, confidence)

    return MonteCarloResult(
        probability=prob,
        confidence_interval=ci,
        confidence_level=confidence,
        counts={"trials": trials, "given_hits": given_hits, "query_hits": query_hits},
    )
