---
name: state-backfill-and-tick-loop
description: Hold the engine, portfolio, cash and active scenario in process; backfill 780 ticks from a fixed seed; advance once per second.
task: T5
model: claude-opus-5
---

# Objective

Hold the engine, the portfolio, the cash balance and the active scenario in process; backfill
history at startup from a fixed seed; and advance the engine once per second for the life of
the process. This is the module every route reads through.

# Outcome

`build_state()` leaves 780 bars per instrument, the first at tick index 0, and a fixed
non-empty portfolio, identical across two calls. The active scenario is baseline. One call to `advance_once` appends exactly
one bar to every instrument — this being the same function the background loop calls, so the
loop's behaviour is the function's.

- **Evidenced by:** `cd backend && uv run pytest tests/test_state.py -v` — asserts the backfill
  depth is exactly 780 for every instrument and that the earliest bar held is at tick index 0, that two `build_state()` calls compare equal bar
  for bar and position for position, that the active scenario is baseline, and that one
  `advance_once` call raises every instrument's bar count by exactly one. The comparison test
  must report how many bars and how many positions it compared, so a test comparing two empty
  states is distinguishable from one comparing two full ones. Run before replying and paste
  the output.

# Task context

- Startup backfills 780 ticks, which at 390 ticks to a session establishes exactly two prior
  sessions — enough for `day_change_pct` to have a session boundary behind it.
- **The backfill starts at tick index 0.** `RingBuffer.day_change_pct` raises when the bar at
  session start is not held, and starting the index anywhere else makes that reachable on the
  first session.
- The PRNG seed is a fixed constant and the starting portfolio is fixed, so a run is
  reproducible.
- One tick is one second of wall time.
- Position size is a float, never an integer.
- The lifespan's background task calls `advance_once` once per second and calls nothing else.
  Putting the behaviour in a function the tests can call directly is the reason the loop needs
  no test of its own.
- There is no database. All of this is in process and dies with it.

# Deliverables

- **CREATE** `backend/app/state.py`
- **UPDATE** `backend/app/main.py` — the lifespan and its background task
- **Function(s):** `build_state() -> AppState`, `advance_once(state: AppState) -> None`,
  `lifespan(app)`
- **Evidence:** `backend/tests/test_state.py`

# Instructions

1. CREATE `backend/app/state.py`
2. ADD var `SEED`, `BACKFILL_TICKS`, `SESSION_TICKS`, `STARTING_POSITIONS`, `STARTING_CASH` in
   `backend/app/state.py`
3. ADD class `AppState` in `backend/app/state.py`
4. ADD function `build_state() -> AppState` in `backend/app/state.py`
5. ADD function `advance_once(state: AppState) -> None` in `backend/app/state.py`
6. UPDATE `backend/app/main.py` — ADD function `lifespan(app)` in `backend/app/main.py`
7. CREATE `backend/tests/test_state.py`

# Constraints

- The background task calls `advance_once` and nothing else. No logging, no metrics, no
  conditional work inside the loop.
- No route is added in this task.
- No price-level literal is asserted in any test.
- `STARTING_POSITIONS` names symbols that exist in the universe. If one does not, the test
  must fail rather than the state silently holding a position in nothing.
- If the backfill cannot reach 780 bars for every instrument — if any instrument is added to
  the universe late, or starts short — STOP and report which, rather than asserting a smaller
  depth.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, including the bar and position counts the equality test
compared.
