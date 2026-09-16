"""The scenario routes, and the guarantee that activation never rewrites history.

The snapshot comparison covers **every bar of every instrument**, not a sample. O6 says
bars before `activated_at` are byte-identical after the POST, and a sampled check would
pass against an engine that rewrote the bars it did not look at.
"""

import pytest
from fastapi.testclient import TestClient

from app import state as state_module
from app.main import app
from app.scenarios import BASELINE_ID, load_scenarios
from app.state import build_state


def report(capsys, message: str) -> None:
    with capsys.disabled():
        print(f"\n    {message}")


@pytest.fixture
def state():
    """Fresh per test: these mutate the active scenario."""
    return build_state()


@pytest.fixture
def client(state):
    state_module._state = state
    with TestClient(app) as test_client:
        yield test_client
    state_module._state = None


def snapshot(state) -> dict[str, tuple]:
    """Every bar of every instrument, as comparable tuples."""
    return {
        symbol: tuple(
            (bar.t, bar.open, bar.high, bar.low, bar.close, bar.volume,
             tuple(sorted(bar.contributions.items())), bar.residual)
            for bar in buffer.bars()
        )
        for symbol, buffer in state.buffers.items()
    }


def a_non_baseline_id() -> str:
    return next(one for one in load_scenarios() if one != BASELINE_ID)


def test_scenarios_lists_every_id_the_library_holds(client, capsys) -> None:
    """The dropdown is populated from here, so a missing entry is an absent option."""
    body = client.get("/scenarios").json()
    served = [entry["id"] for entry in body]

    assert set(served) == set(load_scenarios())
    assert served[0] == BASELINE_ID, "the baseline is first, as the file writes it"
    for entry in body:
        assert entry["name"] and entry["description"]

    report(capsys, f"library served: {served}")


def test_active_scenario_carries_the_headlines(client, capsys) -> None:
    """The half of O21 this task owns: the ticker reads them from here."""
    body = client.get("/scenario").json()

    assert body["id"] == BASELINE_ID
    assert body["activated_at"] is None
    assert 2 <= len(body["headlines"]) <= 3, "baseline carries headlines like any other"

    report(capsys, f"baseline headlines: {len(body['headlines'])}")


def test_activation_leaves_every_prior_bar_byte_identical(
    client, state, capsys
) -> None:
    """O6, over every bar of every instrument rather than a sample.

    The claim is about **bars before `activated_at`**, not about the whole buffer. The
    handler ticks before responding — so that the prices have actually moved by the time a
    client refreshes — which appends one bar at `activated_at` carrying the shock. That bar
    is the activation working; the guarantee is that nothing *earlier* than it moved.
    """
    before = snapshot(state)

    response = client.post("/scenario", json={"id": a_non_baseline_id()})
    assert response.status_code == 200
    activated_at = response.json()["activated_at"]

    after = snapshot(state)
    prior = {
        symbol: tuple(bar for bar in series if bar[0] < activated_at)
        for symbol, series in after.items()
    }
    assert prior == before, "activation rewrote history before activated_at"
    bars_compared = sum(len(series) for series in before.values())

    # The activation bar exists and is new, so the comparison above is not passing
    # because nothing happened.
    appended = {
        symbol: [bar for bar in series if bar[0] >= activated_at]
        for symbol, series in after.items()
    }
    assert all(len(bars) == 1 for bars in appended.values()), (
        "activation should append exactly one bar per instrument"
    )

    report(
        capsys,
        f"{bars_compared} bars before tick {activated_at} identical across activation; "
        f"one bar appended per instrument",
    )


def test_activation_moves_prices_before_it_responds(client, state, capsys) -> None:
    """The response reports a state that is already true, not one that is coming.

    `activate()` stamps the *next* bar's index, so without a tick inside the handler the
    POST would return success while every price was still the old one. A client refreshing
    on the response — which is what the scenario selector does — would then fetch stale
    quotes and show nothing happening until the next scheduled poll.
    """
    oil = next(one for one in load_scenarios() if "oil" in one)
    before = {s: b.latest().close for s, b in state.buffers.items()}

    client.post("/scenario", json={"id": oil})

    after = {s: b.latest().close for s, b in state.buffers.items()}
    moved = [s for s in before if after[s] != before[s]]
    assert len(moved) == len(before), (
        f"only {len(moved)} of {len(before)} instruments repriced; the handler returned "
        "before the shock was written to a bar"
    )

    oil_exposed = [
        s for s, i in state.instruments.items() if i.betas["oil"] > 0 and not i.is_macro_driver
    ]
    lifted = [s for s in oil_exposed if after[s] > before[s]]
    assert lifted, "no oil-exposed instrument rose on activation"

    report(
        capsys,
        f"activation repriced all {len(moved)} instruments in the response; "
        f"{len(lifted)}/{len(oil_exposed)} oil-exposed names rose",
    )


def test_delete_returns_to_baseline_and_clears_activated_at(client) -> None:
    """Going back to normal changes what happens next; it does not undo the past."""
    client.post("/scenario", json={"id": a_non_baseline_id()})
    assert client.get("/scenario").json()["activated_at"] is not None

    body = client.delete("/scenario").json()
    assert body["id"] == BASELINE_ID
    assert body["activated_at"] is None


def test_an_unknown_scenario_id_is_rejected_with_422(client) -> None:
    """Typed to the generated enum, so the rejection precedes the handler."""
    assert client.post("/scenario", json={"id": "no_such_scenario"}).status_code == 422
