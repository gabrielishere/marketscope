---
name: backend-skeleton-and-models
description: Create the FastAPI app, its CORS middleware and the fourteen Pydantic response models every route returns.
task: T1
model: claude-opus-5
---

# Objective

Create the FastAPI application and the Pydantic response models every route returns, so that
every later task adds routes to an app that already exists and against a contract that is
already fixed. This is the first task in `trading-demo-backend`; nothing exists under
`backend/` yet.

# Outcome

`uv run python -V` reports 3.12. `app.main` exposes a FastAPI instance whose CORS middleware
answers a cross-origin preflight with an `access-control-allow-origin` header. Each of the
fourteen models below rejects a payload with a required field removed.

- **Evidenced by:** `cd backend && uv run python -V && uv run pytest tests/ -v` — the version
  line must read 3.12; `test_app.py` issues an `OPTIONS` preflight through `TestClient` and
  asserts the allow-origin header is present; `test_models.py` asserts each of the fourteen
  models rejects a payload with a required field removed. The run must collect **at least 15
  tests** and all must pass — fourteen model rejections plus the preflight. A green run with
  fewer than 15 collected means models are missing, not that the suite is fine. Run before
  replying and paste the output.

# Task context

- Python is pinned to 3.12 via `backend/.python-version`; `uv` reads it.
- The frontend is cross-origin in development, so without CORS middleware no request reaches
  the API at all. This is why the preflight is evidence rather than a nicety.
- These models are the contract. T11 emits them as a schema and the frontend spec generates
  its client from that emission, so a field added later is a contract change, not a detail.
- Every instrument is denominated in the same currency and there is no FX rate anywhere, so
  `PortfolioTotals` is one set of figures rather than one per currency.
- `Position` carries a float quantity. Position size is never an integer.

# Deliverables

- **CREATE** `backend/.python-version` — containing `3.12`
- **CREATE** `backend/pyproject.toml` — declaring `fastapi`, `pydantic`, and a dev group with
  `pytest` and `httpx`
- **CREATE** `backend/app/main.py` — the FastAPI instance and its CORS middleware
- **CREATE** `backend/app/models.py` — the fourteen response models
- **Evidence:** `backend/tests/test_models.py`, `backend/tests/test_app.py`

# Instructions

1. CREATE `backend/.python-version`
2. CREATE `backend/pyproject.toml`
3. CREATE `backend/app/main.py`
4. CREATE `backend/app/models.py`
5. ADD type `Quote`, `Candle`, `SymbolMatch`, `Position`, `PortfolioTotals`,
   `PortfolioResponse`, `Mover`, `MoversResponse`, `MacroDriver`, `ScenarioSummary`,
   `ActiveScenario`, `FactorContribution`, `SymbolImpact`, `PortfolioImpact` in
   `backend/app/models.py`
6. CREATE `backend/tests/test_models.py`
7. CREATE `backend/tests/test_app.py`

# Constraints

- No database, and no persistence layer. Nothing is abstracted in anticipation of one.
- No router, no endpoint and no business logic in this task. Routes arrive in T6–T10; an app
  that already answers requests would make those tasks' evidence untrustworthy.
- Declare no dependency beyond the four named. No ASGI server is declared: the schema is
  emitted in T11 by importing the app, never by running one.
- Every model field is explicitly typed. No bare `dict` or `Any` where a shape is known.
- If a model's shape is not determinable from this prompt, STOP and report which — do not
  invent a field and do not leave one out to make the task pass.

# Response format

First, one line per deliverable marked done or not done. Then one line per outcome clause —
the Python version, the preflight header, the model rejections — each with the evidence for
it. Then the pasted output of the evidence command in full, including the collected count.
State that count explicitly as a number.
