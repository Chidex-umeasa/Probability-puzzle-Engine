from __future__ import annotations
import random
from typing import List, Optional

from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint, SumConstraint


def _dice_vars(n: int, n_sides: int) -> List[VariableSpec]:
    domain = [str(i) for i in range(1, n_sides + 1)]
    return [VariableSpec(name=f"d{i+1}", domain=domain) for i in range(n)]


def generate_dice_puzzle(
    n_dice: int = 2,
    n_sides: int = 6,
    rng_seed: Optional[int] = None,
) -> PuzzleSpec:
    """
    Generates a random dice puzzle.

    Constraint types chosen at random:
      - SumConstraint: sum of all dice op k  (e.g. sum >= 7)
      - CountConstraint: count of a specific face op k  (e.g. #sixes >= 1)

    Query types:
      - SumConstraint: sum == k
      - CountConstraint: count of a face == k
    """
    rng = random.Random(rng_seed)

    vars_ = _dice_vars(n_dice, n_sides)
    names = [v.name for v in vars_]
    min_sum = n_dice
    max_sum = n_dice * n_sides

    constraint_type = rng.choice(["sum", "count"])

    if constraint_type == "sum":
        op = rng.choice([">=", "<="])
        mid = (min_sum + max_sum) // 2
        k = rng.randint(min_sum + 1, mid) if op == ">=" else rng.randint(mid, max_sum - 1)
        constraint = SumConstraint(vars=names, op=op, k=k)
    else:
        face = str(rng.randint(1, n_sides))
        op = rng.choice([">=", "<="])
        k = rng.randint(1, n_dice - 1) if n_dice > 1 else 1
        constraint = CountConstraint(values=[face], vars=names, op=op, k=k)

    query_type = rng.choice(["sum", "count"])

    if query_type == "sum":
        k_q = rng.randint(min_sum, max_sum)
        query = SumConstraint(vars=names, op="==", k=k_q)
    else:
        face_q = str(rng.randint(1, n_sides))
        k_q = rng.randint(0, n_dice)
        query = CountConstraint(values=[face_q], vars=names, op="==", k=k_q)

    return PuzzleSpec(variables=vars_, constraints=[constraint], query=query)
