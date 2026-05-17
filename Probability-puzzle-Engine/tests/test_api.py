from fastapi.testclient import TestClient
from ppe.api.main import app

client = TestClient(app)

_TWO_COIN = {
    "variables": [{"name": "c1", "domain": ["H", "T"]}, {"name": "c2", "domain": ["H", "T"]}],
    "constraints": [{"type": "count_eq", "values": ["H"], "vars": ["c1", "c2"], "op": ">=", "k": 1}],
    "query": {"type": "count_eq", "values": ["H"], "vars": ["c1", "c2"], "op": "==", "k": 2},
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_generate_coin():
    r = client.get("/generate/coin?n_coins=3&seed=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["variables"]) == 3
    for v in data["variables"]:
        assert set(v["domain"]) == {"H", "T"}


def test_generate_dice():
    r = client.get("/generate/dice?n_dice=2&n_sides=6&seed=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["variables"]) == 2


def test_solve_exact_classic():
    r = client.post("/solve/exact", json=_TWO_COIN)
    assert r.status_code == 200
    data = r.json()
    assert abs(data["probability"] - 1 / 3) < 1e-9
    assert data["counts"]["given"] == 3
    assert data["counts"]["hit"] == 1


def test_solve_exact_trace():
    r = client.post("/solve/exact?trace=true&max_trace=10", json=_TWO_COIN)
    assert r.status_code == 200
    data = r.json()
    assert len(data["given_states"]) == 3
    assert len(data["hit_states"]) == 1


def test_solve_exact_too_large():
    # 7 variables × 10-value domain = 10^7 = 10M states, exceeds the 1M limit
    payload = {
        "variables": [{"name": f"x{i}", "domain": [str(j) for j in range(10)]} for i in range(7)],
        "constraints": [],
        "query": {"type": "value_eq", "var": "x0", "value": "1"},
    }
    r = client.post("/solve/exact", json=payload)
    assert r.status_code == 422
    assert "State space" in r.json()["detail"]


def test_solve_monte_carlo():
    r = client.post("/solve/monte_carlo?n_samples=20000&seed=42", json=_TWO_COIN)
    assert r.status_code == 200
    data = r.json()
    lo, hi = data["confidence_interval"]
    assert lo <= 1 / 3 <= hi
    assert abs(data["probability"] - 1 / 3) < 0.05


def test_solve_explain():
    payload = {
        "variables": [{"name": "c1", "domain": ["H", "T"]}, {"name": "c2", "domain": ["H", "T"]}],
        "constraints": [],
        "query": {"type": "count_eq", "values": ["H"], "vars": ["c1", "c2"], "op": "==", "k": 2},
    }
    r = client.post("/solve/explain", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "explanation" in data
    assert "P(query | given)" in data["explanation"]


def test_invalid_variable_reference():
    payload = {
        "variables": [{"name": "c1", "domain": ["H", "T"]}],
        "constraints": [{"type": "count_eq", "values": ["H"], "vars": ["c1", "c99"], "op": ">=", "k": 1}],
        "query": {"type": "count_eq", "values": ["H"], "vars": ["c1"], "op": "==", "k": 1},
    }
    r = client.post("/solve/exact", json=payload)
    assert r.status_code == 422


def test_neq_operator():
    # P(sum != 7 | no constraint) for two dice
    payload = {
        "variables": [
            {"name": "d1", "domain": ["1", "2", "3", "4", "5", "6"]},
            {"name": "d2", "domain": ["1", "2", "3", "4", "5", "6"]},
        ],
        "constraints": [],
        "query": {"type": "sum_eq", "vars": ["d1", "d2"], "op": "!=", "k": 7},
    }
    r = client.post("/solve/exact", json=payload)
    assert r.status_code == 200
    data = r.json()
    # P(sum == 7) = 6/36 = 1/6, so P(sum != 7) = 5/6
    assert abs(data["probability"] - 5 / 6) < 1e-9
