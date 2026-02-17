# Probability Puzzle Engine (PPE)

An interactive probability puzzle solver and generator designed to model, solve, and explain discrete probability problems using exact enumeration and Monte Carlo simulation.

Inspired by probability and combinatorics puzzles commonly used in quantitative trading and systems interviews, with an emphasis on correctness, transparency, and testability.

## Features

### Exact Probability Solver
- Solves discrete probability puzzles by explicitly enumerating the sample space
- Computes conditional probabilities of the form P(query | constraints)
- Supports **weighted outcomes** (biased coins, loaded dice)
- Returns probability, internal counts (total / given / hit), and optional state traces

### Monte Carlo Solver
- Estimates probabilities via rejection sampling
- Configurable sample count, confidence level, and random seed
- Returns Wilson score confidence intervals

### Human-Readable Explanations
- Step-by-step breakdown of variables, constraints, query, state counts, and final probability
- GCD-reduced fractions (e.g. "1/3" instead of raw decimals)

### Puzzle DSL (Domain-Specific Language)
- Structured JSON-based puzzle specification using Pydantic v2 models
- Three constraint types:
  - **CountConstraint** (`count_eq`) — count of matching values across variables
  - **ValueConstraint** (`value_eq`) — single variable equals a specific value
  - **SumConstraint** (`sum_eq`) — sum of numeric variable values
- All constraints support operators: `==`, `>=`, `<=`, `>`, `<`

### Puzzle Generators
- **Coin puzzles** — random conditional coin-flip problems
- **Dice puzzles** — random sum/count constraints on multi-sided dice
- Seeded for reproducibility

### Web UI
- Full single-page interactive interface served at `/`
- Puzzle builder with variable, constraint, and query editors
- Preset buttons for coins and dice
- Puzzle library with 8 classic problems (Two Coins, Dice Sum=7, Double Sixes, Loaded Coin, etc.)
- Three solver modes: Exact, Monte Carlo, and Compare (side-by-side)
- Animated probability bar, state counts, confidence interval visualization
- State explorer table with given/hit state highlighting
- Dark/light theme with localStorage persistence
- History drawer (last 50 solves, click to restore)
- JSON editor modal for raw puzzle editing
- Sharing via URL (base64-encoded) and clipboard
- Keyboard shortcuts (Ctrl+Enter to solve, Ctrl+Shift+J for JSON editor)
- Responsive layout (2-column desktop, single-column mobile)

### API Interface
- FastAPI backend with Swagger UI at `/docs`
- Endpoints:
  - `GET /health` — health check
  - `GET /generate/coin` — generate a random coin puzzle
  - `GET /generate/dice` — generate a random dice puzzle
  - `POST /solve/exact` — solve by exact enumeration (optional trace)
  - `POST /solve/monte_carlo` — solve via Monte Carlo sampling
  - `POST /solve/explain` — solve and return human-readable explanation

### Testing
- 71 unit tests covering all modules
- Test suites: exact solver (coins & dice), Monte Carlo, constraints, weighted outcomes, generators, explanations

---

## Example Puzzle

**Problem:** What is the probability of getting two heads, given that at least one head appears when flipping two fair coins?

**Puzzle Specification:**
```json
{
  "variables": [
    { "name": "c1", "domain": ["H", "T"] },
    { "name": "c2", "domain": ["H", "T"] }
  ],
  "constraints": [
    { "type": "count_eq", "values": ["H"], "vars": ["c1", "c2"], "op": ">=", "k": 1 }
  ],
  "query": {
    "type": "count_eq",
    "values": ["H"],
    "vars": ["c1", "c2"],
    "op": "==",
    "k": 2
  }
}
```

**Output:**
```json
{
  "probability": 0.3333333333333333,
  "counts": { "total": 4, "given": 3, "hit": 1 },
  "weighted": false,
  "explanation": "Variables: c1 ∈ {H, T}, c2 ∈ {H, T}\n..."
}
```

---

## Project Structure

```
probability-puzzle-engine/
├── README.md
├── LICENSE
├── pyproject.toml
├── src/
│   └── ppe/
│       ├── api/
│       │   └── main.py              # FastAPI entrypoint + UI serving
│       ├── core/
│       │   ├── exact.py             # Exact enumeration solver
│       │   ├── monte_carlo.py       # Monte Carlo solver with Wilson CI
│       │   ├── explanation.py       # Human-readable explanation generator
│       │   ├── state_space.py       # Sample space construction
│       │   └── constraint.py        # Constraint evaluation logic
│       ├── dsl/
│       │   └── schema.py            # Pydantic v2 puzzle specification models
│       ├── generate/
│       │   ├── coin_puzzles.py      # Random coin puzzle generator
│       │   └── dice_puzzles.py      # Random dice puzzle generator
│       └── static/
│           └── index.html           # Single-page web UI
└── tests/
    ├── test_exact_coin.py
    ├── test_exact_dice.py
    ├── test_monte_carlo.py
    ├── test_constraints.py
    ├── test_weighted.py
    ├── test_generators.py
    └── test_explanation.py
```

---

## Installation

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e .[dev]
```

## Running the Server

```bash
uvicorn ppe.api.main:app --reload --port 8200
```

Then open:
- **Web UI:** http://127.0.0.1:8200/
- **API Docs:** http://127.0.0.1:8200/docs

## Running Tests

```bash
pytest -v
```

All 71 tests should pass, covering exact solving, Monte Carlo estimation, constraint evaluation, weighted outcomes, puzzle generators, and explanations.

---

## API Quick Reference

```bash
# Health check
curl http://127.0.0.1:8200/health

# Generate a random 3-coin puzzle
curl http://127.0.0.1:8200/generate/coin?n_coins=3

# Generate a random 2d6 dice puzzle
curl "http://127.0.0.1:8200/generate/dice?n_dice=2&n_sides=6"

# Solve exact
curl -X POST http://127.0.0.1:8200/solve/exact \
  -H "Content-Type: application/json" \
  -d '{"variables":[{"name":"c1","domain":["H","T"]},{"name":"c2","domain":["H","T"]}],"constraints":[{"type":"count_eq","values":["H"],"vars":["c1","c2"],"op":">=","k":1}],"query":{"type":"count_eq","values":["H"],"vars":["c1","c2"],"op":"==","k":2}}'

# Monte Carlo (10,000 samples)
curl -X POST "http://127.0.0.1:8200/solve/monte_carlo?n_samples=10000" \
  -H "Content-Type: application/json" \
  -d '{"variables":[{"name":"c1","domain":["H","T"]},{"name":"c2","domain":["H","T"]}],"constraints":[],"query":{"type":"count_eq","values":["H"],"vars":["c1","c2"],"op":"==","k":2}}'
```

---

## Design Philosophy

- **Correctness first** — all probabilities derived from explicit state counting or well-defined sampling
- **No hidden math** — intermediate counts and confidence intervals are always exposed
- **Composable architecture** — solvers, constraints, and generators are modular and independently testable
- **Interview-realistic** — models how probability problems are reasoned about step-by-step

## Roadmap

Planned extensions:
- Optional OCaml backend for functional correctness guarantees
- More puzzle types (card draws, urn problems, Bayesian updates)
- Puzzle difficulty scoring and uniqueness checks
- Batch puzzle generation and export

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Alex Chidera Umeasalugo

