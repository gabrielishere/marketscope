"""The `Bar` record, the bounded per-instrument ring buffer and its session queries.

This module is the bottom of the stack. It imports nothing from the rest of the
project — not the engine, not the state, not the instrument universe — so that the
capacity rule and the two session-relative queries stand on their own commit and a
failure in the engine's maths leaves them standing.

`day_change_pct` and `session_volume` live here, once, because every surface that
displays or ranks by either reads through this buffer: the quote set, the movers
endpoint, the portfolio totals and the frontend's tables. A second definition
computed at a route would be a second answer with nothing marking which is right.

Two boundary cases are *not* settled by the definitions this module implements, and
both raise rather than return an invented figure:

* an empty buffer — there is no latest bar, so neither query has a window; and
* a buffer whose oldest bar falls after the current session start — the definition
  of `day change %` names the close *at* the session start tick, and that bar is not
  there to read.

Neither arises under the 780-tick backfill from tick 0, which leaves two whole prior
sessions behind the latest bar, and neither can be created by eviction: the cap of
5000 bars is nearly thirteen sessions, so the session start is always still in the
buffer when it is full.
"""

from collections import deque
from dataclasses import dataclass

#: The five factors, in factor order. The only thing this module takes from outside
#: it, written out as literals rather than imported, because it depends on no other
#: module in the project.
FACTORS: tuple[str, str, str, str, str] = (
    "market",
    "rates/duration",
    "oil",
    "USD",
    "credit spread",
)

#: One tick is one minute; a session is 390 ticks — a 6.5-hour trading day.
SESSION_TICKS = 390

#: Bars kept per instrument. Fixed, not a constructor argument: one cap for the
#: whole process, so no caller can shorten a history another surface reads.
CAPACITY = 5000


def session_start_tick(tick: int) -> int:
    """The most recent tick index that is a multiple of 390, at or before `tick`."""
    return tick - tick % SESSION_TICKS


@dataclass(frozen=True, slots=True)
class Bar:
    """One minute of one instrument, with the tick's attribution stored alongside it.

    `contributions` holds exactly one entry per factor and `residual` the
    idiosyncratic term, so that `sum(contributions.values()) + residual` reconciles
    with `log(close / previous_close)`. They are written here, at the tick, because
    nothing downstream can recover them from the price alone.
    """

    t: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    contributions: dict[str, float]
    residual: float

    def __post_init__(self) -> None:
        if set(self.contributions) != set(FACTORS):
            raise ValueError(
                "Bar.contributions must hold exactly one entry per factor, keyed by "
                f"{list(FACTORS)}; got {sorted(self.contributions)}."
            )


class RingBuffer:
    """A bounded history for one instrument: 5000 bars, oldest discarded first."""

    __slots__ = ("_bars",)

    def __init__(self) -> None:
        # maxlen is the capacity rule: a full deque drops from the left on append.
        self._bars: deque[Bar] = deque(maxlen=CAPACITY)

    def __len__(self) -> int:
        return len(self._bars)

    def append(self, bar: Bar) -> None:
        """Append one bar, evicting the oldest when the buffer is already at 5000."""
        self._bars.append(bar)

    def bars(self) -> tuple[Bar, ...]:
        """Every bar held, oldest first and the latest last."""
        return tuple(self._bars)

    def latest(self) -> Bar:
        """The most recently appended bar."""
        if not self._bars:
            raise ValueError("The buffer holds no bars, so there is no latest bar.")
        return self._bars[-1]

    def session_bars(self) -> tuple[Bar, ...]:
        """Every bar from session start to the latest bar, oldest first."""
        start = session_start_tick(self.latest().t)
        return tuple(bar for bar in self._bars if bar.t >= start)

    def day_change_pct(self) -> float:
        """`(close_latest / close_at_session_start - 1) * 100`, read off the buffer."""
        latest = self.latest()
        start = session_start_tick(latest.t)
        base = self._bar_at(start)
        if base is None:
            raise ValueError(
                f"day change % is undefined: the buffer holds no bar at session start "
                f"tick {start}; its oldest bar is tick {self._bars[0].t}."
            )
        return (latest.close / base.close - 1.0) * 100.0

    def session_volume(self) -> float:
        """The sum of `volume` over every bar from session start to the latest bar."""
        return sum(bar.volume for bar in self.session_bars())

    def _bar_at(self, tick: int) -> Bar | None:
        for bar in reversed(self._bars):
            if bar.t == tick:
                return bar
        return None
