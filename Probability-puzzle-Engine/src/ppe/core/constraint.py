from __future__ import annotations
from typing import Dict
from ppe.dsl.schema import CountConstraint, ValueConstraint, SumConstraint


def _compare(x: int, op: str, k: int) -> bool:
    if op == "==": return x == k
    if op == "!=": return x != k
    if op == ">=": return x >= k
    if op == "<=": return x <= k
    if op == ">":  return x > k
    if op == "<":  return x < k
    raise ValueError(f"Unknown op: {op}")


def eval_count_constraint(assign: Dict[str, str], c: CountConstraint) -> bool:
    count = sum(1 for v in c.vars if assign[v] in set(c.values))
    return _compare(count, c.op, c.k)


def eval_value_constraint(assign: Dict[str, str], c: ValueConstraint) -> bool:
    return assign[c.var] == c.value


def eval_sum_constraint(assign: Dict[str, str], c: SumConstraint) -> bool:
    total = sum(int(assign[v]) for v in c.vars)
    return _compare(total, c.op, c.k)
