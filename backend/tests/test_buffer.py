"""`Bar`'s fields, the 5000-bar cap and the two session-relative queries.

Every expected value below is a literal computed by hand from the Definitions —
the eight field names, the five factor names, the cap of 5000, and the arithmetic
of `day change %` and *session volume* over the hand-built bars in this file. None
of them is read back off the implementation: a test that asks the code what it does
cannot fail when the code is wrong.

The arithmetic, shown once here so the literals below can be checked by eye:

* `FIRST_SESSION_BARS` are ticks 0-3. Session start is 0, so
  `day change % = (96.0 / 100.0 - 1) * 100 = -4.0` and
  `session volume = 10.0 + 20.0 + 30.0 + 40.0 = 100.0`.
* `BOUNDARY_BARS` are ticks 385-395, crossing the boundary at 390. With the latest
  bar at tick 395 the session start is 390, so
  `day change % = (55.0 / 50.0 - 1) * 100 = 10.0` and
  `session volume = 100.0 + 200.0 + 300.0 + 400.0 + 500.0 + 600.0 = 2100.0` — the
  150.0 of volume on ticks 385-389 belongs to the previous session and is excluded.
  Truncated at tick 390 the window is that one bar: `(50.0 / 50.0 - 1) * 100 = 0.0`
  and `100.0`. Truncated at tick 391 it is two: `(51.0 / 50.0 - 1) * 100 = 2.0` and
  `100.0 + 200.0 = 300.0`.

The field-set and attribution assertions are here because no session-window query
reads `contributions` or `residual` — the cap and the two queries would pass
unchanged against a `Bar` that carried neither, and both are what T25 stores O5's
reconciliation in and what T5 and T10 read back.

`pytest.approx` is used for the percentages only: 55.0 / 50.0 is not exact in binary
floating point, and asserting `10.0` to the bit would be a test of IEEE 754.
"""

from dataclasses import fields

import pytest

from app.buffer import CAPACITY, FACTORS, Bar, RingBuffer

# The five factors, written out rather than imported, so a rename in the module
# under test fails here instead of silently agreeing with itself.
THE_FIVE_FACTORS = ["market", "rates/duration", "oil", "USD", "credit spread"]

# One hand-picked attribution: five contributions and a residual, all literals.
# 0.0010 - 0.0004 + 0.0025 - 0.0006 + 0.0003 = 0.0028, and 0.0028 + 0.0007 = 0.0035.
ATTRIBUTION: dict[str, float] = {
    "market": 0.0010,
    "rates/duration": -0.0004,
    "oil": 0.0025,
    "USD": -0.0006,
    "credit spread": 0.0003,
}
RESIDUAL = 0.0007
CONTRIBUTIONS_SUM = 0.0028
LOG_RETURN = 0.0035


def bar(t: int, close: float, volume: float) -> Bar:
    """One hand-built bar. Only `t`, `close` and `volume` are read by the queries."""
    return Bar(
        t=t,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=volume,
        contributions=dict(ATTRIBUTION),
        residual=RESIDUAL,
    )


def buffer_of(bars: list[Bar]) -> RingBuffer:
    buffer = RingBuffer()
    for one in bars:
        buffer.append(one)
    return buffer


# Ticks 0-3: the first session, whose session start is tick 0.
FIRST_SESSION_BARS = [
    bar(0, 100.0, 10.0),
    bar(1, 102.0, 20.0),
    bar(2, 103.0, 30.0),
    bar(3, 96.0, 40.0),
]

# Ticks 385-395, crossing the session boundary at 390. Index 5 is tick 390.
BOUNDARY_BARS = [
    bar(385, 100.0, 10.0),
    bar(386, 101.0, 20.0),
    bar(387, 102.0, 30.0),
    bar(388, 103.0, 40.0),
    bar(389, 104.0, 50.0),
    bar(390, 50.0, 100.0),
    bar(391, 51.0, 200.0),
    bar(392, 52.0, 300.0),
    bar(393, 53.0, 400.0),
    bar(394, 54.0, 500.0),
    bar(395, 55.0, 600.0),
]


# ── Bar: the eight fields, the five factor keys, the attribution ────────────


def test_bar_carries_exactly_the_eight_stated_fields() -> None:
    assert {field.name for field in fields(Bar)} == {
        "t",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "contributions",
        "residual",
    }


def test_the_five_factor_names_are_exactly_the_five() -> None:
    assert list(FACTORS) == THE_FIVE_FACTORS


def test_bar_contributions_hold_one_entry_per_factor() -> None:
    one = bar(390, 50.0, 100.0)

    assert list(one.contributions) == THE_FIVE_FACTORS
    assert len(one.contributions) == 5


def test_bar_stores_the_attribution_it_was_given() -> None:
    one = bar(390, 50.0, 100.0)

    assert one.contributions["market"] == 0.0010
    assert one.contributions["rates/duration"] == -0.0004
    assert one.contributions["oil"] == 0.0025
    assert one.contributions["USD"] == -0.0006
    assert one.contributions["credit spread"] == 0.0003
    assert one.residual == 0.0007
    # O5's reconciliation is stored, not recomputed: the parts are still here to add.
    assert sum(one.contributions.values()) == pytest.approx(CONTRIBUTIONS_SUM, abs=1e-12)
    assert sum(one.contributions.values()) + one.residual == pytest.approx(
        LOG_RETURN, abs=1e-12
    )


