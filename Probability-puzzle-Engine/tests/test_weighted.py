import pytest
from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint, SumConstraint
from ppe.core.exact import solve_exact


def _biased_coin(p_heads: float) -> VariableSpec:
    """VariableSpec for a coin with P(H) = p_heads."""
    return VariableSpec(name="c1", domain=["H", "T"], weights=[p_heads, 1 - p_heads])


def test_biased_coin_single_unconditional():
    """P(H) on a biased coin with P(H)=0.75."""
    puzzle = PuzzleSpec(
        variables=[_biased_coin(0.75)],
        constraints=[],
        query=CountConstraint(values=["H"], vars=["c1"], op="==", k=1),
    )
    result = solve_exact(puzzle)
    assert result.weighted is True
    assert abs(result.probability - 0.75) < 1e-9


def test_biased_coin_two_heads_unconditional():
    """P(2H) = 0.75^2 = 0.5625 for two independent biased coins."""
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"], weights=[3, 1]),
            VariableSpec(name="c2", domain=["H", "T"], weights=[3, 1]),
        ],
        constraints=[],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )
    result = solve_exact(puzzle)
    assert result.weighted is True
    assert abs(result.probability - 0.5625) < 1e-9


def test_biased_coin_conditional():
    """P(2H | >=1H) for biased coin P(H)=0.75.

    States:
      HH: 0.75*0.75 = 0.5625
      HT: 0.75*0.25 = 0.1875
      TH: 0.25*0.75 = 0.1875
      TT: 0.25*0.25 = 0.0625
    P(>=1H) = 0.5625 + 0.1875 + 0.1875 = 0.9375
    P(2H | >=1H) = 0.5625 / 0.9375 = 0.6
    """
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"], weights=[3, 1]),
            VariableSpec(name="c2", domain=["H", "T"], weights=[3, 1]),
        ],
        constraints=[CountConstraint(values=["H"], vars=["c1", "c2"], op=">=", k=1)],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )
    result = solve_exact(puzzle)
    assert result.weighted is True
    assert abs(result.probability - 0.6) < 1e-9


def test_weights_normalized():
    """Weights [2, 2] should normalize to [0.5, 0.5], producing uniform result."""
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"], weights=[2, 2]),
            VariableSpec(name="c2", domain=["H", "T"], weights=[2, 2]),
        ],
        constraints=[CountConstraint(values=["H"], vars=["c1", "c2"], op=">=", k=1)],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )
    result = solve_exact(puzzle)
    # Should give same result as uniform: 1/3
    assert abs(result.probability - (1 / 3)) < 1e-9


def test_mixed_weighted_and_uniform():
    """One variable has weights, the other is uniform."""
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"], weights=[1, 0]),  # always H
            VariableSpec(name="c2", domain=["H", "T"]),                  # uniform
        ],
        constraints=[],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )
    result = solve_exact(puzzle)
    # c1 is always H, c2 is fair -> P(2H) = 1 * 0.5 = 0.5
    assert result.weighted is True
    assert abs(result.probability - 0.5) < 1e-9


def test_uniform_puzzle_not_flagged_as_weighted():
    """A puzzle with no weights should have weighted=False."""
    puzzle = PuzzleSpec(
        variables=[VariableSpec(name="c1", domain=["H", "T"])],
        constraints=[],
        query=CountConstraint(values=["H"], vars=["c1"], op="==", k=1),
    )
    result = solve_exact(puzzle)
    assert result.weighted is False


def test_weight_validation_wrong_length():
    """Weights with wrong length should raise."""
    with pytest.raises(Exception):
        VariableSpec(name="c1", domain=["H", "T"], weights=[0.5])


def test_weight_validation_negative():
    """Negative weights should raise."""
    with pytest.raises(Exception):
        VariableSpec(name="c1", domain=["H", "T"], weights=[-0.5, 1.5])


def test_weight_validation_all_zero():
    """All-zero weights should raise."""
    with pytest.raises(Exception):
        VariableSpec(name="c1", domain=["H", "T"], weights=[0, 0])
