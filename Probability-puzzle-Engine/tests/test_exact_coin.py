from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint
from ppe.core.exact import solve_exact

def test_two_coins_p_2heads_given_atleast1():
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H","T"]),
            VariableSpec(name="c2", domain=["H","T"]),
        ],
        constraints=[
            CountConstraint(values=["H"], vars=["c1","c2"], op=">=", k=1)
        ],
        query=CountConstraint(values=["H"], vars=["c1","c2"], op="==", k=2)
    )
    p, counts = solve_exact(puzzle)
    assert abs(p - (1/3)) < 1e-9
    assert counts["given"] == 3
    assert counts["hit"] == 1
