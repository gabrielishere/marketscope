"""The in-process state's outcome clauses: a 780-bar backfill starting at tick index 0,
a fixed non-empty portfolio identical across two builds, a baseline active scenario, and
one `advance_once` call appending exactly one bar to every instrument.

**No price-level literal is asserted here.** The seed is fixed and the prices are
therefore reproducible, but the only place such a literal could be read off is the
implementation itself, and a test taking its expected value from the code under test
cannot fail. What is asserted instead is structure: bar counts, tick indices, symbol
sets, and two independent builds compared against each other rather than against a
number copied out of the engine.

The literals that *are* here come from the specification: 780 backfilled ticks, tick
index 0 as the first bar held, 390 ticks to a session, `baseline` as the resting
scenario id, and the bar count rising by exactly 1 per `advance_once`.

Counts are printed through `capsys.disabled()`, as the sibling suites do, because
pytest captures stdout on a passing test. Without them a comparison of two empty states
and a comparison of two full ones produce the same green line.
"""

import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from app import main
from app import state as state_module
from app.instruments import load_instruments
from app.scenarios import BASELINE_ID
from app.state import (
    BACKFILL_TICKS,
    SEED,
    SESSION_TICKS,
    STARTING_CASH,
    STARTING_POSITIONS,
    advance_once,
    build_state,
)

# From the spec: "Startup backfills 780 ticks", which at 390 ticks to a session is
# exactly two prior sessions. Written out rather than imported from the module under
# test, so a change there fails here instead of silently agreeing with itself.
EXPECTED_BACKFILL_TICKS = 780
EXPECTED_SESSION_TICKS = 390

# From the outcome: "the first at tick index 0". `RingBuffer.day_change_pct` raises
# when the bar at session start is not held, and any other starting index makes that
# reachable on the first session.
FIRST_TICK_INDEX = 0

# From the Definitions: the id of the scenario the application rests at.
EXPECTED_BASELINE_ID = "baseline"

# From the outcome: one `advance_once` call raises every instrument's bar count by
# exactly one.
BARS_PER_ADVANCE = 1


def report(capsys: pytest.CaptureFixture[str], message: str) -> None:
    """Print past pytest's capture, so a passing test still says what it covered."""
    with capsys.disabled():
        print(f"\n    {message}")


