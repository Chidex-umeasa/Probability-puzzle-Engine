from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ppe.core.state_space import build_state_space
from ppe.core.constraint import eval_count_constraint, eval_value_constraint, eval_sum_constraint
from ppe.dsl.schema import PuzzleSpec, CountConstraint, ValueConstraint, SumConstraint

_MAX_STATES = 1_000_000


def _eval_constraint(assign: Dict[str, str], c) -> bool:
    if isinstance(c, CountConstraint):
        return eval_count_constraint(assign, c)
    if isinstance(c, ValueConstraint):
        return eval_value_constraint(assign, c)
    if isinstance(c, SumConstraint):
        return eval_sum_constraint(assign, c)
    raise ValueError(f"Unsupported constraint: {type(c)}")


def _state_weight(assign: Dict[str, str], puzzle: PuzzleSpec) -> float:
    """Product of per-variable outcome weights (1.0 for uniform variables)."""
    w = 1.0
    for var in puzzle.variables:
        if var.weights is not None:
            idx = var.domain.index(assign[var.name])
            w *= var.weights[idx]
    return w


@dataclass(frozen=True)
class ExactSolveResult:
    probability: float
    counts: Dict[str, int]
    weighted: bool = False
    given_states: Optional[List[Dict[str, str]]] = None
    hit_states: Optional[List[Dict[str, str]]] = None


def solve_exact(puzzle: PuzzleSpec, trace: bool = False, max_trace: int = 50) -> ExactSolveResult:
    """
    Computes P(query | constraints) by enumeration.

    When any variable has weights defined, uses weighted probability sums;
    otherwise assumes uniform outcomes (each state equally likely).

    If trace=True, returns up to max_trace example states for:
      - given_states: states satisfying all constraints
      - hit_states: states satisfying constraints AND query

    Raises ValueError if the state space exceeds _MAX_STATES.
    """
    n_states = math.prod(len(v.domain) for v in puzzle.variables)
    if n_states > _MAX_STATES:
        raise ValueError(
            f"State space has {n_states:,} states (limit: {_MAX_STATES:,}). "
            "Use the Monte Carlo solver for large puzzles."
        )

    var_domains = [(v.name, v.domain) for v in puzzle.variables]
    is_weighted = any(v.weights is not None for v in puzzle.variables)

    total = 0
    given = 0
    hit = 0
    weight_total = 0.0
    weight_given = 0.0
    weight_hit = 0.0

    given_states: List[Dict[str, str]] = []
    hit_states: List[Dict[str, str]] = []

    for assign in build_state_space(var_domains):
        total += 1
        w = _state_weight(assign, puzzle) if is_weighted else 1.0
        weight_total += w

        ok_given = all(_eval_constraint(assign, c) for c in puzzle.constraints)
        if not ok_given:
            continue

        given += 1
        weight_given += w
        if trace and len(given_states) < max_trace:
            given_states.append(assign)

        ok_query = _eval_constraint(assign, puzzle.query)
        if ok_query:
            hit += 1
            weight_hit += w
            if trace and len(hit_states) < max_trace:
                hit_states.append(assign)

    if is_weighted:
        prob = (weight_hit / weight_given) if weight_given > 0 else 0.0
    else:
        prob = (hit / given) if given else 0.0

    counts = {"total": total, "given": given, "hit": hit}

    return ExactSolveResult(
        probability=prob,
        counts=counts,
        weighted=is_weighted,
        given_states=given_states if trace else None,
        hit_states=hit_states if trace else None,
    )
