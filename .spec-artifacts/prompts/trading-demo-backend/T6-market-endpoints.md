---
name: market-endpoints
description: Serve symbol search, the polled quote set and the chart series off the buffer.
task: T6
model: claude-opus-5
---

# Objective

Serve symbol search, the polled quote set and the chart series off the buffer, so the frontend
has prices to display. Three routes on one router.

# Outcome

`GET /symbols?q=` fuzzy-matches symbol and name and returns no non-matching instrument; with
`q` omitted or empty it returns the whole universe with each entry's name, sector, currency
and decimal places. `GET /quotes?symbols=` returns one quote per requested symbol in request
order, carrying last price, `day change %` and a sparkline. `GET /candles/{symbol}?tf=`
aggregates the buffer into 1m, 5m, 15m and session bars, and an unknown `tf` is rejected
rather than silently defaulted.

- **Evidenced by:** `cd backend && uv run pytest tests/test_market.py -v` — asserts the fuzzy
  match excludes a named known non-match, that quote order follows request order for a
  deliberately unsorted request, that the returned day change equals
  `RingBuffer.day_change_pct` for the same symbol, that each timeframe returns a bar count
  consistent with its aggregation factor, and that an unknown `tf` returns 422. Run before
  replying and paste the output.

# Task context

- **`day change %`** is `(close_latest / close_at_session_start − 1) × 100`, read off the
  buffer via `RingBuffer.day_change_pct`. Every surface uses that method and no other — a
  route computing it independently is the defect this evidence exists to catch.
- The empty-`q` behaviour is how the markets table loads its static metadata once at load
  instead of on every poll. It is not a convenience; a later task depends on it.
- Chart timeframes are exactly 1m, 5m, 15m and session.
- Request order matters on `/quotes` because the client selects from the result positionally.
- Every route declares a `response_model` and a tag. Explicit operation ids arrive in T11, but
  the response model and tag are set here.

# Deliverables

- **CREATE** `backend/app/routers/market.py`
- **UPDATE** `backend/app/main.py` — register the router
- **Function(s):** `get_symbols`, `get_quotes`, `get_candles`
- **Evidence:** `backend/tests/test_market.py`

# Instructions

1. CREATE `backend/app/routers/market.py`
2. ADD function `get_symbols`, `get_quotes`, `get_candles` in `backend/app/routers/market.py`
3. UPDATE `backend/app/main.py`
4. CREATE `backend/tests/test_market.py`

# Constraints

- Read `day change %` through `RingBuffer.day_change_pct`. Do not recompute it in the router.
- An unknown `tf` returns 422. Do not fall back to a default timeframe.
- No price-level literal is asserted in any test.
- The sparkline's shape is not specified by the spec. Choose one, state it in your reply, and
  keep it consistent — a later frontend task consumes it and cannot ask.
- If the fuzzy match cannot both include a partial symbol and exclude a known non-match with
  one rule, STOP and report the conflict rather than loosening the test.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output. Then state the sparkline's shape — the field's type and
what its values mean — as one sentence, since the frontend spec must match it.
