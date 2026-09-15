---
spec: trading-demo
---

# Objective

A trader-facing dashboard that shows synthetic price fluctuations of a fixed instrument
universe, where selecting a world event from a dropdown visibly and causally changes the
data. It exists so that a factor-driven market simulation can be demonstrated to a
non-technical audience in a single view.

# Outcomes

- **O1** A running instance advances every instrument's price once per second of wall time
  with no client request, and a bar appended at tick *t* is never modified by any later tick.
- **O2** Two instances started from the same fixed seed produce identical backfilled
  histories and identical starting portfolios, compared field by field.
- **O3** Every instrument's price is strictly greater than zero at every tick, for every
  scenario in the library, over a run of at least 5000 ticks.
- **O4** The history holds at most 5000 bars per instrument; tick 5001 leaves the count at
  5000 and the oldest bar is the one that is gone.
- **O5** Over any window, the sum of the stored per-factor contributions plus the stored
  idiosyncratic residual equals the realised log return over that window, to within 1e-9.
- **O6** Activating a scenario leaves every bar before `activated_at` byte-identical to what
  it was before the POST, and changes bars after it.
- **O7** Every route declares a `response_model`, a tag and an explicit `operation_id`, and
  `/openapi.json` contains no operation id of the form `<name>_<path>_<method>`.
- **O8** `GET /impact/portfolio` returns a per-holding breakdown and never an instrument
  lookup for a symbol named `portfolio`.
- **O9** A trade posted as an amount produces a fractional quantity equal to
  `amount ÷ price` at execution, stored as a float, and the position's average entry
  reflects it.
- **O10** The portfolio response reports value, return and today's change as one set per
  currency, and no field anywhere sums across currencies.
- **O11** `GET /movers` returns gainers descending by day change %, losers ascending by day
  change %, and most active descending by session volume. Under an active scenario the
  membership of at least one of the three lists differs from baseline.
- **O12** `GET /macro` returns exactly five instruments, one per factor, each with exposure
  1.0 to its own factor and 0.0 to the other four.
- **O13** The Angular client is generated from the emitted schema and committed, and
  `ng build` succeeds with the backend not running.
- **O14** The watchlist and the detail view share one poll: exactly one `/quotes` request is
  in flight per interval however many components are subscribed.
- **O15** Selecting a scenario issues the POST and refreshes quotes without waiting out the
  poll interval.
- **O16** The string `Simulated feed` is present in the header on every view.
- **O17** The portfolio summary renders above every other element of the dashboard.
- **O18** The impact panel's default view shows plain-language sentences and at most three
  bars; no exposure value such as `oil beta -0.9` appears outside the expanded detail.
- **O19** The detail chart draws a labelled vertical marker at `activated_at` while a
  scenario is active, and none while at baseline.
- **O20** Adding a scenario to the library requires editing JSON only, with no change to any
  `.py` file.
- **O21** Each scenario in the library carries two or three headlines, and the ticker strip
  shows the active scenario's headlines and the baseline's when at baseline.
- **O22** Across a full poll cycle no numeric column changes width and no row reflows: a
  price moving between `9.99` and `10.01`, or a percentage between `+9.9%` and `+10.1%`,
  leaves every column boundary in the same place.
- **O23** No component stylesheet contains a hex colour, a `px` font size, a `px` spacing
  value or a transition duration; every such value resolves through a custom property
  declared in `frontend/src/styles/tokens.css`.

# Constraints

Quoted from `app-features.md` unless marked. Decisions taken at intake are marked
**[decided]** and carry no quotation because the input does not state them.

- "**Backend:** FastAPI (Python), Pydantic response models, no database" — `app-features.md:9`
- "**Frontend:** Angular (standalone components, RxJS, `HttpClient`)" — `app-features.md:10`
- "**Styling:** hand-rolled CSS, dark theme, no UI or styling packages" — `app-features.md:11`
- "**Transport:** HTTP polling (no WebSockets)" — `app-features.md:12`
- "Frontend and API are cross-origin in dev — either `CORSMiddleware` or an Angular dev proxy
  is required for requests to reach the API at all." — `app-features.md:23`
- "Roughly 25–40 equities across 6–8 sectors" plus "the five macro drivers" —
  `app-features.md:53`
