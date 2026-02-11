Probability Puzzle Engine (PPE)
An interactive probability puzzle solver and generator designed to model, solve, and explain discrete probability problems using exact enumeration and simulation-based methods.
This project is inspired by the style of probability and combinatorics puzzles commonly used in quantitative trading and systems interviews, with an emphasis on correctness, transparency, and testability.

    Features (Current)
Exact Probability Solver
- Solves discrete probability puzzles by explicitly enumerating the sample space
- Supports conditional probabilities of the form
   𝑃 (query | constraints )
- Produces both:
 - Final probability
 - Internal counts (total states, conditioned states, matching states)

    Puzzle DSL (Domain-Specific Language)
- Structured JSON-based puzzle specification
- Clear separation between:
 - Variables and domains
 - Conditioning constraints (“given”)
 - Query event

    API Interface
- FastAPI backend with a clean /solve/exact endpoint
- Interactive testing via Swagger UI (/docs)
- Designed to support future solver backends without API changes

    Testing

- Unit-tested with pytest
- Deterministic, reproducible results
- Covers canonical probability puzzles (e.g. coin flips) 

Example Puzzle
Problem:
What is the probability of getting two heads, given that at least one head appears when flipping two fair coins?

Puzzle Specification
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

Output
{
  "probability": 0.3333333333333333,
  "counts": {
    "total": 4,
    "given": 3,
    "hit": 1
  }
}

Project Structure
probability-puzzle-engine/
├── README.md
├── pyproject.toml
├── src/
│   └── ppe/
│       ├── api/
│       │   └── main.py          # FastAPI entrypoint
│       ├── core/
│       │   ├── exact.py         # Exact enumeration solver
│       │   ├── state_space.py   # Sample space construction
│       │   └── constraints.py   # Constraint evaluation logic
│       ├── dsl/
│       │   └── schema.py        # Puzzle specification models
│       └── generate/            # Puzzle generators (WIP)
└── tests/
    └── test_exact_coin.py

Installation
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -e .[dev]

Running the Server
uvicorn ppe.api.main:app --reload --port 8123
Then open:
http://127.0.0.1:8123/docs
Running Tests
pytest -q

    Design Philosophy
Correctness first: all probabilities are derived from explicit state counting
No hidden math: intermediate counts are exposed
Composable architecture: solvers, constraints, and generators are modular
Interview-realistic: models how probability problems are reasoned about step-by-step

    Roadmap
Planned extensions:
- Weighted outcomes (biased coins, non-uniform dice)
- Monte Carlo solver with confidence intervals
- Explanation traces (“why this probability is correct”)
- Puzzle generator with uniqueness checks
- Web-based interactive UI
- Optional OCaml backend for functional correctness guarantees

    Status
🚧 Active development
Currently supports exact solving for discrete, finite probability spaces.