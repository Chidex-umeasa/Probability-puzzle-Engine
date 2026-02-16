import pytest
from ppe.dsl.schema import PuzzleSpec, SumConstraint, CountConstraint, ValueConstraint
from ppe.core.exact import solve_exact
from ppe.generate.coin_puzzles import generate_coin_puzzle
from ppe.generate.dice_puzzles import generate_dice_puzzle


# ── Coin generator ────────────────────────────────────────────────────────────

class TestCoinGenerator:
    def test_returns_puzzle_spec(self):
        puzzle = generate_coin_puzzle(n_coins=3)
        assert isinstance(puzzle, PuzzleSpec)

    def test_correct_variable_count(self):
        for n in (1, 3, 5):
            puzzle = generate_coin_puzzle(n_coins=n)
            assert len(puzzle.variables) == n

    def test_coin_domain(self):
        puzzle = generate_coin_puzzle(n_coins=4)
        for v in puzzle.variables:
            assert set(v.domain) == {"H", "T"}

    def test_has_constraint_and_query(self):
        puzzle = generate_coin_puzzle(n_coins=3)
        assert len(puzzle.constraints) >= 1
        assert puzzle.query is not None

    def test_seeded_reproducibility(self):
        p1 = generate_coin_puzzle(n_coins=5, rng_seed=42)
        p2 = generate_coin_puzzle(n_coins=5, rng_seed=42)
        assert p1.model_dump() == p2.model_dump()

    def test_different_seeds_may_differ(self):
        results = {generate_coin_puzzle(n_coins=5, rng_seed=i).model_dump().__repr__() for i in range(10)}
        assert len(results) > 1  # not all the same

    def test_generated_puzzle_is_solvable(self):
        for seed in range(10):
            puzzle = generate_coin_puzzle(n_coins=4, rng_seed=seed)
            result = solve_exact(puzzle)
            assert 0.0 <= result.probability <= 1.0


# ── Dice generator ────────────────────────────────────────────────────────────

class TestDiceGenerator:
    def test_returns_puzzle_spec(self):
        puzzle = generate_dice_puzzle(n_dice=2, n_sides=6)
        assert isinstance(puzzle, PuzzleSpec)

    def test_correct_variable_count(self):
        for n in (1, 2, 4):
            puzzle = generate_dice_puzzle(n_dice=n)
            assert len(puzzle.variables) == n

    def test_dice_domain(self):
        puzzle = generate_dice_puzzle(n_dice=2, n_sides=6)
        for v in puzzle.variables:
            assert v.domain == [str(i) for i in range(1, 7)]

    def test_custom_sides(self):
        puzzle = generate_dice_puzzle(n_dice=2, n_sides=4)
        for v in puzzle.variables:
            assert v.domain == ["1", "2", "3", "4"]

    def test_has_constraint_and_query(self):
        puzzle = generate_dice_puzzle()
        assert len(puzzle.constraints) >= 1
        assert puzzle.query is not None

    def test_seeded_reproducibility(self):
        p1 = generate_dice_puzzle(n_dice=3, n_sides=6, rng_seed=7)
        p2 = generate_dice_puzzle(n_dice=3, n_sides=6, rng_seed=7)
        assert p1.model_dump() == p2.model_dump()

    def test_generated_puzzle_is_solvable(self):
        for seed in range(10):
            puzzle = generate_dice_puzzle(n_dice=2, n_sides=6, rng_seed=seed)
            result = solve_exact(puzzle)
            assert 0.0 <= result.probability <= 1.0

    def test_constraint_is_valid_type(self):
        for seed in range(20):
            puzzle = generate_dice_puzzle(rng_seed=seed)
            for c in puzzle.constraints:
                assert isinstance(c, (SumConstraint, CountConstraint, ValueConstraint))