- Betas are drawn from "{−1, −0.5, 0, +0.5, +1}" — `app-features.md:225`
- Factors are exactly: "market, rates/duration, oil, USD, credit spread" — `app-features.md:169`
- "one tick per second of wall time, representing one minute of market time" —
  `app-features.md:151`
- "At startup the loop runs roughly 780 ticks at full speed" — `app-features.md:203`
- "The buffer caps at ~5000 bars per instrument and discards the oldest" — `app-features.md:204`
- Client polls `/quotes` "on an RxJS interval (~2–3s) via a shared `QuoteService`" —
  `app-features.md:129`
- Chart timeframes are "1m, 5m, 15m, session" — `app-features.md:208`
- "Six or seven" scenarios — `app-features.md:293`
- Position size "is a float rather than an integer" — `app-features.md:50`
- "a 'Simulated feed' label in the header is required, not optional" — `app-features.md:299`
- "Exposure values such as 'oil beta −0.9' ... do not belong on the headline view" —
  `app-features.md:271`
- Generator is `ng-openapi-gen`, and the output is committed "so the frontend builds without
  the backend running" — `app-features.md:112`
- Off-limits: "WebSockets, offline support, Redis, multi-service deployment, options/greeks,
  customisable multi-pane layouts, order matching against a simulated book" — `app-features.md:320`
- Off-limits: "User-authored scenarios, timed multi-stage event sequences, estimating betas
  from historical data" — `app-features.md:303`
- No persistence layer, and "Do not abstract for it in advance" — `app-features.md:81`
- **[decided]** Instruments carry a native currency. No FX rate exists anywhere. Portfolio
  value, return and today's change are reported as one set per currency and never summed
  across currencies. The trade amount is in the instrument's native currency.
- **[decided]** The optional feature is the headlines ticker. Price alerts are out of scope.
- **[decided]** The PRNG seed is a fixed constant and the starting portfolio is fixed, so a
  run is reproducible.
- **[decided]** Backend outcomes are evidenced by `pytest` and commit at verification, per the
  orchestrator's default.
- **[decided]** **Frontend outcomes are verified by a human, not by a checker.** A frontend
  task's evidence is `ng build` succeeding plus the implementor's stated observation of the
  rendered application, reported verbatim. No frontend test framework is installed and none
  is to be added. Every frontend outcome is recorded `UNVERIFIED` — this is the expected
  result, not a gap to be closed.
- **[decided]** **Frontend tasks are not committed before human review.** T13–T24 land their
  deliverables and their run record, and the orchestrator stops at the review boundary rather
  than committing. This varies the standing commit rule, which `log-schema.md:196-200` allows
  a spec to do in its Constraints. Backend tasks are unaffected.
- **[decided]** Python is 3.12, pinned by `backend/.python-version`, and the environment is
  managed by `uv`. Two traps this guards against, both observed on this machine:
  - The system `python3` is 3.9.6, end of life since October 2025. A command resolving
    `python3` from PATH gets that interpreter, so no task invokes `python3` directly.
  - `requires-python = ">=3.12"` in `pyproject.toml` does **not** pin. uv selects the newest
    installed version satisfying the range — here 3.14.6, which is already present. Only
    `.python-version` (or an explicit `--python 3.12`) fixes the interpreter.
- **[decided]** **Every backend command runs from `backend/`.** uv discovers a project by
  searching the working directory and its ancestors, never its descendants, so `uv run` from
  the repository root does not find `backend/pyproject.toml` and silently executes in an
  ephemeral environment without the project's dependencies — no warning, no non-zero exit.
  Backend evidence commands are therefore written `cd backend && uv run …`, mirroring the
  frontend's `cd frontend && …`.
- **[decided]** `GET /impact/portfolio` is declared before `GET /impact/{symbol}` in the same
  router. The ordering is load-bearing, not stylistic.
- **[decided, not from the input]** Each bar carries a synthetic volume, so that "most
  active" ranks on something the model holds and stays currency-independent. The input
  defines `/movers` but not what makes an instrument active.
- The schema is emitted to a file by importing the app, not by running a server, so no task
  depends on a live process.
