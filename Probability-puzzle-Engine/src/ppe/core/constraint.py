from __future__ import annotations
from typing import Dict
from ppe.dsl.schema import CountConstraint

def _compare(x: int, op: str, k: int) -> bool:
    if op == "==": return x == k
    if op == ">=": return x >= k
    if op == "<=": return x <= k
    if op == ">":  return x > k
    if op == "<":  return x < k
    raise ValueError(f"Unknown op: {op}")

def eval_count_constraint(assign: Dict[str, str], c: CountConstraint) -> bool:
    count = 0
    values = set(c.values)
    for v in c.vars:
        if assign[v] in values:
            count += 1
    return _compare(count, c.op, c.k)
