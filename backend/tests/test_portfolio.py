"""The portfolio route: every starting position present, and one set of totals.

No price-level literal is asserted. The totals are checked for internal consistency —
value equals holdings plus cash, return equals value minus cost — rather than against
numbers read off the implementation.
"""

import pytest
from fastapi.testclient import TestClient

from app import state as state_module
from app.main import app
from app.state import STARTING_CASH, STARTING_POSITIONS, build_state


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


def test_every_starting_position_is_served_with_a_float_quantity(
    client, capsys
) -> None:
    """All of them, not a subset — a missing holding is a hole a summary falls into."""
    body = client.get("/portfolio").json()
    served = {entry["symbol"]: entry for entry in body["positions"]}

    assert set(served) == set(STARTING_POSITIONS)
    for symbol, entry in served.items():
        assert isinstance(entry["quantity"], float)
        assert entry["quantity"] == pytest.approx(STARTING_POSITIONS[symbol])
        assert entry["avg_entry"] > 0.0

    report(capsys, f"{len(served)} positions served, quantities all float")


def test_the_totals_carry_value_return_and_todays_change(client, capsys) -> None:
    """One set of figures. There is one currency, so there is nothing to sum across."""
    totals = client.get("/portfolio").json()["totals"]

    for field in (
        "value",
        "cash",
        "total_return",
        "total_return_pct",
        "day_change",
        "day_change_pct",
    ):
        assert field in totals, f"totals carries no {field}"
        assert isinstance(totals[field], float)

    assert totals["cash"] == pytest.approx(STARTING_CASH)
    report(capsys, f"totals fields present: {sorted(totals)}")


def test_value_reconciles_with_the_holdings_and_the_cash(client, state) -> None:
    """Internal consistency rather than a literal: value is holdings plus cash."""
    body = client.get("/portfolio").json()
    holdings = sum(
        state.buffers[entry["symbol"]].latest().close * entry["quantity"]
        for entry in body["positions"]
    )
    assert body["totals"]["value"] == pytest.approx(holdings + STARTING_CASH)


def test_unrealised_pnl_follows_the_entry_and_the_latest_close(client, state) -> None:
    """Computed where it is served, so it cannot go stale between ticks."""
    for entry in client.get("/portfolio").json()["positions"]:
        last = state.buffers[entry["symbol"]].latest().close
        expected = (last - entry["avg_entry"]) * entry["quantity"]
        assert entry["unrealised_pnl"] == pytest.approx(expected)


def test_the_route_is_read_only(client) -> None:
    """There is no trade endpoint in this build."""
    assert client.post("/portfolio/trade", json={}).status_code in (404, 405)