- No price-level literal is asserted in any test. A fixed seed makes exact prices
  reproducible, but the only source for such a literal is the implementation itself, and a
  test that takes its expected value from the code under test cannot fail. Price behaviour is
  asserted as properties: positivity, reconciliation, ordering, boundedness, determinism
  across two runs.

## Visual design

The frontend must read as a professional trading product, not as a demo of one. Taste is
judged at human review; the rules below are the part that is not a matter of taste, and they
are what stop twelve components each inventing their own greys and spacing.

- **One token file is the only source of visual values.** No component declares a raw hex
  colour, a `px` font size, a `px` spacing value or a motion duration of its own. Everything
  references a custom property from `frontend/src/styles/tokens.css`.
- **Numerals are tabular.** Every price, percentage and quantity renders in a
  `font-variant-numeric: tabular-nums` face, so digits occupy constant width.
- **No layout shift on poll.** Numeric columns are fixed-width and decimal-aligned; a price
  going from `9.99` to `10.01` must not move the column or reflow the row.
- **Fixed decimal places per instrument**, carried on the instrument and never inferred from
  the value. Prices do not gain or lose a decimal as they move.
- **Percentages are always signed** — `+1.24%` / `−1.24%` — using U+2212 minus, not a hyphen.
- **Colour carries signal only.** Green and red mean direction and nothing else. Every other
  surface is from the neutral ramp. No decorative accent colour anywhere.
- **Body text meets 4.5:1 contrast** against its background on the dark theme.
- **Motion is short and purposeful.** The row flash is a single background transition of
  120–300ms with no easing flourish, and all motion is suppressed under
  `prefers-reduced-motion: reduce`.
- **Every data surface declares its loading and empty states.** A pane awaiting its first
  poll shows a skeleton at the final layout's dimensions, never a blank area that then
  reflows.
- **Density over airiness.** Watchlist and movers rows are a stated fixed height; the
  dashboard shows the whole watchlist without scrolling at 1440×900.

**The run must be permitted to:** create and write under `backend/` and `frontend/`; run
`uv python install 3.12`, `uv venv`, `uv pip install`, `uv sync`, `uv run pytest`,
`uv run python`, each from `backend/`; run `npm install`,
`npm run`, `npx ng build`, `npx ng generate`, `npx ng-openapi-gen`. It must not be permitted
to start a long-running server as evidence for any task, and it must not install a frontend
test framework.

# Shared

- `backend/app/models.py` — the Pydantic response models every route returns — created by **T1**
- `backend/app/instruments.py` — the instrument universe and its loader — created by **T2**
- `backend/app/scenarios.py` — the scenario library, its loader and the id enum — created by **T3**
- `backend/app/sim.py` — the tick engine and the ring buffer — created by **T4**
- `backend/app/state.py` — the in-process store and the accessors every route reads through — created by **T5**
- `frontend/src/app/api/` — the generated API client — created by **T12**
- `frontend/src/styles/tokens.css` — the only source of colour, spacing, type, radius and
  motion values; every component reads it and none redeclares one — created by **T13**
- `frontend/src/app/core/format.ts` — the shared number, price and signed-percentage
  formatters, so no component formats a figure its own way — created by **T13**
- `frontend/src/app/core/quote.service.ts` — the single shared poll — created by **T14**

# Tasks

Ordered for reading, not for execution.

## T1 — Backend skeleton and response models

**Objective:** Create the FastAPI application and the Pydantic models every route returns, so
that later tasks add routes to an app that already exists and a contract that is already fixed.
**Outcome:** `cd backend && uv run python -V` reports 3.12; importing `app.main` yields a
FastAPI instance with CORS enabled; and every model named below is importable and rejects a
payload missing a required field. → serves **O7**
**Reads:** nothing — this is the first task.
**Deliverables:**
- CREATE `backend/.python-version` containing `3.12`
- CREATE `backend/pyproject.toml`
- CREATE `backend/app/main.py`
- CREATE `backend/app/models.py`
- ADD type `Quote`, `Candle`, `SymbolMatch`, `Position`, `CurrencyTotals`, `PortfolioResponse`, `TradeRequest`, `Mover`, `MoversResponse`, `MacroDriver`, `ScenarioSummary`, `ActiveScenario`, `FactorContribution`, `SymbolImpact`, `PortfolioImpact` in `backend/app/models.py`
- CREATE `backend/tests/test_models.py`

