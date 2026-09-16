"""The tick engine's three outcome clauses: one bar per instrument per tick, strict
positivity over 1200 ticks under every scenario, and attribution that reconciles to 1e-6.

**No price-level literal is asserted anywhere in this file.** A fixed seed makes the
engine's prices reproducible, but the only place such a literal could be read off is the
implementation itself, and a test taking its expected value from the code under test
cannot fail. Price behaviour is asserted as properties instead: every price strictly
greater than zero, and `sum(contributions.values()) + residual` equal to
`log(close / previous_close)` to within the 1e-6 the outcome states.

The literals that *are* here come from the specification, not from the engine: the five
factor keys, the library size of 6 or 7 scenarios, the 1200 ticks, the 1e-6 tolerance,
and the bar counts 1 and 2 after one and two ticks.

Counts and extremes are printed through `capsys.disabled()` rather than a bare `print`,
because pytest captures stdout on a passing test. Without them a run that quietly
covered zero scenarios and one that covered seven would produce the same green line.
"""

from math import log

import pytest

from app.instruments import load_instruments
from app.scenarios import load_scenarios
from app.sim import Engine

# The five factor keys, written out rather than imported from the module under test, so
# a rename there fails here instead of silently agreeing with itself. Identifier-style:
# these are the keys, not the prose names of the factors.
THE_FIVE_FACTORS = ["market", "rates", "oil", "usd", "credit"]

# From the spec's Constraints: "The library holds 6 or 7 scenarios." A positivity test
# that iterated an empty library would otherwise pass having asserted nothing.
MIN_LIBRARY_SIZE = 6
MAX_LIBRARY_SIZE = 7

# From the outcome: positivity holds over a run of at least 1200 ticks.
POSITIVITY_TICKS = 1200

# From the outcome: the reconciliation tolerance. Not tightened, not widened.
RECONCILIATION_TOLERANCE = 1e-6

# Ticks per scenario for the reconciliation sweep. Long enough to cover the activation
# tick, the decay that follows it and a stretch of ordinary drift.
RECONCILIATION_TICKS = 200

# Any fixed seed. Nothing is asserted about which one it is; it is fixed so that a
# failure here is reproducible.
SEED = 20240917


def report(capsys: pytest.CaptureFixture[str], message: str) -> None:
    """Print past pytest's capture, so a passing test still says what it covered."""
    with capsys.disabled():
        print(f"\n    {message}")