def test_the_backfill_is_780_bars_per_instrument_starting_at_tick_0(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every instrument holds exactly 780 bars, the earliest at tick index 0.

    Asserted per instrument, not in aggregate: an instrument added to the universe
    after the engine was built, or one that started short, would leave the total
    plausible while one history was empty.
    """
    universe = load_instruments()
    state = build_state()

    assert EXPECTED_SESSION_TICKS == SESSION_TICKS
    assert EXPECTED_BACKFILL_TICKS == BACKFILL_TICKS
    # Two prior sessions, so a session boundary sits behind the latest bar.
    assert EXPECTED_BACKFILL_TICKS == 2 * EXPECTED_SESSION_TICKS

    assert len(universe) > 0
    assert set(state.buffers) == set(universe)

    depths = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}
    assert depths == {symbol: EXPECTED_BACKFILL_TICKS for symbol in universe}

    for symbol in universe:
        bars = state.buffers[symbol].bars()
        assert bars[0].t == FIRST_TICK_INDEX
        assert bars[-1].t == EXPECTED_BACKFILL_TICKS - 1
        # No gap and no repeat between the two: the history is one bar per tick.
        assert [bar.t for bar in bars] == list(range(EXPECTED_BACKFILL_TICKS))

    report(
        capsys,
        f"instruments backfilled: {len(universe)}; bars each: "
        f"{EXPECTED_BACKFILL_TICKS}; first tick index held: {FIRST_TICK_INDEX}; "
        f"last: {EXPECTED_BACKFILL_TICKS - 1}",
    )


def test_day_change_is_defined_on_the_backfilled_history(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The session-start bar is held, so `day_change_pct` returns rather than raising.

    This is the reason the backfill starts at tick index 0 and not at an arbitrary
    index. The figure itself is not asserted — no price literal — only that every
    instrument has one.
    """
    state = build_state()
    session_start = (BACKFILL_TICKS - 1) - (BACKFILL_TICKS - 1) % EXPECTED_SESSION_TICKS

    computed = 0
    for buffer in state.buffers.values():
        assert isinstance(buffer.day_change_pct(), float)
        assert any(bar.t == session_start for bar in buffer.bars())
        computed += 1

    assert computed == len(state.buffers)
    report(
        capsys,
        f"day change % computed for {computed} instruments against session start "
        f"tick {session_start}",
    )


def test_two_build_state_calls_compare_equal_bar_for_bar_and_position_for_position(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Two builds on the fixed seed hold the same history and the same portfolio.

    Neither side is an expected value taken from the implementation: two independent
    builds are compared against each other. The counts of bars and of positions
    actually compared are reported, so a run comparing two empty states is
    distinguishable from one comparing two full ones.
    """
    first = build_state()
    second = build_state()

    first_bars = {symbol: buffer.bars() for symbol, buffer in first.buffers.items()}
    second_bars = {symbol: buffer.bars() for symbol, buffer in second.buffers.items()}

    assert set(first_bars) == set(second_bars)

    bars_compared = 0
    for symbol in first_bars:
        left, right = first_bars[symbol], second_bars[symbol]
        assert len(left) == len(right) == EXPECTED_BACKFILL_TICKS
        for left_bar, right_bar in zip(left, right):
            assert left_bar == right_bar
            bars_compared += 1

    assert set(first.positions) == set(second.positions)
    positions_compared = 0
    for symbol in first.positions:
        assert first.positions[symbol] == second.positions[symbol]
        positions_compared += 1

    # A comparison of two empty states would pass every equality above. These make the
    # depth of what was compared part of the assertion rather than part of the prose.
    assert bars_compared == EXPECTED_BACKFILL_TICKS * len(first_bars)
    assert bars_compared > 0
    assert positions_compared == len(STARTING_POSITIONS)
    assert positions_compared > 0

    assert first.cash == second.cash == STARTING_CASH

    report(
        capsys,
        f"seed {SEED}: compared {bars_compared} bars and {positions_compared} "
        f"positions between two build_state() calls; cash {first.cash} both sides",
    )


def test_the_starting_portfolio_is_fixed_non_empty_and_in_the_universe(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every position names a real instrument, carries a float quantity, and is held."""
    universe = load_instruments()
    state = build_state()

    assert len(STARTING_POSITIONS) > 0
    assert set(state.positions) == set(STARTING_POSITIONS)

    for symbol, holding in state.positions.items():
        assert symbol in universe
        assert holding.symbol == symbol
        # A float, never an integer, per Constraints.
        assert isinstance(holding.quantity, float)
        assert not isinstance(holding.quantity, int)
        assert holding.quantity > 0.0
        assert isinstance(holding.avg_entry, float)
        assert holding.avg_entry > 0.0

    assert state.cash == STARTING_CASH

    report(
        capsys,
        f"positions held: {len(state.positions)} "
        f"({', '.join(sorted(state.positions))}); cash {state.cash}",
    )


def test_a_position_in_an_instrument_outside_the_universe_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The other side of the boundary the previous test asserts.

    Without this, `STARTING_POSITIONS` naming a symbol the universe does not hold would
    leave the state silently holding a position in nothing, and the suite above would
    still be green for every symbol that did exist.
    """
    unknown = "NOSUCHSYMBOL"
    assert unknown not in load_instruments()

    monkeypatch.setattr(
        state_module,
        "STARTING_POSITIONS",
        {**STARTING_POSITIONS, unknown: 10.0},
    )
    with pytest.raises(ValueError) as failure:
        build_state()
    assert unknown in str(failure.value)


def test_the_active_scenario_is_baseline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The process rests at baseline: nothing shocked, nothing drifting, nothing
    stamped as activated."""
    state = build_state()

    assert BASELINE_ID == EXPECTED_BASELINE_ID
    assert state.scenario.id == EXPECTED_BASELINE_ID
    assert state.scenario.is_baseline
    assert state.scenario.named_factors == ()
    for shock in state.scenario.factors.values():
        assert shock.shock == 0.0
        assert shock.drift == 0.0
    assert state.activated_at is None

    report(
        capsys,
        f"active scenario: {state.scenario.id!r}; activated_at: {state.activated_at}; "
        f"factors moved: {len(state.scenario.named_factors)}",
    )


def test_advance_once_appends_exactly_one_bar_to_every_instrument(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """One call, one bar per instrument — and a second call, one more.

    This is the same function the background task calls once a second, so the loop's
    behaviour is asserted here.
    """
    state = build_state()
    before = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}
    assert len(before) > 0

    advance_once(state)
    after_one = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}
    assert after_one == {
        symbol: depth + BARS_PER_ADVANCE for symbol, depth in before.items()
    }

    advance_once(state)
    after_two = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}
    assert after_two == {
        symbol: depth + 2 * BARS_PER_ADVANCE for symbol, depth in before.items()
    }

    # The appended bars continue the backfill's tick indices rather than restarting.
    for buffer in state.buffers.values():
        assert [bar.t for bar in buffer.bars()[-2:]] == [
            EXPECTED_BACKFILL_TICKS,
            EXPECTED_BACKFILL_TICKS + 1,
        ]

    report(
        capsys,
        f"instruments advanced: {len(before)}; bars each before: "
        f"{EXPECTED_BACKFILL_TICKS}; after one advance_once: "
        f"{EXPECTED_BACKFILL_TICKS + 1}; after two: {EXPECTED_BACKFILL_TICKS + 2}",
    )


