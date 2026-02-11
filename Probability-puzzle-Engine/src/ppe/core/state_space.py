from __future__ import annotations
from itertools import product
from typing import Dict, Iterable, List, Tuple

def build_state_space(var_domains: List[Tuple[str, List[str]]]) -> Iterable[Dict[str, str]]:
    """
    Builds the full sample space as dict assignments:
      [{"c1":"H","c2":"T"}, ...]
    """
    names = [n for n, _ in var_domains]
    domains = [d for _, d in var_domains]
    for combo in product(*domains):
        yield dict(zip(names, combo))
