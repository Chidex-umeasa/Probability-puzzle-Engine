from __future__ import annotations
from math import gcd
from typing import Union

from ppe.core.exact import ExactSolveResult
from ppe.dsl.schema import (
    PuzzleSpec, CountConstraint, ValueConstraint, SumConstraint,
)


def _as_fraction(hit: int, given: int) -> str:
    """Return 'hit/given' reduced to lowest terms, or '0' / '1' for edge cases."""
    if given == 0:
        return "undefined (no states satisfy the constraints)"
    if hit == 0:
        return "0"
    g = gcd(hit, given)
    n, d = hit // g, given // g
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _describe_constraint(c: Union[CountConstraint, ValueConstraint, SumConstraint]) -> str:
    if isinstance(c, CountConstraint):
        vals = ", ".join(c.values)
        vars_ = ", ".join(c.vars)
        return f"count of {{{vals}}} among [{vars_}] {c.op} {c.k}"
    if isinstance(c, ValueConstraint):
        return f"{c.var} == {c.value}"
    if isinstance(c, SumConstraint):
        vars_ = " + ".join(c.vars)
        return f"sum({vars_}) {c.op} {c.k}"
    return str(c)


def explain(puzzle: PuzzleSpec, result: ExactSolveResult) -> str:
    """
    Returns a human-readable, multi-line explanation of a solve result.

    Example output:
        Variables:
          c1 ∈ {H, T}
          c2 ∈ {H, T}

        Constraints (given):
          count of {H} among [c1, c2] >= 1

        Query:
          count of {H} among [c1, c2] == 2

        State counts:
          Total states      :   4
          Satisfying given  :   3
          Satisfying query  :   1

        P(query | given) = 1/3 ≈ 0.3333
    """
    lines: list[str] = []

    # Variables
    lines.append("Variables:")
    for v in puzzle.variables:
        domain_str = ", ".join(v.domain)
        if v.weights is not None:
            weight_str = ", ".join(f"{w:.3f}" for w in v.weights)
            lines.append(f"  {v.name} ∈ {{{domain_str}}}  [weights: {weight_str}]")
        else:
            lines.append(f"  {v.name} ∈ {{{domain_str}}}")
    lines.append("")

    # Constraints
    if puzzle.constraints:
        lines.append("Constraints (given):")
        for c in puzzle.constraints:
            lines.append(f"  {_describe_constraint(c)}")
    else:
        lines.append("Constraints (given): none (unconditional)")
    lines.append("")

    # Query
    lines.append("Query:")
    lines.append(f"  {_describe_constraint(puzzle.query)}")
    lines.append("")

    # Counts
    total = result.counts["total"]
    given = result.counts["given"]
    hit = result.counts["hit"]
    lines.append("State counts:")
    lines.append(f"  Total states      : {total:>6}")
    lines.append(f"  Satisfying given  : {given:>6}")
    lines.append(f"  Satisfying query  : {hit:>6}")
    lines.append("")

    # Result
    frac = _as_fraction(hit, given)
    prob = result.probability
    if result.weighted:
        lines.append(f"P(query | given) = {prob:.6f}  [weighted]")
        lines.append("  (Weighted probability: state weights applied)")
    else:
        lines.append(f"P(query | given) = {frac} ≈ {prob:.4f}")

    return "\n".join(lines)