def test_one_tick_appends_exactly_one_bar_to_every_instrument(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """One `tick()` call appends one bar per instrument — no more, and none skipped."""
    universe = load_instruments()
    engine = Engine(seed=SEED)

    assert set(engine.buffers) == set(universe)
    assert all(len(buffer) == 0 for buffer in engine.buffers.values())

    engine.tick()
    depths_after_one = {symbol: len(buffer) for symbol, buffer in engine.buffers.items()}
    assert depths_after_one == {symbol: 1 for symbol in universe}

    engine.tick()
    depths_after_two = {symbol: len(buffer) for symbol, buffer in engine.buffers.items()}
    assert depths_after_two == {symbol: 2 for symbol in universe}

    # The two bars are consecutive ticks starting at index 0, so the history a session
    # query reads has no gap and no repeat.
    for symbol in universe:
        assert [bar.t for bar in engine.buffers[symbol].bars()] == [0, 1]

    report(
        capsys,
        f"instruments: {len(universe)}; bars each after one tick: 1; after two: 2",
    )


def test_prices_are_strictly_positive_over_1200_ticks_under_every_scenario(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every price, under every scenario in the library, over 1200 ticks, exceeds zero.

    The count of scenarios covered and the smallest price seen across all of them are
    reported, so a run that covered none is distinguishable from one that covered seven.
    """
    library = load_scenarios()
    assert MIN_LIBRARY_SIZE <= len(library) <= MAX_LIBRARY_SIZE

    minimum_price = None
    minimum_where = ""
    prices_checked = 0

    for scenario_id, scenario in library.items():
        engine = Engine(seed=SEED)
        engine.activate(scenario)
        for _ in range(POSITIVITY_TICKS):
            engine.tick()
        for symbol, buffer in engine.buffers.items():
            assert len(buffer) == POSITIVITY_TICKS
            for bar in buffer.bars():
                assert bar.open > 0.0
                assert bar.high > 0.0
                assert bar.low > 0.0
                assert bar.close > 0.0
                prices_checked += 4
                if minimum_price is None or bar.low < minimum_price:
                    minimum_price = bar.low
                    minimum_where = f"{symbol} at tick {bar.t} under {scenario_id}"

    assert minimum_price is not None
    assert minimum_price > 0.0
    report(
        capsys,
        f"scenarios run: {len(library)}; ticks each: {POSITIVITY_TICKS}; "
        f"prices checked: {prices_checked}; minimum price observed: "
        f"{minimum_price!r} ({minimum_where})",
    )


def test_contributions_plus_residual_equal_the_log_return_to_1e_6(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`sum(contributions.values()) + residual` equals `log(close / previous_close)`.

    Checked on every consecutive pair of bars, for every instrument, under every
    scenario in the library — baseline included, where the factors move on noise alone.
    The worst discrepancy seen is reported.
    """
    library = load_scenarios()
    assert MIN_LIBRARY_SIZE <= len(library) <= MAX_LIBRARY_SIZE

    worst_discrepancy = 0.0
    worst_where = "nothing compared"
    comparisons = 0

    for scenario_id, scenario in library.items():
        engine = Engine(seed=SEED)
        engine.activate(scenario)
        for _ in range(RECONCILIATION_TICKS):
            engine.tick()
        for symbol, buffer in engine.buffers.items():
            bars = buffer.bars()
            assert len(bars) == RECONCILIATION_TICKS
            for previous, bar in zip(bars, bars[1:]):
                assert sorted(bar.contributions) == sorted(THE_FIVE_FACTORS)
                attributed = sum(bar.contributions.values()) + bar.residual
                realised = log(bar.close / previous.close)
                discrepancy = abs(attributed - realised)
                assert discrepancy <= RECONCILIATION_TOLERANCE
                comparisons += 1
                if discrepancy > worst_discrepancy:
                    worst_discrepancy = discrepancy
                    worst_where = f"{symbol} at tick {bar.t} under {scenario_id}"

    assert comparisons > 0
    report(
        capsys,
        f"scenarios run: {len(library)}; reconciliations checked: {comparisons}; "
        f"tolerance: {RECONCILIATION_TOLERANCE}; worst discrepancy: "
        f"{worst_discrepancy!r} ({worst_where})",
    )


def test_a_discrepancy_beyond_the_tolerance_would_fail() -> None:
    """The reconciliation check above can fail — it is not vacuously satisfied.

    A stored residual perturbed by twice the tolerance breaks the equality the previous
    test asserts. Without this, a comparison that always reported zero would be
    indistinguishable from one that was genuinely exact.
    """
    engine = Engine(seed=SEED)
    engine.tick()
    engine.tick()
    previous, bar = engine.buffers["AAPL"].bars()

    realised = log(bar.close / previous.close)
    attributed = sum(bar.contributions.values()) + bar.residual
    perturbed = attributed + 2 * RECONCILIATION_TOLERANCE

    assert abs(attributed - realised) <= RECONCILIATION_TOLERANCE
    assert abs(perturbed - realised) > RECONCILIATION_TOLERANCE


def test_the_same_seed_gives_the_same_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Two engines on one seed hold identical histories, so a rehearsal and the demo
    look the same.

    Compared bar for bar between two independent runs — neither side is an expected
    value taken from the implementation.
    """
    scenario = load_scenarios()["oil_supply_shock"]
    histories = []
    for _ in range(2):
        engine = Engine(seed=SEED)
        engine.activate(scenario)
        for _ in range(50):
            engine.tick()
        histories.append(
            {symbol: buffer.bars() for symbol, buffer in engine.buffers.items()}
        )

    first, second = histories
    assert set(first) == set(second)
    assert first == second

    bars_compared = sum(len(bars) for bars in first.values())
    assert bars_compared > 0
    report(capsys, f"bars compared between two runs on seed {SEED}: {bars_compared}")


def test_switching_scenarios_unwinds_the_one_it_replaces(capsys) -> None:
    """A scenario's price effect is not permanently baked in when another replaces it.

    The engine tracks the shock level currently *applied to the prices*, so a tick moves
    that level toward whatever the active scenario asks for. Activation, decay, a switch
    and a return to baseline are then the same operation, and none of them strands a
    level nobody is decaying any more.

    Without this, flipping between scenarios in a demo ratchets prices in one direction
    and every day-change figure stops meaning anything.
    """
    library = load_scenarios()
    shock = next(one for one in library.values() if one.id == "oil_supply_shock")

    engine = Engine(seed=7)
    for _ in range(20):
        engine.tick()
    before = engine.prices["XOM"]

    engine.activate(shock)
    engine.tick()
    lifted = engine.prices["XOM"]
    assert lifted > before * 1.03, "the oil shock did not lift an oil-exposed name"

    # Back to baseline: the shock's level must come out of the prices, not linger.
    engine.deactivate()
    engine.tick()
    unwound = engine.prices["XOM"]

    lift = (lifted / before - 1) * 100
    residue = (unwound / before - 1) * 100
    assert abs(residue) < abs(lift) / 2, (
        f"the shock lifted XOM {lift:+.2f}% and {residue:+.2f}% was still there after "
        "returning to baseline; the outgoing level was never unwound"
    )

    report(
        capsys,
        f"oil shock lifted XOM {lift:+.2f}%; after baseline {residue:+.2f}% remains",
    )
