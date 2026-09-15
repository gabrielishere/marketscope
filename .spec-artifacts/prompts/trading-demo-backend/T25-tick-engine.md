---
name: tick-engine
description: Implement the factor simulation — per-factor returns, per-instrument log returns, the multiplicative price update and stored contributions.
task: T25
model: claude-opus-5
---

# Objective

Implement the simulation itself — per-factor returns, per-instrument log returns, the
multiplicative price update and the stored per-factor contributions — appending each tick to
the buffer T4 provides, so that price history exists and every move is attributable.

# Outcome

Ticking advances every instrument's price by `exp(Σ beta·f + σ·vol_mult·ε)` and appends one
`Bar` per instrument. Prices stay strictly positive over 1200 ticks under every scenario in
the library. A bar's stored contributions plus its residual equal its log return to within
1e-6.

- **Evidenced by:** `cd backend && uv run pytest tests/test_sim.py -v` — one test per outcome
  clause: positivity over 1200 ticks for each scenario in the library, and contribution
  reconciliation to 1e-6. The positivity test must report the number of scenarios it ran and
  the minimum price it observed across all of them, so a test that silently ran zero scenarios
  is distinguishable from one that ran seven. No price literal is asserted. Run before
  replying and paste the output.

# Task context

- The five factors are exactly: market, rates/duration, oil, USD, credit spread.
- One tick is one second of wall time and represents one minute of market time.
- A scenario supplies per-factor shock, drift and half-life, plus a scenario-level volatility
  multiplier. Baseline's shocks and drifts are all zero.
- `Bar.contributions` holds exactly one entry per factor. `Bar.residual` holds the
  idiosyncratic part. The reconciliation the evidence checks is
  `sum(contributions.values()) + residual` against `log(close / previous_close)`.
- The multiplicative form is what keeps prices positive: a price is multiplied by `exp(...)`
  and never has a return added to it. Positivity is a consequence of that choice, not
  something to clamp for afterwards.
- The engine is constructed with a seed. Reproducibility matters so that a rehearsal and the
  demo look the same.

# Deliverables

- **CREATE** `backend/app/sim.py`
- **Function(s):** `tick(self) -> None` on `Engine` — advances one tick and appends one `Bar`
  per instrument
- **Evidence:** `backend/tests/test_sim.py`

# Instructions

1. CREATE `backend/app/sim.py`
2. ADD class `Engine` in `backend/app/sim.py`
3. ADD function `tick(self) -> None` in `backend/app/sim.py`
4. CREATE `backend/tests/test_sim.py`

# Constraints

- No price-level literal is asserted in any test. Price behaviour is asserted as properties:
  positivity and reconciliation. A fixed seed makes exact prices reproducible, but the only
  source for such a literal is the implementation itself, and a test taking its expected value
  from the code under test cannot fail.
- Do not clamp, floor or `max(0, ...)` a price to keep it positive. If positivity does not
  fall out of the multiplicative update, the update is wrong — STOP and report it.
- `tick()` appends exactly one bar per instrument per call and does nothing else. No timing,
  no sleeping, no scheduling: the loop that calls it lives in T5.
- Reconciliation is to 1e-6. Do not tighten or loosen it.
- If the reconciliation cannot be made to hold — if contributions and residual do not sum to
  the realised log return — STOP and report the discrepancy with a worked example. Do not
  widen the tolerance to make the test pass.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, including the scenario count and minimum observed price
from the positivity test, and the worst-case reconciliation residual observed.
