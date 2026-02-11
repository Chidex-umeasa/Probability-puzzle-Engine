from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

from ppe.core.state_space import build_state_space
from ppe.core.constraint import eval_count_constraint
from ppe.dsl.schema import PuzzleSpec, CountConstraint


def _eval_constraint(assign: Dict[str, str], c) -> bool:
    if isinstance(c, CountConstraint):
        return eval_count_constraint(assign, c)
    raise ValueError(f"Unsupported constraint: {type(c)}")


@dataclass(frozen=True)
class ExactSolveResult:
    probability: float
    counts: Dict[str, int]
    given_states: Optional[List[Dict[str, str]]] = None
    hit_states: Optional[List[Dict[str, str]]] = None


def solve_exact(puzzle: PuzzleSpec, trace: bool = False, max_trace: int = 50) -> ExactSolveResult:
    """
    Computes P(query | constraints) by enumeration assuming uniform outcomes.

    If trace=True, returns up to max_trace example states for:
      - given_states: states satisfying all constraints
      - hit_states: states satisfying constraints AND query
    """
    var_domains = [(v.name, v.domain) for v in puzzle.variables]

    total = 0
    given = 0
    hit = 0

    given_states: List[Dict[str, str]] = []
    hit_states: List[Dict[str, str]] = []

    for assign in build_state_space(var_domains):
        total += 1

        ok_given = all(_eval_constraint(assign, c) for c in puzzle.constraints)
        if not ok_given:
            continue

        given += 1
        if trace and len(given_states) < max_trace:
            given_states.append(assign)

        ok_query = _eval_constraint(assign, puzzle.query)
        if ok_query:
            hit += 1
            if trace and len(hit_states) < max_trace:
                hit_states.append(assign)

    prob = (hit / given) if given else 0.0
    counts = {"total": total, "given": given, "hit": hit}

    if trace:
        return ExactSolveResult(probability=prob, counts=counts, given_states=given_states, hit_states=hit_states)

    return ExactSolveResult(probability=prob, counts=counts)
