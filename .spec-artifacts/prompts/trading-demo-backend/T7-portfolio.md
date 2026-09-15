---
name: portfolio
description: Serve the fixed paper positions and one set of totals.
task: T7
model: claude-sonnet-5
---

# Objective

Serve the fixed paper positions and their totals, so the portfolio summary has something to
show. One read-only route.

# Outcome

`GET /portfolio` returns every held position with its symbol, quantity and average entry, and
one set of totals — value, return and today's change, using `day change %` as defined below.

- **Evidenced by:** `cd backend && uv run pytest tests/test_portfolio.py -v` — asserts every
  symbol in `STARTING_POSITIONS` appears in the response with a float quantity, naming the
  count it found, and asserts the totals payload carries value, return and today's change. Run
  before replying and paste the output.

# Task context

- Anything below restated from the spec reproduces `## Definitions` and `## Response models`
  in `.spec-artifacts/specs/trading-demo-backend.md`. **If this prompt and the spec
  disagree, the spec governs**, and the disagreement is a defect to report rather than one
  to resolve. Read that file if a term here is thinner than the work needs.
- **`day change %`** is `(close_latest / close_at_session_start − 1) × 100`, read off the
  buffer via `RingBuffer.day_change_pct`.
- Every instrument is denominated in the same currency and there is no FX rate anywhere, so
  the totals are **one set of figures**, not one per currency. No field sums across
  currencies because there is nothing to sum across.
- Position size is a float, never an integer.
- There is no trade endpoint in this build. This route is read-only.

# Deliverables

- **CREATE** `backend/app/routers/portfolio.py`
- **UPDATE** `backend/app/main.py` — register the router
- **Function(s):** `get_portfolio`
- **Evidence:** `backend/tests/test_portfolio.py`

# Instructions

1. CREATE `backend/app/routers/portfolio.py`
2. ADD function `get_portfolio` in `backend/app/routers/portfolio.py`
3. UPDATE `backend/app/main.py`
4. CREATE `backend/tests/test_portfolio.py`

# Constraints

- Read-only. Add no `POST`, no trade handling and no mutation of state.
- Read `day change %` through `RingBuffer.day_change_pct`. Do not recompute it.
- No price-level literal is asserted in any test.
- The route declares a `response_model` and a tag.
- If `STARTING_POSITIONS` names a symbol absent from the universe, STOP and report it rather
  than skipping the position.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, including the position count the test found.
