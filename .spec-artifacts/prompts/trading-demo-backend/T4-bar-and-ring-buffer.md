---
name: bar-and-ring-buffer
description: Implement the Bar record, the bounded per-instrument ring buffer, and the two session-relative queries every ranking surface reads through.
task: T4
model: claude-opus-5
---

# Objective

Implement the `Bar` record and the bounded per-instrument ring buffer, plus the
session-relative queries every ranking and display surface reads through, so that the engine
in T25 has a history to append to and nothing downstream computes a session figure twice.

# Outcome

`Bar` carries exactly the fields named below. The buffer caps at 5000 bars per instrument and
discards the oldest when it is full. `day_change_pct` and `session_volume` compute against
tick index 390 boundaries, over hand-constructed bars rather than simulated ones.

- **Evidenced by:** `cd backend && uv run pytest tests/test_buffer.py -v` — asserts that
  `Bar`'s field names equal exactly the eight the Task context states, that `contributions`
  holds one entry per factor keyed by the five factor names, and that a `Bar` cannot be
  constructed without `contributions` or without `residual`; asserts the cap and the eviction
  order at the cap boundary; and asserts `day_change_pct` and `session_volume` against bars
  constructed by hand across a known tick-390 boundary, with expected values written as
  literals derived from the Task context rather than read out of the implementation. Run
  before replying and paste the output.

# Task context

- **`Bar` fields, exactly:** `t: int` (tick index), `open`, `high`, `low`, `close: float`,
  `volume: float`, `contributions: dict[str, float]` with exactly one entry per factor, and
  `residual: float`.
- **Market time.** One tick is one minute. A session is 390 ticks — a 6.5-hour trading day.
- **Session start.** The most recent tick index that is a multiple of 390.
- **`day change %`.** `(close_latest / close_at_session_start − 1) × 100`, read off the
  buffer. Every surface that displays or sorts by day change uses this definition and no
  other.
- **Session volume.** The sum of `volume` over every bar from session start to the latest bar.
  This is what the movers endpoint ranks *most active* on.
- **The five factor keys are exactly `market`, `rates`, `oil`, `usd`, `credit`, in that
  order.** They key `contributions`, and they are the only thing you take from outside this
  module. Use these strings verbatim — they are identifier-style on purpose and are not the
  prose names the Constraints use to describe the factors.
- This task and T25 were one task. The split puts the mechanical half — a data structure with
  a capacity rule, testable against literals with no simulation running — on its own commit,
  so a failure in the engine maths leaves it standing. Write nothing here that needs the
  engine to exist.

# Deliverables

- **CREATE** `backend/app/buffer.py`
- **Function(s):** `append(self, bar: Bar) -> None`, `day_change_pct(self) -> float`,
  `session_volume(self) -> float`
- **Evidence:** `backend/tests/test_buffer.py`

# Instructions

1. CREATE `backend/app/buffer.py`
2. ADD type `Bar` in `backend/app/buffer.py`
3. ADD class `RingBuffer` in `backend/app/buffer.py`
4. ADD function `append(self, bar: Bar) -> None` in `backend/app/buffer.py`
5. ADD function `day_change_pct(self) -> float` in `backend/app/buffer.py`
6. ADD function `session_volume(self) -> float` in `backend/app/buffer.py`
7. CREATE `backend/tests/test_buffer.py`

# Constraints

- This module imports nothing from `app.sim`, `app.state`, `app.instruments` or
  `app.scenarios`. It depends on no other module in the project.
- Every expected value in the test is written as a literal computed by hand from the
  definitions above. A test that calls the implementation to produce its own expected value
  cannot fail.
- **The attribution fields must be asserted, not merely declared.** `contributions` and
  `residual` are where O5's reconciliation is stored and are read by T25, T5 and T10, but no
  session-window query touches either — so evidence that only exercises the cap and the
  session queries would pass against a `Bar` that omits them entirely.
- No price level is asserted as a simulated value; hand-constructed bars are not price
  literals in the prohibited sense, and are required here.
- The cap is 5000 and the eviction is oldest-first. Do not make either configurable.
- If the definitions above leave a boundary case undetermined — the first session, a buffer
  shorter than one session — STOP and report which, rather than choosing silently.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, and the hand-computed literals used for
`day_change_pct` and `session_volume` with the arithmetic shown.
