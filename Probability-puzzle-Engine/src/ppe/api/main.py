from __future__ import annotations
from fastapi import FastAPI, Query
from ppe.dsl.schema import PuzzleSpec
from ppe.core.exact import solve_exact
from ppe.generate.coin_puzzles import generate_coin_puzzle


app = FastAPI(title="Probability Puzzle Engine")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/generate/coin")
def gen_coin(n_coins: int = 3, seed: int | None = None):
    puzzle = generate_coin_puzzle(n_coins=n_coins, rng_seed=seed)
    return puzzle.model_dump()


@app.post("/solve/exact")
def solve(puzzle: PuzzleSpec, trace: bool = Query(False), max_trace: int = Query(50, ge=1, le=500)):
    res = solve_exact(puzzle, trace=trace, max_trace=max_trace)
    out = {"probability": res.probability, "counts": res.counts}
    if trace:
        out["given_states"] = res.given_states
        out["hit_states"] = res.hit_states
    return out
