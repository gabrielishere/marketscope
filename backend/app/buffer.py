"""The `Bar` record, the bounded per-instrument ring buffer and its session queries.

This module is the bottom of the stack. It imports nothing from the rest of the
project — not the engine, not the state, not the instrument universe — so that the
capacity rule and the two session-relative queries stand on their own commit and a
failure in the engine's maths leaves them standing.

`day_change_pct` and `session_volume` live here, once, because every surface that
displays or ranks by either reads through this buffer: the quote set, the movers
endpoint, the portfolio totals and the frontend's tables. A second definition
computed at a route would be a second answer with nothing marking which is right.

Buffer boundaries, as the Definitions settle them:

* `day_change_pct` **raises** on an empty buffer, and on one whose oldest bar falls
  after the current session start. There is no honest number for a session whose
  opening bar is not held, and a fallback to the oldest bar held or to `0.0` would
  quietly misreport every surface that displays day change.
* `session_volume` in both those cases is determined: it returns the sum of what
  the buffer holds, which for an empty buffer is `0.0`.

Neither case arises in the assembled system — backfill starts at tick 0 and the
5000-bar cap is about 12.8 sessions, so eviction cannot reach a session-start bar —
but the behaviour is required, not incidental.
"""

from collections import deque
from dataclasses import dataclass

#: The five factors, in factor order. The only thing this module takes from outside
#: it, written out as literals rather than imported, because it depends on no other
#: module in the project. These identifier-style strings are the keys themselves —
#: they reach the client as generated TypeScript — and are not the prose names
#: (market, rates/duration, oil, USD, credit spread) that describe the factors.
FACTORS: tuple[str, str, str, str, str] = (
    "market",
    "rates",
    "oil",
    "usd",
    "credit",
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
        """Every bar from session start to the latest bar, oldest first.

        Empty when the buffer is empty: there is no latest bar, so the window holds
        nothing rather than being undefined.
        """
        if not self._bars:
            return ()
        start = session_start_tick(self._bars[-1].t)
        return tuple(bar for bar in self._bars if bar.t >= start)

    def day_change_pct(self) -> float:
        """`(close_latest / close_at_session_start - 1) * 100`, read off the buffer.

        Raises `ValueError` when the buffer is empty, and when its oldest bar falls
        after the current session start — in neither case is the session's opening
        close held, and there is no honest figure to return in its place.
        """
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
        """The sum of `volume` over every bar from session start to the latest bar.

        Determined in every case, including the two where `day_change_pct` raises:
        it returns the sum of what the buffer holds, which is `0.0` when it is empty.
        """
        # The 0.0 start keeps the return a float when the window holds no bars.
        return sum((bar.volume for bar in self.session_bars()), 0.0)

    def _bar_at(self, tick: int) -> Bar | None:
        for bar in reversed(self._bars):
            if bar.t == tick:
                return bar
        return None