**Evidenced by:** `cd backend && uv run python -V && uv run pytest tests/test_models.py -v` —
the version line must read 3.12, and the tests assert each model rejects a payload with a
required field removed. Run before replying, output pasted.

## T2 — Instrument universe

**Objective:** Define the instrument universe as JSON and load it at startup, so that
scenarios have something to act on and betas can be tuned without touching code.
**Outcome:** The loader returns between 30 and 45 instruments spanning at least 6 sectors;
every instrument carries a currency and a beta for each of the five factors, every beta is
one of {-1.0, -0.5, 0.0, 0.5, 1.0}, and exactly five instruments are marked as macro drivers
with exposure 1.0 to their own factor and 0.0 to the other four. → serves **O12**
**Reads:** `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/data/instruments.json`
- CREATE `backend/app/instruments.py`
- ADD type `Instrument` in `backend/app/instruments.py`
- ADD function `load_instruments() -> dict[str, Instrument]` in `backend/app/instruments.py`
- CREATE `backend/tests/test_instruments.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_instruments.py -v` — asserts the
count bounds, the sector count, the beta value set, and the five macro drivers' exposure
rows. Run before replying, output pasted.

## T3 — Scenario library

**Objective:** Define the scenario library as JSON with per-factor shock, drift and half-life
plus a scenario-level volatility multiplier and its headlines, and load it behind a typed id
enum, so that adding a scenario is a data edit.
**Outcome:** The loader returns 6 or 7 scenarios including a baseline whose every shock and
drift is zero; each non-baseline scenario names at least two factors and carries 2 or 3
headlines; the id enum's members equal the ids present in the JSON. → serves **O20**, **O21**
**Reads:** `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/data/scenarios.json`
- CREATE `backend/app/scenarios.py`
- ADD type `FactorShock`, `Scenario` in `backend/app/scenarios.py`
- ADD type `ScenarioId` in `backend/app/scenarios.py`
- ADD function `load_scenarios() -> dict[ScenarioId, Scenario]` in `backend/app/scenarios.py`
- CREATE `backend/tests/test_scenarios.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_scenarios.py -v` — asserts the
library size, the baseline's zeroed factors, the headline counts, and that the enum members
and the JSON ids are the same set. Run before replying, output pasted.

## T4 — Simulation core

**Objective:** Implement the tick engine — per-factor returns, per-instrument log returns,
multiplicative price update, stored per-factor contributions and a bounded ring buffer — so
that price history exists and every move is attributable.
**Outcome:** Ticking advances every instrument's price by `exp(Σ beta·f + σ·vol_mult·ε)`;
prices stay strictly positive over 5000 ticks under every scenario; the buffer holds at most
5000 bars per instrument and discards oldest-first; the sum of a bar's stored factor
contributions plus its residual equals its log return to within 1e-9; two engines built with
the same seed produce identical bar sequences. → serves **O1**, **O2**, **O3**, **O4**, **O5**
**Reads:** `backend/app/instruments.py`, `backend/app/scenarios.py`
**Deliverables:**
- CREATE `backend/app/sim.py`
- ADD type `Bar` in `backend/app/sim.py`
- ADD class `RingBuffer` in `backend/app/sim.py`
- ADD class `Engine` in `backend/app/sim.py`
- ADD function `tick(self) -> None` in `backend/app/sim.py`
- CREATE `backend/tests/test_sim.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_sim.py -v` — one test per outcome
clause: positivity over 5000 ticks per scenario, buffer cap and eviction order at the 5000
and 5001 boundary, contribution reconciliation to 1e-9, and identity of two same-seed runs.
Run before replying, output pasted.

## T5 — In-process state, fixed-seed backfill and the tick loop