def test_the_lifespans_background_task_advances_the_state(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The lifespan really runs the clock: entering it advances every instrument.

    The interval is shortened so the test does not wait seconds of wall time; what is
    asserted is that the task ticks at all and that every instrument advances by the
    same number of bars, which is what `advance_once` being its whole body means.
    """
    monkeypatch.setattr(main, "TICK_SECONDS", 0.01)
    state = build_state()
    monkeypatch.setattr(state_module, "_state", state)

    before = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}

    async def run_lifespan() -> None:
        async with main.lifespan(main.app):
            await asyncio.sleep(0.2)

    asyncio.run(run_lifespan())

    after = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}
    advances = {after[symbol] - before[symbol] for symbol in before}
    assert len(advances) == 1
    (advanced,) = advances
    assert advanced >= BARS_PER_ADVANCE

    report(
        capsys,
        f"lifespan run: {len(before)} instruments advanced by {advanced} bars each",
    )


def test_the_application_runs_the_clock(capsys, monkeypatch) -> None:
    """O1's other half: that *the app* advances the market, not just that a loop would.

    Asserted by entering the application's own lifespan through `TestClient` and
    watching the bars grow. A static check cannot do this job: FastAPI installs
    `_DefaultLifespan` when no `lifespan=` is passed, which is truthy, and once routers
    are included **both** the attached and the unattached case become merged wrapper
    functions — so neither truthiness, nor identity against `lifespan`, nor an
    `isinstance` against `_DefaultLifespan` tells the two apart.

    What does tell them apart is whether the clock runs. Drop `lifespan=` from the
    `FastAPI(...)` call and this test fails; nothing else in the suite would.
    """
    monkeypatch.setattr(main, "TICK_SECONDS", 0.01)
    state = build_state()
    monkeypatch.setattr(state_module, "_state", state)

    before = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}
    with TestClient(main.app):
        time.sleep(0.2)
    after = {symbol: len(buffer) for symbol, buffer in state.buffers.items()}

    advances = {after[symbol] - before[symbol] for symbol in before}
    assert len(advances) == 1, "instruments advanced by differing amounts"
    (advanced,) = advances
    assert advanced >= 1, (
        "the application served a request window without advancing the market; "
        "lifespan is not attached to the app"
    )

    report(
        capsys,
        f"the app's own lifespan advanced {len(before)} instruments by {advanced} bars",
    )


def test_tick_seconds_is_one_second() -> None:
    """One tick is one second of wall time, so the loop's interval is 1."""
    assert main.TICK_SECONDS == 1
