---
name: movers-and-macro
description: Rank the quote set into gainers, losers and most active, and expose the five macro drivers.
task: T8
model: claude-sonnet-5
---

# Objective

Rank the quote set into gainers, losers and most active, and expose the five macro drivers as
their own endpoint. Two routes on one router.

# Outcome

`GET /movers` returns gainers sorted descending by `day change %`, losers ascending, and most
active descending by session volume, with no instrument in both gainers and losers.
`GET /macro` returns exactly the five macro-driver instruments in factor order.

- **Evidenced by:** `cd backend && uv run pytest tests/test_movers.py -v` — asserts each
  list's sort direction pairwise over the whole list, asserts the gainers and losers sets are
  disjoint, asserts most active ranks on `RingBuffer.session_volume`, asserts `/macro` returns
  exactly five in factor order, and asserts that activating a scenario and ticking changes the
  membership of at least one list, naming which list changed. Run before replying and paste
  the output.

# Task context

- **`day change %`** is `(close_latest / close_at_session_start − 1) × 100`, via
  `RingBuffer.day_change_pct`. **Session volume** is the sum of `volume` from session start to
  the latest bar, via `RingBuffer.session_volume`.
- **Factor order** is the order the factors are declared in: market, rates/duration, oil, USD,
  credit spread. `/macro` returns its five in that order, not sorted by anything else.
- The membership-change assertion is the backend half of the demo's payoff: a scenario has to
  visibly move the rankings, and this is where that becomes checkable without a browser.
- The client applies no sort of its own — the API's ordering is the contract — so a wrong
  order here surfaces as a silently wrong UI rather than an error.

# Deliverables

- **CREATE** `backend/app/routers/movers.py`
- **UPDATE** `backend/app/main.py` — register the router
- **Function(s):** `get_movers`, `get_macro`
- **Evidence:** `backend/tests/test_movers.py`

# Instructions

1. CREATE `backend/app/routers/movers.py`
2. ADD function `get_movers`, `get_macro` in `backend/app/routers/movers.py`
3. UPDATE `backend/app/main.py`
4. CREATE `backend/tests/test_movers.py`

# Constraints

- Rank through `RingBuffer.day_change_pct` and `RingBuffer.session_volume`. Do not recompute
  either in the router.
- Sort assertions are pairwise across the entire list, not a check of the first two elements.
- No price-level literal is asserted in any test.
- Both routes declare a `response_model` and a tag.
- If activating a scenario and ticking does not change any list's membership, STOP and report
  it — that is a defect in the simulation or the universe, not a test to relax.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, including which list's membership changed under the
scenario and what it changed from and to.
