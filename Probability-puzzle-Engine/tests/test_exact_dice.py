import pytest
from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint, SumConstraint
from ppe.core.exact import solve_exact


def _two_dice():
    domain = [str(i) for i in range(1, 7)]
    return [VariableSpec(name="d1", domain=domain), VariableSpec(name="d2", domain=domain)]


def test_two_dice_sum7_unconditional():
    """P(sum==7) = 6/36 = 1/6 for two fair dice."""
    puzzle = PuzzleSpec(
        variables=_two_dice(),
        constraints=[],
        query=SumConstraint(vars=["d1", "d2"], op="==", k=7),
    )
    result = solve_exact(puzzle)
    assert result.counts["total"] == 36
    assert result.counts["hit"] == 6
    assert abs(result.probability - (1 / 6)) < 1e-9


def test_two_dice_sum7_given_sum_ge6():
    """P(sum==7 | sum>=6) = 6/26."""
    puzzle = PuzzleSpec(
        variables=_two_dice(),
        constraints=[SumConstraint(vars=["d1", "d2"], op=">=", k=6)],
        query=SumConstraint(vars=["d1", "d2"], op="==", k=7),
    )
    result = solve_exact(puzzle)
    assert result.counts["given"] == 26
    assert result.counts["hit"] == 6
    assert abs(result.probability - (6 / 26)) < 1e-9


def test_two_dice_sum12():
    """P(sum==12) = 1/36 (only 6+6)."""
    puzzle = PuzzleSpec(
        variables=_two_dice(),
        constraints=[],
        query=SumConstraint(vars=["d1", "d2"], op="==", k=12),
    )
    result = solve_exact(puzzle)
    assert result.counts["hit"] == 1
    assert abs(result.probability - (1 / 36)) < 1e-9


def test_two_dice_at_least_one_six():
    """P(at least one 6) = 11/36."""
    puzzle = PuzzleSpec(
        variables=_two_dice(),
        constraints=[],
        query=CountConstraint(values=["6"], vars=["d1", "d2"], op=">=", k=1),
    )
    result = solve_exact(puzzle)
    assert result.counts["hit"] == 11
    assert abs(result.probability - (11 / 36)) < 1e-9


def test_two_dice_sum7_given_at_least_one_six():
    """P(sum==7 | at least one 6) = 2/11."""
    puzzle = PuzzleSpec(
        variables=_two_dice(),
        constraints=[CountConstraint(values=["6"], vars=["d1", "d2"], op=">=", k=1)],
        query=SumConstraint(vars=["d1", "d2"], op="==", k=7),
    )
    result = solve_exact(puzzle)
    assert result.counts["given"] == 11
    assert result.counts["hit"] == 2
    assert abs(result.probability - (2 / 11)) < 1e-9


def test_sum_impossible_returns_zero():
    """P(sum==100 | no constraint) = 0 for two 6-sided dice."""
    puzzle = PuzzleSpec(
        variables=_two_dice(),
        constraints=[],
        query=SumConstraint(vars=["d1", "d2"], op="==", k=100),
    )
    result = solve_exact(puzzle)
    assert result.probability == 0.0
    assert result.counts["hit"] == 0