**Objective:** Hold the engine, the portfolio, the cash balance and the active scenario in
process; backfill history at startup from a fixed seed; and advance the engine once per
second for the life of the process.
**Outcome:** Startup leaves at least 780 bars per instrument and a fixed non-empty portfolio
identical across two starts; the active scenario is baseline; and the loop advances the
engine without any request being made. → serves **O1**, **O2**
**Reads:** `backend/app/sim.py`, `backend/app/main.py`
**Deliverables:**
- CREATE `backend/app/state.py`
- ADD var `SEED`, `BACKFILL_TICKS`, `STARTING_POSITIONS`, `STARTING_CASH` in `backend/app/state.py`
- ADD class `AppState` in `backend/app/state.py`
- ADD function `build_state() -> AppState` in `backend/app/state.py`
- UPDATE `backend/app/main.py` — ADD function `lifespan(app)` in `backend/app/main.py`
- CREATE `backend/tests/test_state.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_state.py -v` — asserts the backfill
depth, that two `build_state()` calls compare equal bar for bar and position for position,
that the active scenario is baseline, and that advancing the loop's coroutine once increases
every instrument's bar count by one. Run before replying, output pasted.

## T6 — Market endpoints

**Objective:** Serve symbol search, the polled quote set and the chart series off the buffer,
so the frontend has prices to display.
**Outcome:** `GET /symbols?q=` fuzzy-matches symbol and name and returns no non-matching
instrument; `GET /quotes?symbols=` returns one quote per requested symbol in request order
with last price, day change % and a sparkline; `GET /candles/{symbol}?tf=` aggregates the
buffer into 1m, 5m, 15m and session bars, and an unknown `tf` is rejected rather than
silently defaulted. → serves **O7**
**Reads:** `backend/app/state.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/market.py`
- ADD function `get_symbols`, `get_quotes`, `get_candles` in `backend/app/routers/market.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_market.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_market.py -v` — asserts the fuzzy
match excludes a known non-match, that quote order follows request order, that each timeframe
returns a bar count consistent with its aggregation factor, and that an unknown `tf` returns
422. Run before replying, output pasted.

## T7 — Portfolio and the amount-denominated trade

**Objective:** Serve paper positions with per-currency totals, and accept a trade expressed
as an amount in the instrument's native currency.
**Outcome:** `POST /portfolio/trade` with an amount produces a position quantity equal to
`amount ÷ price` as a float, updates the average entry on a second buy of the same symbol,
and rejects an amount exceeding the cash balance in that currency. `GET /portfolio` returns
one totals row per currency present in the holdings and no field summing across them.
→ serves **O9**, **O10**
**Reads:** `backend/app/state.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/portfolio.py`
- ADD function `get_portfolio`, `post_trade` in `backend/app/routers/portfolio.py`
- ADD function `apply_trade(state, symbol, amount) -> Position` in `backend/app/state.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_portfolio.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_portfolio.py -v` — asserts the
derived quantity is fractional and equals `amount ÷ price`, asserts the average entry after
two buys at different prices, asserts an over-balance trade is rejected, and asserts the
totals payload has one row per currency and no cross-currency total field. Run before
replying, output pasted.

## T8 — Movers and the macro drivers strip

**Objective:** Rank the quote set into gainers, losers and most active, and expose the five
macro drivers as their own endpoint.
**Outcome:** `GET /movers` returns gainers sorted descending by day change %, losers
ascending, and most active descending by session volume, with no instrument in both gainers
and losers. `GET /macro` returns exactly the five macro-driver instruments in factor order.
→ serves **O11**, **O12**
**Reads:** `backend/app/state.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/movers.py`
- ADD function `get_movers`, `get_macro` in `backend/app/routers/movers.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_movers.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_movers.py -v` — asserts each list's
sort direction pairwise, asserts the gainers and losers sets are disjoint, asserts `/macro`
returns exactly five in factor order, and asserts that activating a scenario and ticking
changes the membership of at least one list. Run before replying, output pasted.

## T9 — Scenario endpoints

**Objective:** Expose the scenario library, the active scenario and its activation, deletion
and headlines, so the dropdown has something to drive.
**Outcome:** `POST /scenario` sets the active scenario and stamps `activated_at`; `DELETE
/scenario` returns to baseline; `GET /scenario` reports the active id, its headlines and
`activated_at`; bars written before activation are unchanged by it. → serves **O6**, **O21**
**Reads:** `backend/app/state.py`, `backend/app/scenarios.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/scenario.py`
- ADD function `get_scenarios`, `get_scenario`, `post_scenario`, `delete_scenario` in `backend/app/routers/scenario.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_scenario_routes.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_scenario_routes.py -v` — snapshots
every bar before a POST and asserts the pre-activation slice is identical afterwards, asserts
`activated_at` is set on activation and cleared on delete, and asserts an unknown scenario id
returns 422. Run before replying, output pasted.

