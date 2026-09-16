"""The attribution routes: reconciliation, ordering, peers, and the route-order guarantee.

The reconciliation is the one numeric property that matters here — the contributions
plus the residual must equal the window's log return. It holds by construction, because
each bar's price was derived from the numbers being summed, so a failure means the engine
and the decomposition have drifted apart rather than that a tolerance is too tight.

`GET /impact/portfolio` returning the portfolio payload rather than a symbol lookup is
O8, and it is a property of declaration order in the router.
"""

import pytest
from fastapi.testclient import TestClient

from app import state as state_module
from app.buffer import FACTORS
from app.main import app
from app.routers.impact import FACTOR_SENTENCES
from app.scenarios import BASELINE_ID, load_scenarios
from app.state import STARTING_POSITIONS, build_state

TOLERANCE = 1e-6


def report(capsys, message: str) -> None:
    with capsys.disabled():
        print(f"\n    {message}")


@pytest.fixture(scope="module")
def state():
    """Backfilled, with a scenario active so the window is a scenario window."""
    built = build_state()
    shock = next(
        one for one in load_scenarios().values() if one.id != BASELINE_ID
    )
    built.engine.activate(shock)
    for _ in range(90):
        built.engine.tick()
    return built


@pytest.fixture(scope="module")
def client(state):
    state_module._state = state
    with TestClient(app) as test_client:
        yield test_client
    state_module._state = None


def test_contributions_plus_residual_reconcile_with_the_move(
    client, state, capsys
) -> None:
    """To 1e-6, across every instrument in the universe."""
    worst = 0.0
    checked = 0
    for symbol in state.instruments:
        body = client.get(f"/impact/{symbol}").json()
        total = sum(one["contribution"] for one in body["contributions"])
        total += body["residual"]
        discrepancy = abs(total - body["log_return"])
        worst = max(worst, discrepancy)
        checked += 1
        assert discrepancy < TOLERANCE, f"{symbol} reconciles only to {discrepancy}"

    assert checked == len(state.instruments)
    report(capsys, f"{checked} instruments reconciled; worst discrepancy {worst:.3e}")


def test_contributions_are_ordered_by_descending_absolute_value(client, state) -> None:
    """A large negative ranks above a small positive."""
    for symbol in list(state.instruments)[:10]:
        values = [
            abs(one["contribution"])
            for one in client.get(f"/impact/{symbol}").json()["contributions"]
        ]
        assert all(a >= b for a, b in zip(values, values[1:])), values


def test_every_factor_appears_with_a_plain_language_sentence(
    client, state, capsys
) -> None:
    """One per factor, and no sentence names a beta or an exposure."""
    symbol = next(iter(state.instruments))
    body = client.get(f"/impact/{symbol}").json()

    assert {one["factor"] for one in body["contributions"]} == set(FACTORS)
    for one in body["contributions"]:
        assert one["sentence"], f"{one['factor']} carries no sentence"
        assert "beta" not in one["sentence"].lower()
        assert "exposure" not in one["sentence"].lower()

    report(capsys, f"{symbol}: " + " | ".join(
        one["sentence"] for one in body["contributions"][:3]
    ))


def test_the_sentences_cover_every_factor_key(capsys) -> None:
    """A factor with no phrase would raise where the panel is rendered."""
    assert set(FACTOR_SENTENCES) == set(FACTORS)
    report(capsys, f"FACTOR_SENTENCES keys: {sorted(FACTOR_SENTENCES)}")


def test_peers_are_same_sector_ranked_by_absolute_move(client, state, capsys) -> None:
    """A field on the response, so the panel issues no request per peer."""
    symbol = next(
        one for one, inst in state.instruments.items() if not inst.is_macro_driver
    )
    sector = state.instruments[symbol].sector
    peers = client.get(f"/impact/{symbol}").json()["peers"]

    assert peers, f"{symbol} has no peers in {sector}"
    assert symbol not in {peer["symbol"] for peer in peers}
    for peer in peers:
        assert state.instruments[peer["symbol"]].sector == sector
        assert peer["name"]
    moves = [abs(peer["move_pct"]) for peer in peers]
    assert all(a >= b for a, b in zip(moves, moves[1:])), moves

    report(capsys, f"{symbol} ({sector}) has {len(peers)} peers, ranked by |move|")


def test_impact_portfolio_is_the_portfolio_and_not_a_symbol_lookup(
    client, capsys
) -> None:
    """O8. A property of declaration order: portfolio is declared before {symbol}."""
    response = client.get("/impact/portfolio")
    assert response.status_code == 200

    body = response.json()
    assert "holdings" in body, "resolved as an instrument lookup, not the portfolio"
    assert "symbol" not in body
    assert {one["symbol"] for one in body["holdings"]} == set(STARTING_POSITIONS)
    assert isinstance(body["total_impact"], float)

    report(capsys, f"portfolio impact covered {len(body['holdings'])} holdings")


def test_position_impact_is_null_for_an_instrument_not_held(client, state) -> None:
    """Always present, with null permitted — the client sees a key that is always there."""
    unheld = next(one for one in state.instruments if one not in STARTING_POSITIONS)
    assert client.get(f"/impact/{unheld}").json()["position_impact"] is None

    held = next(iter(STARTING_POSITIONS))
    assert client.get(f"/impact/{held}").json()["position_impact"] is not None


def test_an_unknown_symbol_is_a_404(client) -> None:
    assert client.get("/impact/NOPE").status_code == 404
