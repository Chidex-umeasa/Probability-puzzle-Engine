import pytest
from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint
from ppe.core.exact import solve_exact


def _two_coin_puzzle(constraint_op, constraint_k, query_k):
    return PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"]),
            VariableSpec(name="c2", domain=["H", "T"]),
        ],
        constraints=[CountConstraint(values=["H"], vars=["c1", "c2"], op=constraint_op, k=constraint_k)],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=query_k),
    )


def test_two_coins_p_2heads_given_atleast1():
    """Classic: P(2H | >=1H) = 1/3."""
    puzzle = _two_coin_puzzle(">=", 1, 2)
    result = solve_exact(puzzle)
    assert abs(result.probability - (1 / 3)) < 1e-9
    assert result.counts["given"] == 3
    assert result.counts["hit"] == 1


def test_two_coins_p_0heads_given_atleast1():
    """P(0H | >=1H) = 0."""
    puzzle = _two_coin_puzzle(">=", 1, 0)
    result = solve_exact(puzzle)
    assert result.probability == 0.0
    assert result.counts["hit"] == 0


def test_two_coins_p_1head_given_atleast1():
    """P(1H | >=1H) = 2/3."""
    puzzle = _two_coin_puzzle(">=", 1, 1)
    result = solve_exact(puzzle)
    assert abs(result.probability - (2 / 3)) < 1e-9
    assert result.counts["hit"] == 2


def test_two_coins_unconditional():
    """P(2H) = 1/4 with no constraints."""
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"]),
            VariableSpec(name="c2", domain=["H", "T"]),
        ],
        constraints=[],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )
    result = solve_exact(puzzle)
    assert abs(result.probability - 0.25) < 1e-9
    assert result.counts["total"] == 4
    assert result.counts["given"] == 4
    assert result.counts["hit"] == 1


def test_three_coins_p_3heads_given_atleast2():
    """P(3H | >=2H) = 1/4  (states >=2H: HHH,HHT,HTH,THH = 4; ==3H: HHH = 1)."""
    puzzle = PuzzleSpec(
        variables=[VariableSpec(name=f"c{i}", domain=["H", "T"]) for i in range(1, 4)],
        constraints=[CountConstraint(values=["H"], vars=["c1", "c2", "c3"], op=">=", k=2)],
        query=CountConstraint(values=["H"], vars=["c1", "c2", "c3"], op="==", k=3),
    )
    result = solve_exact(puzzle)
    assert result.counts["total"] == 8
    assert result.counts["given"] == 4
    assert result.counts["hit"] == 1
    assert abs(result.probability - 0.25) < 1e-9


def test_trace_returns_states():
    puzzle = _two_coin_puzzle(">=", 1, 2)
    result = solve_exact(puzzle, trace=True, max_trace=10)
    assert result.given_states is not None
    assert result.hit_states is not None
    assert len(result.given_states) == 3
    assert len(result.hit_states) == 1
    assert result.hit_states[0] == {"c1": "H", "c2": "H"}


def test_no_trace_states_are_none():
    puzzle = _two_coin_puzzle(">=", 1, 2)
    result = solve_exact(puzzle, trace=False)
    assert result.given_states is None
    assert result.hit_states is None
