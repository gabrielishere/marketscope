---
name: scenario-endpoints
description: Expose the library, the active scenario, its activation and deletion — and guarantee history written before activation is never rewritten.
task: T9
model: claude-opus-5
---

# Objective

Expose the scenario library, the active scenario and its activation, deletion and headlines,
so the dropdown has something to drive. Four routes on one router.

# Outcome

`GET /scenarios` lists the library. `POST /scenario` sets the active scenario and stamps
`activated_at`. `DELETE /scenario` returns to baseline. `GET /scenario` reports the active id,
its headlines and `activated_at`. Bars written before activation are unchanged by it.

- **Evidenced by:** `cd backend && uv run pytest tests/test_scenario_routes.py -v` — snapshots
  every bar for every instrument before a POST and asserts the pre-activation slice is
  byte-identical afterwards, reporting how many bars it compared; asserts `GET /scenarios`
  returns every id the library holds; asserts `GET /scenario` carries the active scenario's
  headlines, which is the half of O21 this task owns; asserts `activated_at` is set on
  activation and cleared on delete; and asserts an unknown scenario id returns 422. Run before
  replying and paste the output.

# Task context

- Anything below restated from the spec reproduces `## Definitions` and `## Response models`
  in `.spec-artifacts/specs/trading-demo-backend.md`. **If this prompt and the spec
  disagree, the spec governs**, and the disagreement is a defect to report rather than one
  to resolve. Read that file if a term here is thinner than the work needs.
- **`activated_at` is the tick index at which the active scenario was activated.** It lives on
  the application state, set by `POST /scenario` and cleared by `DELETE /scenario`. It is not
  a `Bar` field. Two later surfaces read it: the detail chart draws its marker there, and the
  impact endpoints measure the move since it.
- **The no-rewrite guarantee is the important clause.** Activating a scenario changes what
  happens *next*; it must never alter a bar already written. If it did, the chart would
  visibly redraw its own history mid-demo, which an audience notices immediately.
- Baseline is a scenario in the library like any other, with its own headlines. `DELETE`
  returns to it rather than to a null state.
- The typed scenario id enum from T3 is what makes a 422 possible rather than a 500.

# Deliverables

- **CREATE** `backend/app/routers/scenario.py`
- **UPDATE** `backend/app/main.py` — register the router
- **Function(s):** `get_scenarios`, `get_scenario`, `post_scenario`, `delete_scenario`
- **Evidence:** `backend/tests/test_scenario_routes.py`

# Instructions

1. CREATE `backend/app/routers/scenario.py`
2. ADD function `get_scenarios`, `get_scenario`, `post_scenario`, `delete_scenario` in
   `backend/app/routers/scenario.py`
3. UPDATE `backend/app/main.py`
4. CREATE `backend/tests/test_scenario_routes.py`

# Constraints

- Activation mutates only the active scenario and `activated_at`. It touches no existing bar,
  recomputes no history and re-seeds nothing.
- The snapshot comparison is over every bar of every instrument, not a sample.
- An unknown scenario id returns 422, not 404 and not 500.
- No price-level literal is asserted in any test.
- All four routes declare a `response_model` and a tag.
- If activation cannot leave prior bars untouched given how the engine holds state, STOP and
  report why — that is a defect in T25 or T5 to escalate, not something to work around here.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, including how many bars the snapshot comparison
covered. State in one sentence where `activated_at` is stored and what its type is, since two
later tasks read it.
