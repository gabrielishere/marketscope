"""The in-process store: the engine, the paper portfolio, the cash balance and the
active scenario, plus the fixed-seed backfill that gives the process a history the
moment it starts.

There is no database. Everything here lives in memory and dies with the process, and
nothing is abstracted in anticipation of a persistence layer that is not coming.

**The backfill.** `build_state()` ticks the engine `BACKFILL_TICKS` times before
returning, so the first request served already has history behind it. The count is
**two sessions** — 780 ticks at 390 ticks to a session — and the first bar written is
at **tick index 0**. Both matter:

* `RingBuffer.day_change_pct` raises when the bar at session start is not held.
  Starting anywhere but tick 0 would make that reachable on the very first session,
  because the session start for tick 500 is tick 390, and a backfill that began at
  tick 500 holds no bar there.
* Two prior sessions put a session boundary *behind* the latest bar, so day change is
  a figure about part of a session rather than about the whole of the only one held.

**Reproducibility.** `SEED` is a fixed constant and `STARTING_POSITIONS` is fixed data,
so two `build_state()` calls in one process, or one run today and one tomorrow, hold
the same bars and the same positions. Nothing here reads the clock, and no identifier,
quantity or price is drawn from anything but the seed and the data files.

**The tick loop.** `advance_once(state)` is one tick — the whole of what the background
task in `app.main` does, once a second. The behaviour lives in a function rather than
inside the loop body so that the tests can call it directly; a loop whose body is one
call has nothing left to test that the function does not already cover.

**The portfolio.** Positions are paper: a fixed set of symbols and quantities, held
since before the backfilled history begins, which is why each one's `avg_entry` is the
instrument's start price — the price the first backfilled bar opens at. Quantities are
floats, never integers, per Constraints. There is one currency across the universe and
no FX rate, so `STARTING_CASH` and every position value are figures in that one
currency and there is nothing to convert.
"""

from dataclasses import dataclass, field

from app import buffer as buffer_module
from app.buffer import RingBuffer
from app.instruments import Instrument
from app.scenarios import Scenario
from app.sim import Engine

#: The PRNG seed. A fixed constant, so a rehearsal and the demo show the same prices.
SEED = 20250101

#: One tick is one minute of market time; a session is 390 of them. Taken from
#: `app.buffer`, where the session-relative queries define it, rather than restated:
#: two definitions of a session would be two answers with nothing marking which is
#: right.
SESSION_TICKS = buffer_module.SESSION_TICKS

#: Ticks backfilled at startup: exactly two prior sessions, per the spec's 780. The
#: first bar written carries tick index 0 — see the module docstring for why.
BACKFILL_TICKS = 2 * SESSION_TICKS

#: Wall-clock seconds between ticks. One tick is one second of wall time and one
#: minute of market time; this is the whole of the conversion between the two.
TICK_SECONDS = 1.0

#: The paper portfolio: symbol to quantity, fixed so the run is reproducible.
#: Quantities are floats — a fractional share is a legitimate holding here, and the
#: contract's `Position.quantity` is a float — and the symbols are checked against the
#: universe at `build_state()`, so a position in an instrument that does not exist is
#: an error at startup rather than a hole a route falls into later.
STARTING_POSITIONS: dict[str, float] = {
    "AAPL": 320.0,
    "MSFT": 145.5,
    "NVDA": 480.25,
    "JPM": 210.0,
    "XOM": 640.75,
    "UNH": 55.5,
    "TSLA": 132.5,
    "NEE": 875.0,
}

#: Uninvested cash, in the one currency the universe is denominated in.
STARTING_CASH = 250_000.0


@dataclass(frozen=True, slots=True)
class Holding:
    """One paper position: what is held, how much of it, and at what average price.

    `unrealised_pnl` is not stored — it is a function of the latest price and is
    computed where it is served, so nothing here goes stale between ticks.
    """

    symbol: str
    quantity: float
    avg_entry: float


@dataclass(slots=True)
class AppState:
    """Everything the process holds: the simulation, the portfolio and the cash.

    Routes read through this object and never construct an `Engine` of their own, so
    there is one history in the process and one active scenario over it.
    """

    engine: Engine
    positions: dict[str, Holding] = field(default_factory=dict)
    cash: float = STARTING_CASH

    @property
    def instruments(self) -> dict[str, Instrument]:
        """The universe the engine is running, keyed by symbol."""
        return self.engine.instruments

    @property
    def buffers(self) -> dict[str, RingBuffer]:
        """Every instrument's bar history, keyed by symbol."""
        return self.engine.buffers

    @property
    def scenario(self) -> Scenario:
        """The active scenario. Baseline until something activates another."""
        return self.engine.scenario

    @property
    def activated_at(self) -> int | None:
        """The tick index the active scenario was activated at, or None at baseline."""
        return self.engine.activated_at

    @property
    def tick_index(self) -> int:
        """The tick index the next appended bar will carry."""
        return self.engine.tick_index


def build_state() -> AppState:
    """Build the process state and backfill `BACKFILL_TICKS` ticks of history.

    The engine rests at baseline: `Engine` constructed without a scenario takes the
    library's baseline and leaves `activated_at` as None, so the backfilled history is
    a quiet market and a scenario activated later has a before to be compared against.

    Raises `ValueError` when `STARTING_POSITIONS` names a symbol the universe does not
    hold — a position in nothing is a startup error, not a state to serve from.
    """
    engine = Engine(seed=SEED)
    positions = _build_positions(engine.instruments)
    for _ in range(BACKFILL_TICKS):
        engine.tick()
    return AppState(engine=engine, positions=positions, cash=STARTING_CASH)


def advance_once(state: AppState) -> None:
    """Advance the simulation by exactly one tick.

    One call, one bar appended to every instrument. This is the whole of what the
    background task in `app.main` does once a second, which is why the task needs no
    test of its own: its behaviour is this function's.
    """
    state.engine.tick()


def _build_positions(universe: dict[str, Instrument]) -> dict[str, Holding]:
    """The fixed portfolio as `Holding`s, rejecting a symbol outside the universe.

    `avg_entry` is the instrument's start price: the position predates the backfilled
    history, so it was entered at the price the first backfilled bar opens at.
    """
    missing = [symbol for symbol in STARTING_POSITIONS if symbol not in universe]
    if missing:
        raise ValueError(
            f"STARTING_POSITIONS names {missing}, which the universe does not hold; a "
            "position must name an instrument that exists."
        )
    return {
        symbol: Holding(
            symbol=symbol,
            quantity=float(quantity),
            avg_entry=universe[symbol].start_price,
        )
        for symbol, quantity in STARTING_POSITIONS.items()
    }


#: The one state the process serves from, built on first use. Routes call `get_state()`
#: rather than building their own, so every request reads the same history. The
#: lifespan takes this same instance and hands it to the background task.
_state: AppState | None = None


def get_state() -> AppState:
    """The process-wide state, backfilled on the first call and reused thereafter."""
    global _state
    if _state is None:
        _state = build_state()
    return _state
