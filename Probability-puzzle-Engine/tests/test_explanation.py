import pytest
from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint, SumConstraint, ValueConstraint
from ppe.core.exact import solve_exact
from ppe.core.explanation import explain, _as_fraction, _describe_constraint


class TestAsFraction:
    def test_zero_given(self):
        assert "undefined" in _as_fraction(0, 0)

    def test_zero_hits(self):
        assert _as_fraction(0, 5) == "0"

    def test_reducible(self):
        assert _as_fraction(2, 6) == "1/3"

    def test_whole_number(self):
        assert _as_fraction(6, 6) == "1"

    def test_irreducible(self):
        assert _as_fraction(1, 3) == "1/3"


class TestDescribeConstraint:
    def test_count_constraint(self):
        c = CountConstraint(values=["H"], vars=["c1", "c2"], op=">=", k=1)
        desc = _describe_constraint(c)
        assert "H" in desc
        assert ">=" in desc
        assert "1" in desc

    def test_value_constraint(self):
        c = ValueConstraint(var="c1", value="H")
        desc = _describe_constraint(c)
        assert "c1" in desc
        assert "H" in desc

    def test_sum_constraint(self):
        c = SumConstraint(vars=["d1", "d2"], op="==", k=7)
        desc = _describe_constraint(c)
        assert "7" in desc
        assert "==" in desc


class TestExplain:
    def _classic_puzzle(self):
        return PuzzleSpec(
            variables=[
                VariableSpec(name="c1", domain=["H", "T"]),
                VariableSpec(name="c2", domain=["H", "T"]),
            ],
            constraints=[CountConstraint(values=["H"], vars=["c1", "c2"], op=">=", k=1)],
            query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
        )

    def test_explain_returns_string(self):
        puzzle = self._classic_puzzle()
        result = solve_exact(puzzle)
        text = explain(puzzle, result)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_explain_contains_key_info(self):
        puzzle = self._classic_puzzle()
        result = solve_exact(puzzle)
        text = explain(puzzle, result)
        assert "1/3" in text
        assert "c1" in text
        assert "c2" in text
        assert "4" in text   # total states
        assert "3" in text   # given states
        assert "1" in text   # hit states

    def test_explain_no_constraints(self):
        puzzle = PuzzleSpec(
            variables=[VariableSpec(name="c1", domain=["H", "T"])],
            constraints=[],
            query=CountConstraint(values=["H"], vars=["c1"], op="==", k=1),
        )
        result = solve_exact(puzzle)
        text = explain(puzzle, result)
        assert "none" in text.lower() or "unconditional" in text.lower()

    def test_explain_weighted_puzzle(self):
        puzzle = PuzzleSpec(
            variables=[VariableSpec(name="c1", domain=["H", "T"], weights=[3, 1])],
            constraints=[],
            query=CountConstraint(values=["H"], vars=["c1"], op="==", k=1),
        )
        result = solve_exact(puzzle)
        text = explain(puzzle, result)
        assert "weighted" in text.lower()

    def test_explain_dice_puzzle(self):
        domain = [str(i) for i in range(1, 7)]
        puzzle = PuzzleSpec(
            variables=[
                VariableSpec(name="d1", domain=domain),
                VariableSpec(name="d2", domain=domain),
            ],
            constraints=[],
            query=SumConstraint(vars=["d1", "d2"], op="==", k=7),
        )
        result = solve_exact(puzzle)
        text = explain(puzzle, result)
        assert "1/6" in text
        assert "36" in text  # total states