## T10 — Impact and attribution endpoints

**Objective:** Serve the scenario impact breakdown for one instrument and for the portfolio,
summed from the stored per-tick contributions.
**Outcome:** `GET /impact/{symbol}` returns the move since activation with its factor
contributions ordered largest absolute first, a residual, and a templated sentence per
factor; the contributions plus residual reconcile with the headline move to within 1e-9.
`GET /impact/portfolio` returns a per-holding breakdown and is never resolved as a symbol
lookup. → serves **O5**, **O8**
**Reads:** `backend/app/state.py`, `backend/app/sim.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/impact.py`
- ADD function `get_portfolio_impact`, `get_symbol_impact` in `backend/app/routers/impact.py`
- ADD var `FACTOR_SENTENCES` in `backend/app/routers/impact.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_impact.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_impact.py -v` — asserts the
reconciliation to 1e-9, asserts the contribution ordering, and asserts
`GET /impact/portfolio` returns the portfolio payload rather than a 404 or a symbol payload.
Run before replying, output pasted.

## T11 — OpenAPI hardening and schema emission

**Objective:** Give every route an explicit operation id and a tag, and emit the schema to a
file by importing the app, so the client generator needs no running server.
**Outcome:** `backend/openapi.json` exists on disk; every operation in it has an explicit
`operationId` and at least one tag; no operation id matches the FastAPI default form
`<name>_<path>_<method>`. → serves **O7**, **O13**
**Reads:** every router created by T6–T10, `backend/app/main.py`
**Deliverables:**
- UPDATE `backend/app/main.py`
- ADD function `generate_unique_id(route) -> str` in `backend/app/main.py`
- CREATE `backend/scripts/emit_openapi.py`
- CREATE `backend/openapi.json`
- CREATE `backend/tests/test_openapi.py`

**Evidenced by:** `cd backend && uv run python scripts/emit_openapi.py && uv run pytest
tests/test_openapi.py -v` — asserts all 13 operations carry an explicit id and a tag, and
asserts none matches the default-name pattern. Run before replying, output pasted.

## T12 — Angular workspace and the generated client

**Objective:** Create the Angular workspace and generate the typed API client from the
emitted schema, committing the output.
**Outcome:** `npm run gen:api` regenerates the client from `backend/openapi.json`; the
generated services cover all 13 operations; `ng build` succeeds with no backend process
running. → serves **O13**
**Reads:** `backend/openapi.json`
**Deliverables:**
- CREATE `frontend/package.json`
- CREATE `frontend/angular.json`
- CREATE `frontend/ng-openapi-gen.json`
- CREATE `frontend/src/app/api/`
- CREATE `frontend/src/app/app.config.ts`

**Evidenced by:** `cd frontend && npm run gen:api && npx ng build` — run with no backend
process running, output pasted. Then report the count of generated service methods and
confirm it is 13.

## T13 — Design system and application shell

**Objective:** Establish the token file and the shared formatters that every later component
is built from, and render the dark-theme shell, the toolbar and the required simulated-feed
label. This task sets the visual bar for the whole frontend; the eleven that follow inherit
it rather than restating it.
**Outcome:** `tokens.css` declares the full neutral ramp, the two signal colours, the spacing
scale, the type scale, the radii and the motion durations as custom properties, with body
text meeting 4.5:1 against its background; `format.ts` exports the price, quantity and signed
percentage formatters, the last emitting U+2212 for negatives; the shell renders a toolbar
containing the exact string `Simulated feed`; `package.json` declares no UI or styling
package. → serves **O16**, **O23**
**Reads:** `frontend/src/app/app.config.ts`
**Deliverables:**
- CREATE `frontend/src/styles/tokens.css`
- CREATE `frontend/src/styles.css`
- CREATE `frontend/src/app/core/format.ts`
- ADD function `formatPrice(value: number, dp: number) -> string`, `formatQuantity(value: number) -> string`, `formatSignedPercent(value: number) -> string` in `frontend/src/app/core/format.ts`
- CREATE `frontend/src/app/shell/shell.component.ts`
- UPDATE `frontend/src/app/app.config.ts`

