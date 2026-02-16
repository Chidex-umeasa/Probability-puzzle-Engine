import pytest
from ppe.dsl.schema import PuzzleSpec, VariableSpec, CountConstraint, SumConstraint
from ppe.core.monte_carlo import solve_monte_carlo


def _two_coin_puzzle():
    return PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"]),
            VariableSpec(name="c2", domain=["H", "T"]),
        ],
        constraints=[CountConstraint(values=["H"], vars=["c1", "c2"], op=">=", k=1)],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )


def _two_dice_puzzle():
    domain = [str(i) for i in range(1, 7)]
    return PuzzleSpec(
        variables=[VariableSpec(name="d1", domain=domain), VariableSpec(name="d2", domain=domain)],
        constraints=[],
        query=SumConstraint(vars=["d1", "d2"], op="==", k=7),
    )


def test_mc_coin_estimate_within_ci():
    """MC estimate of P(2H | >=1H) = 1/3 should be within 95% CI."""
    puzzle = _two_coin_puzzle()
    res = solve_monte_carlo(puzzle, n_samples=20_000, confidence=0.95, seed=42)
    lo, hi = res.confidence_interval
    assert lo <= (1 / 3) <= hi, f"True value 1/3 not in CI [{lo:.4f}, {hi:.4f}]"
    assert abs(res.probability - (1 / 3)) < 0.05


def test_mc_dice_sum7_estimate():
    """MC estimate of P(sum==7) ≈ 1/6 for two dice."""
    puzzle = _two_dice_puzzle()
    res = solve_monte_carlo(puzzle, n_samples=50_000, confidence=0.95, seed=123)
    lo, hi = res.confidence_interval
    true_p = 1 / 6
    assert lo <= true_p <= hi, f"True value {true_p:.4f} not in CI [{lo:.4f}, {hi:.4f}]"


def test_mc_result_fields():
    """Result contains all expected fields with correct types."""
    puzzle = _two_coin_puzzle()
    res = solve_monte_carlo(puzzle, n_samples=1000, seed=0)
    assert 0.0 <= res.probability <= 1.0
    lo, hi = res.confidence_interval
    assert 0.0 <= lo <= hi <= 1.0
    assert res.confidence_level == 0.95
    assert res.counts["trials"] == 1000
    assert res.counts["given_hits"] + res.counts["trials"] - res.counts["given_hits"] == res.counts["trials"]


def test_mc_seeded_reproducibility():
    """Same seed produces same result."""
    puzzle = _two_coin_puzzle()
    r1 = solve_monte_carlo(puzzle, n_samples=5000, seed=7)
    r2 = solve_monte_carlo(puzzle, n_samples=5000, seed=7)
    assert r1.probability == r2.probability
    assert r1.counts == r2.counts


def test_mc_custom_confidence():
    """Custom confidence level is preserved in result."""
    puzzle = _two_coin_puzzle()
    res = solve_monte_carlo(puzzle, n_samples=5000, confidence=0.99, seed=1)
    assert res.confidence_level == 0.99
    lo, hi = res.confidence_interval
    assert hi - lo > 0  # CI has non-zero width


def test_mc_weighted_coin():
    """Biased coin P(H)=0.75: P(2H) ≈ 0.75^2 = 0.5625 unconditionally."""
    puzzle = PuzzleSpec(
        variables=[
            VariableSpec(name="c1", domain=["H", "T"], weights=[3, 1]),
            VariableSpec(name="c2", domain=["H", "T"], weights=[3, 1]),
        ],
        constraints=[],
        query=CountConstraint(values=["H"], vars=["c1", "c2"], op="==", k=2),
    )
    res = solve_monte_carlo(puzzle, n_samples=50_000, confidence=0.95, seed=99)
    true_p = 0.75 * 0.75
    assert abs(res.probability - true_p) < 0.02, (
        f"MC estimate {res.probability:.4f} too far from true {true_p:.4f}"
    )