@pytest.mark.parametrize(
    ("contributions", "case"),
    [
        (
            {
                "market": 0.0010,
                "rates/duration": -0.0004,
                "oil": 0.0025,
                "USD": -0.0006,
            },
            "one factor missing",
        ),
        (
            {
                "market": 0.0010,
                "rates/duration": -0.0004,
                "oil": 0.0025,
                "USD": -0.0006,
                "credit spread": 0.0003,
                "momentum": 0.0001,
            },
            "a sixth key that is not a factor",
        ),
        ({}, "no entries at all"),
    ],
    ids=["missing-factor", "extra-key", "empty"],
)
def test_bar_rejects_contributions_that_are_not_exactly_the_five_factors(
    contributions: dict[str, float], case: str
) -> None:
    with pytest.raises(ValueError):
        Bar(
            t=390,
            open=50.0,
            high=50.0,
            low=50.0,
            close=50.0,
            volume=100.0,
            contributions=contributions,
            residual=RESIDUAL,
        )


def test_bar_cannot_be_constructed_without_contributions() -> None:
    with pytest.raises(TypeError) as excinfo:
        Bar(  # type: ignore[call-arg]
            t=390,
            open=50.0,
            high=50.0,
            low=50.0,
            close=50.0,
            volume=100.0,
            residual=RESIDUAL,
        )

    assert "contributions" in str(excinfo.value)


def test_bar_cannot_be_constructed_without_residual() -> None:
    with pytest.raises(TypeError) as excinfo:
        Bar(  # type: ignore[call-arg]
            t=390,
            open=50.0,
            high=50.0,
            low=50.0,
            close=50.0,
            volume=100.0,
            contributions=dict(ATTRIBUTION),
        )

    assert "residual" in str(excinfo.value)


# ── The cap and the eviction order, both sides of the boundary ─────────────


def test_the_cap_is_five_thousand() -> None:
    assert CAPACITY == 5000


def test_one_short_of_the_cap_keeps_every_bar() -> None:
    buffer = buffer_of([bar(tick, 100.0, 1.0) for tick in range(4999)])

    assert len(buffer) == 4999
    assert buffer.bars()[0].t == 0
    assert buffer.latest().t == 4998


def test_at_the_cap_nothing_is_evicted() -> None:
    buffer = buffer_of([bar(tick, 100.0, 1.0) for tick in range(5000)])

    assert len(buffer) == 5000
    assert buffer.bars()[0].t == 0
    assert buffer.latest().t == 4999


def test_one_past_the_cap_evicts_the_oldest_bar() -> None:
    buffer = buffer_of([bar(tick, 100.0, 1.0) for tick in range(5001)])

    assert len(buffer) == 5000
    assert buffer.bars()[0].t == 1
    assert buffer.latest().t == 5000
    assert 0 not in [one.t for one in buffer.bars()]


def test_eviction_is_oldest_first_and_order_is_preserved() -> None:
    buffer = buffer_of([bar(tick, 100.0, 1.0) for tick in range(5005)])
    ticks = [one.t for one in buffer.bars()]

    assert len(buffer) == 5000
    assert ticks[:5] == [5, 6, 7, 8, 9]
    assert ticks[-1] == 5004
    assert ticks == list(range(5, 5005))


# ── The session queries across a tick-390 boundary ────────────────────────


def test_day_change_pct_across_the_session_boundary() -> None:
    buffer = buffer_of(BOUNDARY_BARS)

    # (55.0 / 50.0 - 1) * 100. Off tick 385's close of 100.0 it would be -45.0.
    assert buffer.day_change_pct() == pytest.approx(10.0, abs=1e-9)


def test_session_volume_across_the_session_boundary() -> None:
    buffer = buffer_of(BOUNDARY_BARS)

    # The fixture carries 2250.0 in all; ticks 385-389 hold 150.0 of it and are
    # the previous session, so the window is the remaining 2100.0.
    assert sum(one.volume for one in BOUNDARY_BARS) == 2250.0
    assert buffer.session_volume() == 2100.0


def test_at_the_session_start_tick_the_window_is_that_bar_alone() -> None:
    buffer = buffer_of(BOUNDARY_BARS[:6])

    assert buffer.latest().t == 390
    assert buffer.day_change_pct() == pytest.approx(0.0, abs=1e-9)
    assert buffer.session_volume() == 100.0


def test_one_tick_past_the_session_start_the_window_is_two_bars() -> None:
    buffer = buffer_of(BOUNDARY_BARS[:7])

    assert buffer.latest().t == 391
    assert buffer.day_change_pct() == pytest.approx(2.0, abs=1e-9)
    assert buffer.session_volume() == 300.0


def test_the_first_session_reads_from_tick_zero() -> None:
    buffer = buffer_of(FIRST_SESSION_BARS)

    assert buffer.day_change_pct() == pytest.approx(-4.0, abs=1e-9)
    assert buffer.session_volume() == 100.0


def test_a_session_figure_is_not_invented_where_the_definitions_do_not_reach() -> None:
    """Two cases the Definitions leave undetermined; reported, not chosen.

    Neither arises under the 780-tick backfill or under eviction at the 5000-bar
    cap. Until they are settled, both refuse rather than return a number: an empty
    buffer has no latest bar, and a buffer whose oldest bar falls after the session
    start has no close *at* the session start to divide by.
    """
    with pytest.raises(ValueError):
        RingBuffer().day_change_pct()

    with pytest.raises(ValueError):
        RingBuffer().session_volume()

    # Ticks 385-389: the latest is 389, so the session start is tick 0 — absent.
    short = buffer_of(BOUNDARY_BARS[:5])
    assert short.latest().t == 389
    with pytest.raises(ValueError):
        short.day_change_pct()