**Evidenced by:** `cd frontend && npx ng build`, plus `grep -nE '#[0-9a-fA-F]{3,8}|[0-9]+px'
frontend/src/app/**/*.css` returning no match outside `tokens.css`, plus an observation:
state that `Simulated feed` appears in the rendered toolbar, paste the token file's colour
block with the computed contrast ratio for body text, and paste the `dependencies` block of
`frontend/package.json`. Recorded `UNVERIFIED`; held for human review before commit.

## T14 — The shared quote poll

**Objective:** Build the single `QuoteService` that polls `/quotes` on an RxJS interval and
is shared by every subscriber, and expose a method to force an immediate refresh.
**Outcome:** However many components subscribe, exactly one `/quotes` request is in flight
per interval; `refreshNow()` issues a request without waiting out the interval. → serves
**O14**, **O15**
**Reads:** `frontend/src/app/api/`
**Deliverables:**
- CREATE `frontend/src/app/core/quote.service.ts`
- ADD class `QuoteService` in `frontend/src/app/core/quote.service.ts`
- ADD function `quotes$(symbols: string[])`, `refreshNow()` in `frontend/src/app/core/quote.service.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: with two components
subscribed, report the number of `/quotes` entries in the browser network panel over one
interval. Recorded `UNVERIFIED`; held for human review before commit.

## T15 — Portfolio summary

**Objective:** Render total value, total return in currency and %, and today's change, as one
set per currency, above everything else on the dashboard.
**Outcome:** The summary is the first element in the dashboard's DOM order; it shows one
block per currency held; no displayed figure sums across currencies. → serves **O10**, **O17**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/shell/shell.component.ts`
**Deliverables:**
- CREATE `frontend/src/app/features/portfolio/portfolio-summary.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the dashboard's
first child element and the per-currency blocks rendered. Recorded `UNVERIFIED`; held for human review before commit.

## T16 — Macro drivers strip

**Objective:** Pin the five macro drivers along the top of the dashboard so the factor set is
visible as moving prices.
**Outcome:** Five tiles render, one per factor, in factor order, updating on the shared poll.
→ serves **O12**, **O14**
**Reads:** `frontend/src/app/core/quote.service.ts`, `frontend/src/app/api/`
**Deliverables:**
- CREATE `frontend/src/app/features/macro/macro-strip.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the five tile
labels in render order. Recorded `UNVERIFIED`; held for human review before commit.

## T17 — Watchlist

**Objective:** Render the watchlist rows — symbol, last price, day change %, sparkline — off
the shared poll, flashing green or red on change.
**Outcome:** Each row shows the four fields at a fixed row height, with price and change in
fixed-width decimal-aligned columns that do not move as values change width; a row whose
price rose since the previous poll flashes green and one that fell flashes red, for a single
transition of 120–300ms suppressed under `prefers-reduced-motion`; the sparkline redraws on
each poll without changing its box. → serves **O14**, **O22**
**Reads:** `frontend/src/app/core/quote.service.ts`, `frontend/src/app/api/`,
`frontend/src/app/core/format.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- CREATE `frontend/src/app/features/watchlist/watchlist.component.ts`
- CREATE `frontend/src/app/features/watchlist/sparkline.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report a row's four
fields and the flash colour observed on a rising and a falling tick. Recorded `UNVERIFIED`; held for human review before commit.

## T18 — Symbol search

**Objective:** Add the search box that fuzzy-matches the instrument list and adds a result to
the watchlist.
**Outcome:** Typing a partial symbol or name lists matching instruments and no non-matching
one; selecting a result adds it to the watchlist. → serves **O14**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/features/watchlist/watchlist.component.ts`
**Deliverables:**
- CREATE `frontend/src/app/features/search/symbol-search.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the results for a
two-character query and confirm a known non-match is absent. Recorded `UNVERIFIED`; held for human review before commit.

