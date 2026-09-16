"""The ranked lists and the macro strip.

Sort direction is asserted **pairwise across the whole list**, not by comparing the
first two entries: a list sorted correctly at its head and wrong at its tail would pass
the weaker check.

The membership-change assertion is the backend half of the demo's payoff. A scenario has
to visibly move the rankings, and this is the only place that becomes checkable without
a browser.
"""

import pytest
from fastapi.testclient import TestClient

from app import state as state_module
from app.buffer import FACTORS
from app.main import app
from app.scenarios import load_scenarios
from app.state import build_state


def report(capsys, message: str) -> None:
    with capsys.disabled():
        print(f"\n    {message}")


@pytest.fixture(scope="module")
def state():
    return build_state()


@pytest.fixture(scope="module")
def client(state):
    state_module._state = state
    with TestClient(app) as test_client:
        yield test_client
    state_module._state = None


def descending(values: list[float]) -> bool:
    return all(a >= b for a, b in zip(values, values[1:]))


def ascending(values: list[float]) -> bool:
    return all(a <= b for a, b in zip(values, values[1:]))


def test_each_list_is_sorted_in_its_declared_direction(client, capsys) -> None:
    """Pairwise over the whole list, so a wrong tail is not hidden by a right head."""
    body = client.get("/movers").json()

    gainers = [row["day_change_pct"] for row in body["gainers"]]
    losers = [row["day_change_pct"] for row in body["losers"]]
    active = [row["session_volume"] for row in body["most_active"]]

    assert descending(gainers), f"gainers not descending: {gainers}"
    assert ascending(losers), f"losers not ascending: {losers}"
    assert descending(active), f"most active not descending: {active}"

    report(capsys, f"gainers {len(gainers)}, losers {len(losers)}, active {len(active)}")


def test_gainers_and_losers_are_disjoint(client) -> None:
    """One instrument cannot be in both ends of the same ranking."""
    body = client.get("/movers").json()
    assert not {row["symbol"] for row in body["gainers"]} & {
        row["symbol"] for row in body["losers"]
    }


def test_most_active_ranks_on_the_buffers_session_volume(client, state) -> None:
    """Read through `RingBuffer.session_volume`, not recomputed in the router."""
    for row in client.get("/movers").json()["most_active"]:
        expected = state.buffers[row["symbol"]].session_volume()
        assert row["session_volume"] == pytest.approx(expected)


def test_macro_returns_exactly_five_in_factor_order(client, capsys) -> None:
    """One per factor, in factor order, with the key strings on the wire."""
    body = client.get("/macro").json()

    assert len(body) == 5
    assert [row["factor"] for row in body] == list(FACTORS)
    for row in body:
        assert row["name"], f"{row['symbol']} has no name"

    report(capsys, f"macro order: {[row['factor'] for row in body]}")


def test_a_scenario_changes_the_membership_of_at_least_one_list(
    client, state, capsys
) -> None:
    """The demo's payoff, asserted where a browser is not needed to see it."""
    before = {
        name: {row["symbol"] for row in client.get("/movers").json()[name]}
        for name in ("gainers", "losers", "most_active")
    }

    library = load_scenarios()
    shock = next(
        scenario
        for scenario in library.values()
        if not scenario.is_baseline and "oil" in scenario.id
    )
    state.engine.activate(shock)
    for _ in range(60):
        state.engine.tick()

    after = {
        name: {row["symbol"] for row in client.get("/movers").json()[name]}
        for name in ("gainers", "losers", "most_active")
    }

    changed = [name for name in before if before[name] != after[name]]
    assert changed, f"{shock.id} moved no list's membership"

    report(
        capsys,
        f"{shock.id} changed {changed}; gainers "
        f"{sorted(before['gainers'])} -> {sorted(after['gainers'])}",
    )

    state.engine.deactivate()
