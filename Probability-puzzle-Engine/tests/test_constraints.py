import pytest
from ppe.dsl.schema import CountConstraint, ValueConstraint, SumConstraint
from ppe.core.constraint import eval_count_constraint, eval_value_constraint, eval_sum_constraint


# ── CountConstraint ───────────────────────────────────────────────────────────

class TestCountConstraint:
    def test_count_eq(self):
        c = CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=1)
        assert eval_count_constraint({"c1": "H", "c2": "T"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "H"}, c) is False
        assert eval_count_constraint({"c1": "T", "c2": "T"}, c) is False

    def test_count_ge(self):
        c = CountConstraint(values=["H"], vars=["c1", "c2", "c3"], op=">=", k=2)
        assert eval_count_constraint({"c1": "H", "c2": "H", "c3": "T"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "H", "c3": "H"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "T", "c3": "T"}, c) is False

    def test_count_le(self):
        c = CountConstraint(values=["T"], vars=["c1", "c2"], op="<=", k=1)
        assert eval_count_constraint({"c1": "T", "c2": "H"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "H"}, c) is True
        assert eval_count_constraint({"c1": "T", "c2": "T"}, c) is False

    def test_count_gt(self):
        c = CountConstraint(values=["H"], vars=["c1", "c2"], op=">", k=1)
        assert eval_count_constraint({"c1": "H", "c2": "H"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "T"}, c) is False

    def test_count_lt(self):
        c = CountConstraint(values=["H"], vars=["c1", "c2"], op="<", k=2)
        assert eval_count_constraint({"c1": "H", "c2": "T"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "H"}, c) is False

    def test_multiple_target_values(self):
        c = CountConstraint(values=["H", "X"], vars=["c1", "c2", "c3"], op="==", k=2)
        assert eval_count_constraint({"c1": "H", "c2": "X", "c3": "T"}, c) is True
        assert eval_count_constraint({"c1": "H", "c2": "T", "c3": "T"}, c) is False


# ── ValueConstraint ───────────────────────────────────────────────────────────

class TestValueConstraint:
    def test_match(self):
        c = ValueConstraint(var="c1", value="H")
        assert eval_value_constraint({"c1": "H", "c2": "T"}, c) is True

    def test_no_match(self):
        c = ValueConstraint(var="c1", value="H")
        assert eval_value_constraint({"c1": "T", "c2": "H"}, c) is False

    def test_numeric_value(self):
        c = ValueConstraint(var="d1", value="6")
        assert eval_value_constraint({"d1": "6", "d2": "3"}, c) is True
        assert eval_value_constraint({"d1": "5", "d2": "6"}, c) is False


# ── SumConstraint ─────────────────────────────────────────────────────────────

class TestSumConstraint:
    def test_sum_eq(self):
        c = SumConstraint(vars=["d1", "d2"], op="==", k=7)
        assert eval_sum_constraint({"d1": "3", "d2": "4"}, c) is True
        assert eval_sum_constraint({"d1": "6", "d2": "6"}, c) is False

    def test_sum_ge(self):
        c = SumConstraint(vars=["d1", "d2"], op=">=", k=10)
        assert eval_sum_constraint({"d1": "5", "d2": "6"}, c) is True
        assert eval_sum_constraint({"d1": "4", "d2": "4"}, c) is False

    def test_sum_le(self):
        c = SumConstraint(vars=["d1", "d2"], op="<=", k=4)
        assert eval_sum_constraint({"d1": "2", "d2": "2"}, c) is True
        assert eval_sum_constraint({"d1": "3", "d2": "3"}, c) is False

    def test_sum_gt(self):
        c = SumConstraint(vars=["d1", "d2"], op=">", k=11)
        assert eval_sum_constraint({"d1": "6", "d2": "6"}, c) is True
        assert eval_sum_constraint({"d1": "5", "d2": "6"}, c) is False

    def test_sum_lt(self):
        c = SumConstraint(vars=["d1", "d2"], op="<", k=3)
        assert eval_sum_constraint({"d1": "1", "d2": "1"}, c) is True
        assert eval_sum_constraint({"d1": "1", "d2": "2"}, c) is False

    def test_three_dice(self):
        c = SumConstraint(vars=["d1", "d2", "d3"], op="==", k=18)
        assert eval_sum_constraint({"d1": "6", "d2": "6", "d3": "6"}, c) is True
        assert eval_sum_constraint({"d1": "6", "d2": "6", "d3": "5"}, c) is False