## T19 — Instrument detail chart

**Objective:** Render the line/candle chart with the timeframe toggle and the scenario
activation marker.
**Outcome:** Selecting an instrument renders its series; the toggle switches between 1m, 5m,
15m and session and the bar count changes accordingly; while a scenario is active a labelled
vertical marker is drawn at `activated_at`, and at baseline none is. → serves **O19**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/quote.service.ts`
**Deliverables:**
- CREATE `frontend/src/app/features/detail/detail.component.ts`
- CREATE `frontend/src/app/features/detail/chart.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the bar count at
each of the four timeframes, and confirm the marker's presence with a scenario active and its
absence at baseline. Recorded `UNVERIFIED`; held for human review before commit.

## T20 — Trade ticket

**Objective:** Build the ticket that takes an amount in the instrument's native currency and
shows the derived quantity before submission.
**Outcome:** The amount field is labelled with the selected instrument's currency; the
derived quantity shown equals `amount ÷ price` and is fractional; submitting posts the amount
and the portfolio summary updates. → serves **O9**, **O10**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/features/portfolio/portfolio-summary.component.ts`
**Deliverables:**
- CREATE `frontend/src/app/features/portfolio/trade-ticket.component.ts`
- UPDATE `frontend/src/app/features/detail/detail.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the currency
label, the amount entered, the derived quantity shown, and the summary before and after
submission. Recorded `UNVERIFIED`; held for human review before commit.

## T21 — Top movers

**Objective:** Render gainers, losers and most active as three lists that repopulate under a
scenario.
**Outcome:** Three lists render with the ordering the API returns; activating a scenario
visibly changes the membership of at least one. → serves **O11**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/quote.service.ts`
**Deliverables:**
- CREATE `frontend/src/app/features/movers/movers.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report each list's
membership at baseline and after activating the oil supply shock. Recorded `UNVERIFIED`; held for human review before commit.

## T22 — Scenario selector

**Objective:** Add the always-visible dropdown, the active-scenario chip and the forced
refresh on selection.
**Outcome:** The dropdown lists the library with "Reset to normal" first; selecting an item
POSTs and calls `refreshNow()` rather than waiting out the interval; the active scenario
shows as a chip in the toolbar. → serves **O15**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/quote.service.ts`, `frontend/src/app/shell/shell.component.ts`
**Deliverables:**
- CREATE `frontend/src/app/core/scenario.service.ts`
- CREATE `frontend/src/app/features/scenario/scenario-selector.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the dropdown's
first item, and the elapsed time between selecting a scenario and the watchlist updating.
Recorded `UNVERIFIED`; held for human review before commit.

## T23 — Headlines ticker

**Objective:** Render the active scenario's canned headlines in a ticker strip, so the
causality reads to a non-technical audience.
**Outcome:** The strip shows the active scenario's headlines and swaps to the new set within
one refresh of a scenario change. → serves **O21**
**Reads:** `frontend/src/app/core/scenario.service.ts`, `frontend/src/app/api/`
**Deliverables:**
- CREATE `frontend/src/app/features/ticker/headline-ticker.component.ts`
- UPDATE `frontend/src/app/shell/shell.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the headlines
shown at baseline and after activating a scenario. Recorded `UNVERIFIED`; held for human review before commit.

## T24 — Impact panel

**Objective:** Render the scenario impact panel for a selected instrument — plain language
first, full attribution behind a disclosure — and the peer comparison.
**Outcome:** The default view shows the headline move, at most three bars and one
plain-language sentence per factor, and contains no exposure value such as `oil beta -0.9`;
expanding the detail reveals the full per-factor attribution including exposures; the peer
list ranks same-sector instruments by impact. → serves **O18**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/features/detail/detail.component.ts`
**Deliverables:**
- CREATE `frontend/src/app/features/impact/impact-panel.component.ts`
- CREATE `frontend/src/app/features/impact/peer-comparison.component.ts`
- UPDATE `frontend/src/app/features/detail/detail.component.ts`

**Evidenced by:** `cd frontend && npx ng build` plus an observation: report the default
view's bar count and its full text, confirming no exposure value appears, then report the
expanded view's contents. Recorded `UNVERIFIED`; held for human review before commit.
