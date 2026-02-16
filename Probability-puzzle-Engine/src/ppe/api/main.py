from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from ppe.dsl.schema import PuzzleSpec
from ppe.core.exact import solve_exact
from ppe.core.monte_carlo import solve_monte_carlo
from ppe.core.explanation import explain
from ppe.generate.coin_puzzles import generate_coin_puzzle
from ppe.generate.dice_puzzles import generate_dice_puzzle

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="Probability Puzzle Engine",
    description=(
        "Solve and generate discrete probability puzzles.\n\n"
        "Supports exact enumeration, Monte Carlo estimation, weighted outcomes, "
        "and human-readable explanations."
    ),
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_ui():
    return (_STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Generators ────────────────────────────────────────────────────────────────

@app.get("/generate/coin", summary="Generate a random coin-flip puzzle")
def gen_coin(n_coins: int = Query(3, ge=1, le=20), seed: int | None = None):
    puzzle = generate_coin_puzzle(n_coins=n_coins, rng_seed=seed)
    return puzzle.model_dump()


@app.get("/generate/dice", summary="Generate a random dice puzzle")
def gen_dice(
    n_dice: int = Query(2, ge=1, le=10),
    n_sides: int = Query(6, ge=2, le=20),
    seed: int | None = None,
):
    puzzle = generate_dice_puzzle(n_dice=n_dice, n_sides=n_sides, rng_seed=seed)
    return puzzle.model_dump()


# ── Solvers ───────────────────────────────────────────────────────────────────

@app.post("/solve/exact", summary="Solve a puzzle by exact enumeration")
def solve_exact_endpoint(
    puzzle: PuzzleSpec,
    trace: bool = Query(False, description="Include sample states in response"),
    max_trace: int = Query(50, ge=1, le=500),
):
    res = solve_exact(puzzle, trace=trace, max_trace=max_trace)
    out: dict = {
        "probability": res.probability,
        "counts": res.counts,
        "weighted": res.weighted,
    }
    if trace:
        out["given_states"] = res.given_states
        out["hit_states"] = res.hit_states
    return out


@app.post("/solve/monte_carlo", summary="Estimate probability via Monte Carlo sampling")
def solve_mc_endpoint(
    puzzle: PuzzleSpec,
    n_samples: int = Query(10_000, ge=100, le=1_000_000),
    confidence: float = Query(0.95, ge=0.5, le=0.999),
    seed: int | None = None,
):
    res = solve_monte_carlo(puzzle, n_samples=n_samples, confidence=confidence, seed=seed)
    return {
        "probability": res.probability,
        "confidence_interval": list(res.confidence_interval),
        "confidence_level": res.confidence_level,
        "counts": res.counts,
    }


@app.post("/solve/explain", summary="Solve and return a human-readable explanation")
def solve_explain_endpoint(puzzle: PuzzleSpec):
    res = solve_exact(puzzle)
    text = explain(puzzle, res)
    return {
        "probability": res.probability,
        "counts": res.counts,
        "weighted": res.weighted,
        "explanation": text,
    }
