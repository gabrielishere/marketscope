---
name: impact-and-attribution
description: Serve the scenario impact breakdown for one instrument and for the portfolio, summed from stored per-tick contributions.
task: T10
model: claude-opus-5
---

# Objective

Serve the scenario impact breakdown for one instrument and for the portfolio, summed from the
stored per-tick contributions, so the frontend can explain a move in plain language.

# Outcome

`GET /impact/{symbol}` returns the move since activation with its factor contributions ordered
largest absolute first, a residual, a templated sentence per factor, and its same-sector peers
ranked by descending absolute move; the contributions plus residual reconcile with the
headline move to within 1e-6. `GET /impact/portfolio` returns a
per-holding breakdown and is never resolved as a symbol lookup.

- **Evidenced by:** `cd backend && uv run pytest tests/test_impact.py -v` — asserts the
  reconciliation to 1e-6 and reports the worst residual observed; asserts the contribution
  ordering is by descending absolute value, pairwise across the whole list; and asserts
  `GET /impact/portfolio` returns the portfolio payload rather than a 404 or a symbol payload;
  and asserts `peers` holds only same-sector instruments, excludes the subject symbol, and is
  ordered by descending absolute move, reporting the count it found for a named symbol. Run
  before replying and paste the output.

# Task context

- Anything below restated from the spec reproduces `## Definitions` and `## Response models`
  in `.spec-artifacts/specs/trading-demo-backend.md`. **If this prompt and the spec
  disagree, the spec governs**, and the disagreement is a defect to report rather than one
  to resolve. Read that file if a term here is thinner than the work needs.
- **Route ordering is load-bearing, not stylistic.** `GET /impact/portfolio` must be declared
  **before** `GET /impact/{symbol}` in the same router. Declared the other way round, FastAPI
  matches `portfolio` as a symbol and the portfolio breakdown becomes an instrument lookup for
  a symbol that does not exist.
- The contributions are already stored per bar by T25 — `Bar.contributions` and
  `Bar.residual`. This task sums them over the window since `activated_at`; it does not
  recompute the factor model.
- `activated_at` is the tick index the active scenario was activated at, held on application
  state by T9.
- `FACTOR_SENTENCES` is keyed by the five factor keys — `market`, `rates`, `oil`, `usd`,
  `credit` — and templates one plain-language sentence per factor. The frontend shows
  these in the collapsed impact panel and must show **no exposure value** such as
  `oil beta -0.9` there, so the sentences carry no beta and no exposure number.
- Reconciliation is to 1e-6, matching the tolerance T25 holds the stored contributions to.

# Deliverables

- **CREATE** `backend/app/routers/impact.py`
- **UPDATE** `backend/app/main.py` — register the router
- **Function(s):** `get_portfolio_impact`, `get_symbol_impact` — `get_portfolio_impact`
  declared first
- **Evidence:** `backend/tests/test_impact.py`

# Instructions

1. CREATE `backend/app/routers/impact.py`
2. ADD function `get_portfolio_impact`, `get_symbol_impact` in `backend/app/routers/impact.py`
3. ADD var `FACTOR_SENTENCES` in `backend/app/routers/impact.py`
4. UPDATE `backend/app/main.py`
5. CREATE `backend/tests/test_impact.py`

# Constraints

- `get_portfolio_impact` is declared before `get_symbol_impact`. Do not reorder them.
- Sum the stored contributions. Do not recompute the factor model in this router.
- Sentences in `FACTOR_SENTENCES` contain no beta, no exposure value and no factor jargon.
  They are read by a non-technical audience.
- Ordering is by descending **absolute** contribution, so a large negative ranks above a small
  positive. `peers` is ordered the same way, by absolute `move_pct`.
- `peers` is a field on the response, not a second request. The frontend's impact panel ranks
  same-sector instruments by impact and would otherwise issue one call per peer.
- No price-level literal is asserted in any test.
- Both routes declare a `response_model` and a tag.
- If the stored contributions do not reconcile to 1e-6, STOP and report it as a defect in T25
  rather than widening the tolerance here.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, including the worst reconciliation residual observed.
Then paste `FACTOR_SENTENCES` in full, so the wording can be read before the frontend renders
it.
