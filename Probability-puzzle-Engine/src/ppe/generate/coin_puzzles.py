from __future__ import annotations
import random
from typing import List, Tuple

from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint


def _coin_vars(n: int) -> List[VariableSpec]:
    return [VariableSpec(name=f"c{i+1}", domain=["H", "T"]) for i in range(n)]


def generate_coin_puzzle(
    n_coins: int = 3,
    rng_seed: int | None = None
) -> PuzzleSpec:
    """
    Generates a random coin puzzle:
      - constraint: number of heads satisfies some inequality
      - query: number of heads equals some value
    Example type:
      P( #H == 2 | #H >= 1 ) for n coins
    """
    rng = random.Random(rng_seed)

    vars_ = _coin_vars(n_coins)
    names = [v.name for v in vars_]

    # constraint like #H >= k1 or #H <= k1
    op1 = rng.choice([">=", "<="])
    k1 = rng.randint(1, n_coins - 1)  # avoid 0 and n (often too trivial)

    constraint = CountConstraint(values=["H"], vars=names, op=op1, k=k1)

    # query like #H == k2
    k2 = rng.randint(0, n_coins)
    query = CountConstraint(values=["H"], vars=names, op="==", k=k2)

    return PuzzleSpec(variables=vars_, constraints=[constraint], query=query)
