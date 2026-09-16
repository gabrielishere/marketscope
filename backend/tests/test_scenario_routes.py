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
    """O6, over every bar of every instrument rather than a sample."""
    before = snapshot(state)
    bars_compared = sum(len(series) for series in before.values())

    response = client.post("/scenario", json={"id": a_non_baseline_id()})
    assert response.status_code == 200

    after = snapshot(state)
    assert after == before, "activation rewrote history"

    activated_at = response.json()["activated_at"]
    assert activated_at == state.tick_index, "stamped at the next bar to be written"

    # And the history genuinely diverges afterwards, so the comparison above is not
    # passing because nothing is happening.
    state.engine.tick()
    assert snapshot(state) != before

    report(
        capsys,
        f"{bars_compared} bars identical across activation at tick {activated_at}",
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
