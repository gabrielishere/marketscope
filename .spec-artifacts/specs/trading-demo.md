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
- **O3** Every instrument's price is strictly greater than zero at every tick, for every
  scenario in the library, over a run of at least 1200 ticks.
- **O5** Over any window, the sum of the stored per-factor contributions plus the stored
  idiosyncratic residual equals the realised log return over that window, to within 1e-6.
- **O6** Activating a scenario leaves every bar before `activated_at` byte-identical to what
  it was before the POST, and changes bars after it.
- **O7** Every route declares a `response_model`, a tag and an explicit `operation_id`, and
  `/openapi.json` contains no operation id of the form `<name>_<path>_<method>`.
- **O8** `GET /impact/portfolio` returns a per-holding breakdown and never an instrument
  lookup for a symbol named `portfolio`.
- **O11** `GET /movers` returns gainers descending by day change %, losers ascending by day
  change %, and most active descending by session volume. Under an active scenario the
  membership of at least one of the three lists differs from baseline.
- **O12** `GET /macro` returns exactly five instruments, one per factor, each with exposure
  1.0 to its own factor and 0.0 to the other four.
- **O13** The Angular client is generated from the emitted schema and committed, and
  `ng build` succeeds with the backend not running.
- **O14** One `/quotes` request is in flight per interval for the whole application — the
  service polls every symbol in the universe on a single timer and subscribers select from
  the result, so the count does not depend on how many components are mounted, which route is
  showing, or which symbols each one wants.
- **O15** Selecting a scenario issues the POST and refreshes quotes without waiting out the
  poll interval.
- **O16** The string `Simulated feed` is present in the header on every view.
- **O18** The impact panel's default view shows plain-language sentences and at most three
  bars; no exposure value such as `oil beta -0.9` appears outside the expanded detail.
- **O19** The detail chart draws a labelled vertical marker at `activated_at` while a
  scenario is active, and none while at baseline.
- **O21** Each scenario in the library carries two or three headlines, and the ticker strip
  shows the active scenario's headlines and the baseline's when at baseline.
- **O22** Across a full poll cycle no numeric column changes width and no row reflows: a
  price moving between `9.99` and `10.01`, or a percentage between `+9.9%` and `+10.1%`,
  leaves every column boundary in the same place.
- **O23** No component source contains a hex colour, a `px` value or a millisecond duration;
  every such value resolves through a custom property declared in
  `frontend/src/styles/tokens.css`.
- **O24** The app has two routes — `/` (dashboard) and `/markets` (table) — and the toolbar,
  its `Simulated feed` label and the active-scenario chip persist across both. Switching
  between them does not create a second `/quotes` poll: the request rate with both tabs
  visited is the same as with one.
- **O25** The markets table lists every instrument in the universe, grouped by sector, each
  group headed by its aggregate day change; sector groups order by that aggregate, and rows
  order within a group by the selected column. Activating a scenario reorders the groups.

# Constraints

Bounds on how the system is built. Every line is binding on every task.

**Stack**

- Backend is FastAPI with Pydantic response models. No database.
- Frontend is Angular: standalone components, RxJS, `HttpClient`.
- Styling is hand-rolled CSS, dark theme. No UI or styling package.
- Transport is HTTP polling. No WebSockets.
- Frontend and API are cross-origin in dev. `CORSMiddleware` or an Angular dev proxy is
  required for requests to reach the API at all.
- No persistence layer, and nothing is abstracted in anticipation of one.

**The model**

- The factors are exactly: market, rates/duration, oil, USD, credit spread.
- Betas are drawn from {−1, −0.5, 0, +0.5, +1}.
- One tick is one second of wall time and represents one minute of market time.
- Startup backfills 780 ticks.
- The buffer caps at 5000 bars per instrument and discards the oldest.
- Each bar carries a synthetic volume; `/movers` ranks *most active* on it.
- The library holds 6 or 7 scenarios.
- The PRNG seed is a fixed constant and the starting portfolio is fixed, so a run is
  reproducible.
- Position size is a float, never an integer.
- Every instrument is denominated in the same currency and there is no FX rate anywhere.
  Portfolio value, return and today's change are one set of figures, and a trade amount is in
  that currency. Instruments still carry a currency field, so the UI has a symbol to render,
  but it is constant across the universe.

**Surface**

- The client polls `/quotes` on an RxJS interval of 2–3s through one shared service.
- Chart timeframes are 1m, 5m, 15m and session.
- The header carries the string `Simulated feed` on every view. This is required.
- Exposure values such as `oil beta −0.9` never appear on a headline view.
- The optional feature is the headlines ticker. Price alerts are out of scope.

**Contract**

- The client is generated by `ng-openapi-gen` and the output is committed, so the frontend
  builds without the backend running.
- `app.openapi_version` is pinned to `"3.0.2"`. FastAPI emits 3.1 by default and the
  generator may reject it; pinning is unconditional because the task that would discover the
  rejection is not the task that can fix it.
- The schema is emitted to a file by importing the app, never by running a server, so no task
  depends on a live process.
- `GET /impact/portfolio` is declared before `GET /impact/{symbol}` in the same router. The
  ordering is load-bearing, not stylistic.

**Off-limits**

- WebSockets, offline support, Redis, multi-service deployment, options and greeks,
  customisable multi-pane layouts, order matching against a simulated book.
- User-authored scenarios, timed multi-stage event sequences, betas estimated from historical
  data.

**How the run is verified**

- Backend outcomes are evidenced by `pytest` and commit at verification, per the
  orchestrator's default.
- **Frontend outcomes are verified by a human, not by a checker.** No frontend test framework
  is installed and none is to be added. A frontend task's evidence is what the implementor can
  actually produce — a build, a file, a grep — and its behavioural claim is **deferred to
  human review**; *Frontend evidence* below is the rule those tasks are written against. Every
  frontend outcome is recorded `UNVERIFIED`, which is the expected result and not a gap.
- **The frontend stops for review twice, not thirteen times.** Because the visual target is
  approved before the run — see *Visual design* — a per-task taste judgement no longer buys
  anything, and thirteen stops for a demo nobody has built yet is the wrong trade.
  - **T13 holds.** The orchestrator lands its deliverables and its run record and stops. This
    is the one conformance gate: the shell and the token file either match
    `.spec-artifacts/design/dashboard-mock.html` or they do not, and nine tasks are built on
    the answer.
  - **T14–T24 and T26 commit on their implementor evidence**, the way backend tasks do. Their
    behavioural claims are still recorded `UNVERIFIED` and still deferred — they accumulate
    into the single review walk below, taken once after T26.
  - This varies the standing commit rule, which `log-schema.md:196-200` allows a spec to do
    here. Backend tasks are unaffected — including **T25**, which sits inside that range by
    reading order but is the backend tick engine and commits at verification like every other
    backend task.
- No price-level literal is asserted in any test — see the last bullet of this section.

**The environment**

- Python is 3.12, pinned by `backend/.python-version`, managed by `uv`. Two traps, both
  observed on the target machine:
  - The system `python3` is 3.9.6, end of life since October 2025. No task invokes `python3`
    directly.
  - `requires-python = ">=3.12"` does **not** pin — uv takes the newest installed version
    satisfying the range, which on this machine is 3.14.6. Only `.python-version`, or an
    explicit `--python 3.12`, fixes the interpreter.
- **Every backend command runs from `backend/`.** uv finds a project by searching the working
  directory and its ancestors, never its descendants, so `uv run` from the repository root
  misses `backend/pyproject.toml` and executes in an ephemeral environment without the
  project's dependencies — no warning, no non-zero exit. Backend commands are written
  `cd backend && uv run …`, mirroring the frontend's `cd frontend && …`.
- No price-level literal is asserted in any test. A fixed seed makes exact prices
  reproducible, but the only source for such a literal is the implementation itself, and a
  test that takes its expected value from the code under test cannot fail. Price behaviour is
  asserted as properties: positivity, reconciliation, ordering and boundedness.

## Definitions

Terms more than one task reads. Each is settled once here; a task that needs one takes it
from this list rather than deciding it locally, because four tasks deciding the same term
separately is four different answers with nothing marking which is right.

- **Market time.** One tick is one minute. A **session** is **390 ticks** — a 6.5-hour
  trading day. The 780-tick backfill therefore establishes exactly two prior sessions.
- **Session start.** The most recent tick index that is a multiple of 390.
- **`day change %`.** `(close_latest / close_at_session_start − 1) × 100`, read off the
  buffer. Every surface that displays or sorts by day change uses this definition and no
  other — it is shown by T6 and T17, sorted on by T8, and aggregated by T7 and T15.
- **Session volume.** The sum of `volume` over every bar from session start to the latest
  bar. This is what `/movers` ranks *most active* on.
- **`Bar` fields.** `t: int` (tick index), `open`, `high`, `low`, `close: float`,
  `volume: float`, `contributions: dict[str, float]` with exactly one entry per factor, and
  `residual: float`. O5's reconciliation is `sum(contributions.values()) + residual` against
  `log(close / previous_close)`.

## Frontend evidence

The implementor has Read, Write, Edit, Glob, Grep and Bash. **It has no browser.** An
instruction to report what a rendered page does is an instruction it cannot carry out, and
`implementor.md:71-74` requires it to say so rather than invent one — so a task written that
way stalls rather than completing.

Every frontend task therefore splits its evidence in two:

- **Produced by the implementor** — `npx ng build` output, a file pasted, a grep result. Facts
  about the source tree, which Bash can establish.
- **Deferred to human review** — the behavioural claim, stated as a numbered checklist the
  reviewer walks. The implementor **must not** report these as observed, and a report that
  does is a defect worth escalating rather than a result to record.

### The review order

Twelve tasks each deferring two or three items is eighteen checks, and a reviewer walking them
in task order walks them in the order they were *built*, not the order in which they matter. A
rushed pass down that list spends its attention on tile ordering and reaches the feature the
demo exists for last.

This is the **second** of the two frontend stops, taken once after T26 with everything in
place. The first is T13's conformance gate against the mockup, which is not in this index.

So the review has one order, below, and it is an **index** — each row names the task that
defers the item and a short label. The wording that governs lives in the task block and
nowhere else, because a second copy of a check is free to disagree with the first.

Walk it top to bottom with the app running. **F1–F5 are the demo**; if any of them is wrong
nothing below it matters.

| | Task | The check |
|---|---|---|
| **F1** | T22 | selecting a scenario changes the data without waiting out the poll |
| **F1b** | T26 | the oil shock reorders the market table's sector groups, energy above travel |
| **F2** | T21 | the movers lists repopulate under the oil shock |
| **F3** | T19 | the activation marker appears, and is absent at baseline |
| **F4** | T24 | the collapsed impact panel reads as plain language, no exposure values |
| **F5** | T23 | the headlines swap within one refresh |
| **F6** | T14 | one `/quotes` request per interval with two views open |
| **F6b** | T26 | switching to the markets tab and back does not add a second poll |
| **F6c** | T26 | the table's scroll position survives a poll, and the pane never resizes |
| **F6d** | T13 | the toolbar, its label and the scenario chip persist across both tabs |
| **F7** | T17 | no column boundary moves as a price crosses a digit width |
| **F8** | T17 | rising rows flash green, falling red |
| **F9** | T15 | the summary shows value, return and today's change, above every other element |
| **F12** | T24 | peers are same-sector and ranked by impact |
| **F13** | T19 | the four timeframes give visibly different bar counts |
| **F14** | T16 | five macro tiles, in factor order, updating together |

**The run must be permitted to:** create and write under `backend/` and `frontend/`; run
`uv python install 3.12`, `uv venv`, `uv pip install`, `uv sync`, `uv run pytest`,
`uv run python`, each from `backend/`; run `npm install`, `npm run`, `npx ng build`,
`npx ng generate`, `npx ng-openapi-gen`, each from `frontend/`. It must not be permitted to
start a long-running server as evidence for any task, and it must not install a frontend test
framework.

## Visual design

The frontend must read as a professional trading product, not as a demo of one.

**`.spec-artifacts/design/dashboard-mock.html` is the approved visual target**, and it is
where the taste judgement has already been made. It is a static reference — no framework, no
data, no polling — showing both routes with a scenario active. Its `:root` block is the token
file: T13 copies those custom properties into `frontend/src/styles/tokens.css` with the same
names and the same values rather than choosing a palette, a spacing scale or a type scale of
its own. Below that block the mockup itself contains no raw value, which is the rule O23
places on component source, so the file demonstrates the convention it establishes.

A component conforms to the mockup or it is wrong. The rules below are the part of that which
can be stated independently of the file.

- **One token file is the only source of visual values.** No component declares a raw hex
  colour, a `px` value of any kind — type size, spacing, border width or radius — or a motion
  duration of its own. Everything references a custom property from
  `frontend/src/styles/tokens.css`. This is the same ban O23 states; the two are one rule.
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
- **Density over airiness.** Watchlist, movers and market-table rows are a stated fixed
  height, the same one across all three. The two surfaces then differ:
  - **The dashboard's watchlist is curated and does not scroll.** It shows its whole
    contents at 1440×900. A watchlist long enough to scroll is the markets tab's job.
  - **The markets table scrolls inside a fixed-height pane** under a sticky header. The pane's
    height never changes as rows update, and the scroll position survives a poll — a table
    that jumps back to the top every two seconds is unusable, and it is the failure this rule
    exists to prevent.
- **A polled table re-renders only what changed.** The market table is ~40 rows each carrying
  a sparkline, redrawn every 2–3 seconds. Rows track by symbol and the component uses
  `OnPush`, so a poll updates the cells that moved rather than rebuilding the table. Without
  this the flash animation restarts on every row each poll, which reads as flicker rather
  than as signal.

# Shared

- `backend/app/models.py` — the Pydantic response models every route returns — created by **T1**
- `backend/app/instruments.py` — the instrument universe and its loader — created by **T2**
- `backend/app/scenarios.py` — the scenario library, its loader and the id enum — created by **T3**
- `backend/app/buffer.py` — `Bar`, the bounded ring buffer, and the session-relative queries
  (`day_change_pct`, `session_volume`) every ranking and display surface reads through —
  created by **T4**
- `backend/app/sim.py` — the tick engine — created by **T25**
- `backend/app/state.py` — the in-process store and the accessors every route reads through — created by **T5**
- `backend/openapi.json` — the emitted contract the client is generated from — created by **T11**
- `frontend/src/app/api/` — the generated API client — created by **T12**
- `frontend/src/styles/tokens.css` — the only source of colour, spacing, type, radius and
  motion values; every component reads it and none redeclares one — created by **T13**
- `frontend/src/app/core/format.ts` — the shared number, price and signed-percentage
  formatters, so no component formats a figure its own way — created by **T13**
- `frontend/src/app/dashboard/dashboard.component.ts` — the composition: it declares every
  feature slot in its final order at T13 and **is not edited again**. Feature tasks fill
  their own stub and touch nothing shared — created by **T13**
- `frontend/src/app/core/quote.service.ts` — the single shared poll — created by **T14**
- `frontend/src/app/core/scenario.service.ts` — the active scenario and its headlines, read by
  the selector and the ticker — created by **T22**

**On the stubs.** T13 creates every feature component as a skeleton placeholder rendering its
loading state, and the dashboard composes all eight from the start. Two things follow. The app
renders from T13 onward, so a human reviewing T17 sees it in place rather than in isolation —
which matters when twelve tasks are verified by eye. And the feature tasks each `UPDATE` one
file nobody else writes, instead of seven of them `UPDATE`-ing the shell in sequence.

# Tasks

Ordered for reading, not for execution.

## T1 — Backend skeleton and response models

**Objective:** Create the FastAPI application and the Pydantic models every route returns, so
that later tasks add routes to an app that already exists and a contract that is already fixed.
**Outcome:** `uv run python -V` reports 3.12; `app.main` exposes a FastAPI instance whose
CORS middleware answers a cross-origin preflight with an `access-control-allow-origin`
header; and every model named below rejects a payload with a required field removed.
→ serves **O7**
**Reads:** nothing — this is the first task.
**Deliverables:**
- CREATE `backend/.python-version` containing `3.12`
- CREATE `backend/pyproject.toml` declaring `fastapi`, `pydantic`, and a dev group with `pytest` and `httpx`
- CREATE `backend/app/main.py`
- CREATE `backend/app/models.py`
- ADD type `Quote`, `Candle`, `SymbolMatch`, `Position`, `PortfolioTotals`, `PortfolioResponse`, `Mover`, `MoversResponse`, `MacroDriver`, `ScenarioSummary`, `ActiveScenario`, `FactorContribution`, `SymbolImpact`, `PortfolioImpact` in `backend/app/models.py`
- CREATE `backend/tests/test_models.py`
- CREATE `backend/tests/test_app.py`

**Evidenced by:** `cd backend && uv run python -V && uv run pytest tests/ -v` — the version
line must read 3.12; `test_app.py` issues an `OPTIONS` preflight through `TestClient` and
asserts the allow-origin header is present; `test_models.py` asserts each of the fifteen
models rejects a payload with a required field removed. Run before replying, output pasted.

## T2 — Instrument universe

**Objective:** Define the instrument universe as JSON and load it at startup, so that
scenarios have something to act on and betas can be tuned without touching code.
**Outcome:** The loader returns 40 equities across exactly 7 sectors with **at least 4 in
every sector**, plus the 5 macro drivers, for 45 instruments total; every instrument carries
a name, a sector, a currency, a decimal-places value and a beta for each of the five factors;
every beta is one of {-1.0, -0.5, 0.0, 0.5, 1.0}; each macro driver has exposure 1.0 to its
own factor and 0.0 to the other four; and **at least two sectors contain a pair of
instruments whose oil betas have opposite signs**. → serves **O12**, **O25**

*The per-sector minimum and the opposing-beta pair are load-bearing for T26, which groups by
sector: a sector holding one row renders as a header with nothing under it, and a sector whose
members all move together makes the table read as a sector model rather than a factor one.*
**Reads:** `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/data/instruments.json`
- CREATE `backend/app/instruments.py`
- ADD type `Instrument` in `backend/app/instruments.py`
- ADD function `load_instruments() -> dict[str, Instrument]` in `backend/app/instruments.py`
- CREATE `backend/tests/test_instruments.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_instruments.py -v` — asserts the
counts — 40 equities, 7 sectors, no sector below 4, 45 total — that every instrument has a
name, sector, currency and decimal-places value, the beta value set, the five macro drivers'
exposure rows, and that at least two sectors contain a pair with opposite-signed oil betas.
Run before replying, output pasted.

## T3 — Scenario library

**Objective:** Define the scenario library as JSON with per-factor shock, drift and half-life
plus a scenario-level volatility multiplier and its headlines, and load it behind a typed id
enum, so that adding a scenario is a data edit.
**Outcome:** The loader returns 6 or 7 scenarios including a baseline whose every shock and
drift is zero and an oil supply shock; every scenario, baseline included, carries 2 or 3
headlines; each non-baseline scenario names at least two factors; the id enum's members equal
the ids present in the JSON. → serves **O21**
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

## T4 — Bar and the bounded ring buffer

**Objective:** Implement the `Bar` record and the bounded per-instrument ring buffer, plus the
session-relative queries every ranking and display surface reads through, so that the engine
in **T25** has a history to append to and nothing downstream computes a session figure twice.

*This task and T25 were one task. Splitting them puts the mechanical half — a data structure
with a capacity rule, testable against literals with no simulation running — on its own
commit, so a failure in the engine maths leaves it standing.*

**Outcome:** `Bar` carries exactly the fields the Definitions name; the buffer caps at 5000
bars per instrument and discards the oldest, per Constraints; `day_change_pct` and
`session_volume` compute against tick index 390 boundaries as the Definitions state, over
hand-constructed bars rather than simulated ones. → serves no outcome directly; it is the
structure **T25** appends to
**Reads:** nothing — it depends on no other module.
**Deliverables:**
- CREATE `backend/app/buffer.py`
- ADD type `Bar` in `backend/app/buffer.py` — fields exactly as the Definitions section states
- ADD class `RingBuffer` in `backend/app/buffer.py`
- ADD function `append(self, bar: Bar) -> None` in `backend/app/buffer.py`
- ADD function `day_change_pct(self) -> float` in `backend/app/buffer.py`
- ADD function `session_volume(self) -> float` in `backend/app/buffer.py`
- CREATE `backend/tests/test_buffer.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_buffer.py -v` — asserts the cap and
the eviction order at the cap boundary, and asserts `day_change_pct` and
`session_volume` against bars constructed by hand across a known tick-390 boundary, with the
expected values written as literals taken from the Definitions rather than from the code. Run
before replying, output pasted.

## T25 — The tick engine

**Objective:** Implement the simulation itself — per-factor returns, per-instrument log
returns, the multiplicative price update and the stored per-factor contributions — appending
each tick to the buffer **T4** provides, so that price history exists and every move is
attributable.
**Outcome:** Ticking advances every instrument's price by `exp(Σ beta·f + σ·vol_mult·ε)` and
appends one `Bar` per instrument; prices stay strictly positive over 1200 ticks under every
scenario in the library; a bar's stored contributions plus its residual equal its log return
to within 1e-6. → serves **O1**, **O3**, **O5**
**Reads:** `backend/app/buffer.py`, `backend/app/instruments.py`, `backend/app/scenarios.py`
**Deliverables:**
- CREATE `backend/app/sim.py`
- ADD class `Engine` in `backend/app/sim.py`
- ADD function `tick(self) -> None` in `backend/app/sim.py`
- CREATE `backend/tests/test_sim.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_sim.py -v` — one test per outcome
clause: positivity over 1200 ticks for each scenario in the library, and contribution
reconciliation to 1e-6. No price literal is asserted, per Constraints. Run before replying,
output pasted.

## T5 — In-process state, fixed-seed backfill and the tick loop

**Objective:** Hold the engine, the portfolio, the cash balance and the active scenario in
process; backfill history at startup from a fixed seed; and advance the engine once per
second for the life of the process.
**Outcome:** `build_state()` leaves 780 bars per instrument and a fixed non-empty portfolio
identical across two calls; the active scenario is baseline; and one call to `advance_once`
appends exactly one bar to every instrument — this being the same function the background
loop calls, so the loop's behaviour is the function's. → serves **O1**
**Reads:** `backend/app/sim.py`, `backend/app/buffer.py`, `backend/app/main.py`
**Deliverables:**
- CREATE `backend/app/state.py`
- ADD var `SEED`, `BACKFILL_TICKS`, `SESSION_TICKS`, `STARTING_POSITIONS`, `STARTING_CASH` in `backend/app/state.py`
- ADD class `AppState` in `backend/app/state.py`
- ADD function `build_state() -> AppState` in `backend/app/state.py`
- ADD function `advance_once(state: AppState) -> None` in `backend/app/state.py`
- UPDATE `backend/app/main.py` — ADD function `lifespan(app)` in `backend/app/main.py`, whose background task calls `advance_once` once per second and calls nothing else
- CREATE `backend/tests/test_state.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_state.py -v` — asserts the backfill
depth is 780, that two `build_state()` calls compare equal bar for bar and position for
position, that the active scenario is baseline, and that one `advance_once` call raises every
instrument's bar count by exactly one. Run before replying, output pasted.

## T6 — Market endpoints

**Objective:** Serve symbol search, the polled quote set and the chart series off the buffer,
so the frontend has prices to display.
**Outcome:** `GET /symbols?q=` fuzzy-matches symbol and name and returns no non-matching
instrument, and with `q` omitted or empty returns the whole universe with each entry's name,
sector, currency and decimal places — this being how the markets table loads its static
metadata once instead of per poll; `GET /quotes?symbols=` returns one quote per requested
symbol in request order
carrying last price, `day change %` as the Definitions define it, and a sparkline;
`GET /candles/{symbol}?tf=` aggregates the buffer into 1m, 5m, 15m and session bars, and an
unknown `tf` is rejected rather than silently defaulted. → serves **O7**
**Reads:** `backend/app/state.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/market.py`
- ADD function `get_symbols`, `get_quotes`, `get_candles` in `backend/app/routers/market.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_market.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_market.py -v` — asserts the fuzzy
match excludes a known non-match, that quote order follows request order, that the returned
day change equals `RingBuffer.day_change_pct` for the same symbol, that each timeframe returns a
bar count consistent with its aggregation factor, and that an unknown `tf` returns 422. Run
before replying, output pasted.

## T7 — Portfolio

**Objective:** Serve the fixed paper positions and their totals, so the summary has something
to show.
**Outcome:** `GET /portfolio` returns every held position with its symbol, quantity and
average entry, and one set of totals — value, return and today's change, using `day change %`
as the Definitions define it. → serves no outcome directly; it is what the summary reads
**Reads:** `backend/app/state.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/portfolio.py`
- ADD function `get_portfolio` in `backend/app/routers/portfolio.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_portfolio.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_portfolio.py -v` — asserts every
starting position appears with a float quantity, and asserts the totals payload carries value,
return and today's change. Run before replying, output pasted.

## T8 — Movers and the macro drivers strip

**Objective:** Rank the quote set into gainers, losers and most active, and expose the five
macro drivers as their own endpoint.
**Outcome:** `GET /movers` returns gainers sorted descending by `day change %`, losers
ascending, and most active descending by session volume — both as the Definitions define them
— with no instrument in both gainers and losers. `GET /macro` returns exactly the five
macro-driver instruments in factor order. → serves **O11**, **O12**
**Reads:** `backend/app/state.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/movers.py`
- ADD function `get_movers`, `get_macro` in `backend/app/routers/movers.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_movers.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_movers.py -v` — asserts each list's
sort direction pairwise, asserts the gainers and losers sets are disjoint, asserts most active
ranks on `RingBuffer.session_volume`, asserts `/macro` returns exactly five in factor order, and
asserts that activating a scenario and ticking changes the membership of at least one list.
Run before replying, output pasted.

## T9 — Scenario endpoints

**Objective:** Expose the scenario library, the active scenario and its activation, deletion
and headlines, so the dropdown has something to drive.
**Outcome:** `GET /scenarios` lists the library; `POST /scenario` sets the active scenario and
stamps `activated_at`; `DELETE /scenario` returns to baseline; `GET /scenario` reports the
active id, its headlines and `activated_at`; bars written before activation are unchanged by
it. → serves **O6**, **O21**
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
factor; the contributions plus residual reconcile with the headline move to within 1e-6.
`GET /impact/portfolio` returns a per-holding breakdown and is never resolved as a symbol
lookup. → serves **O5**, **O8**
**Reads:** `backend/app/state.py`, `backend/app/buffer.py`, `backend/app/models.py`
**Deliverables:**
- CREATE `backend/app/routers/impact.py`
- ADD function `get_portfolio_impact`, `get_symbol_impact` in `backend/app/routers/impact.py` — `get_portfolio_impact` declared first
- ADD var `FACTOR_SENTENCES` in `backend/app/routers/impact.py`
- UPDATE `backend/app/main.py`
- CREATE `backend/tests/test_impact.py`

**Evidenced by:** `cd backend && uv run pytest tests/test_impact.py -v` — asserts the
reconciliation to 1e-6, asserts the contribution ordering, and asserts
`GET /impact/portfolio` returns the portfolio payload rather than a 404 or a symbol payload.
Run before replying, output pasted.

## T11 — OpenAPI hardening and schema emission

**Objective:** Give every route an explicit operation id and a tag, pin the schema version the
generator accepts, and emit the schema to a file by importing the app, so the client generator
needs no running server.
**Outcome:** `backend/openapi.json` exists on disk and declares `"openapi": "3.0.2"`; all 13
operations carry an explicit `operationId` and at least one tag; no operation id matches the
FastAPI default form `<name>_<path>_<method>`. → serves **O7**, **O13**
**Reads:** every router created by T6–T10, `backend/app/main.py`
**Deliverables:**
- UPDATE `backend/app/main.py` — set `app.openapi_version = "3.0.2"`
- ADD function `generate_unique_id(route) -> str` in `backend/app/main.py`
- CREATE `backend/scripts/emit_openapi.py`
- CREATE `backend/openapi.json`
- CREATE `backend/tests/test_openapi.py`

**Evidenced by:** `cd backend && uv run python scripts/emit_openapi.py && uv run pytest
tests/test_openapi.py -v` — asserts the emitted file's `openapi` field is exactly `3.0.2`,
asserts all 12 operations carry an explicit id and a tag, and asserts none matches the
default-name pattern. Run before replying, output pasted.

## T12 — Angular workspace and the generated client

**Objective:** Create the complete Angular workspace — scaffold included — and generate the
typed API client from the emitted schema, committing the output.
**Outcome:** `npm run gen:api` regenerates the client from `backend/openapi.json`; the
generated services cover all 12 operations; `npx ng build` succeeds with no backend process
running and no file created by a later task present. → serves **O13**
**Reads:** `backend/openapi.json`
**Deliverables:**
- CREATE `frontend/package.json` with a `gen:api` script and no UI or styling dependency
- CREATE `frontend/angular.json` — registering `src/styles.css` as the sole global stylesheet
- CREATE `frontend/src/styles.css` — empty; T13 fills it
- CREATE `frontend/tsconfig.json`
- CREATE `frontend/tsconfig.app.json`
- CREATE `frontend/src/index.html`
- CREATE `frontend/src/main.ts` — bootstraps the root standalone component
- CREATE `frontend/src/app/app.config.ts` — provides `HttpClient`, the API base URL and `provideRouter`
- CREATE `frontend/src/app/app.routes.ts` — `/` → dashboard, `/markets` → markets table
- CREATE `frontend/ng-openapi-gen.json`
- CREATE `frontend/src/app/api/`

**Evidenced by:** `cd frontend && npm install && npm run gen:api && npx ng build` — run with
no backend process running, output pasted. Then, from `backend/`,
`grep -o '"operationId": "[^"]*"' openapi.json | sort -u | wc -l` — confirming it is 12. Then,
from `frontend/`, confirm each of those 12 operation ids appears at least once under
`src/app/api/`, output pasted. Count against the contract, not against the generator's output
shape — a per-file `grep -c` reports one line per file and the emitter may write more than one
symbol per operation, so neither yields 13.
**Deferred to human review:** none — this task's outcome is fully established by the build.

## T13 — Design system, shell and dashboard composition

**Objective:** Establish the token file, the shared formatters, the shell and the dashboard
composition, and stub every feature slot as a skeleton, so that the app renders end to end
from this task onward and the nine that follow each fill one file nobody else writes.
**Outcome:** `tokens.css` declares the neutral ramp, the two signal colours, the spacing
scale, the type scale, the radii and the motion durations as custom properties, with body
text meeting 4.5:1 against its background; `format.ts` exports the price, quantity and signed
percentage formatters, the last emitting U+2212 for negatives; the shell renders a toolbar
containing the exact string `Simulated feed` and a two-tab navigation — Dashboard and
Markets — **outside** the `router-outlet`, so no route can render without them; the dashboard
composes all eight feature slots with the portfolio summary first; every slot renders a
skeleton at its final dimensions; and no component source declares a hex colour, a `px` value
or a millisecond duration. → serves **O16**, **O23**, **O24**
**Reads:** `frontend/src/app/app.config.ts`, `.spec-artifacts/design/dashboard-mock.html` —
the approved visual target; `tokens.css` is its `:root` block, copied with the same property
names and values, not a palette of this task's choosing
**Deliverables:**
- CREATE `frontend/src/styles/tokens.css`
- UPDATE `frontend/src/styles.css` — imports `styles/tokens.css`
- CREATE `frontend/src/app/core/format.ts`
- ADD function `formatPrice(value: number, dp: number) -> string`, `formatQuantity(value: number) -> string`, `formatSignedPercent(value: number) -> string` in `frontend/src/app/core/format.ts`
- CREATE `frontend/src/app/shell/shell.component.ts`
- CREATE `frontend/src/app/dashboard/dashboard.component.ts` — composes the eight slots in final order, portfolio summary first; routed at `/`
- CREATE `frontend/src/app/features/markets/markets.component.ts` as a skeleton placeholder; routed at `/markets`
- FOR EACH path in `features/portfolio/portfolio-summary.component.ts`, `features/macro/macro-strip.component.ts`, `features/watchlist/watchlist.component.ts`, `features/movers/movers.component.ts`, `features/scenario/scenario-selector.component.ts`, `features/ticker/headline-ticker.component.ts`, `features/detail/detail.component.ts`, `features/impact/impact-panel.component.ts` — CREATE it under `frontend/src/app/` as a skeleton placeholder at final dimensions. These are the exact paths T15–T24 later `UPDATE`; a different directory breaks eight tasks.
- UPDATE `frontend/src/main.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then
`grep -rnE '#[0-9a-fA-F]{3,6}\b|[0-9]+px|[0-9]+ms' src/app --include='*.ts'` — must return no
match, and the command is run from `frontend/` so the path resolves. Then paste the shell
template showing the tab navigation, the `router-outlet` and the literal `Simulated feed`
outside the outlet, so that it is structurally impossible for a route to render without it.
Then paste `tokens.css`
in full with the computed contrast ratio for body text on the page background, and paste the
`dependencies` block of `package.json`. Then paste `dashboard.component.ts`'s template,
which must show all eight slot selectors with `portfolio-summary` first, and the shell's
template, which must contain the literal `Simulated feed`.
**Deferred to human review:** the shell and the dashboard composition read as
`.spec-artifacts/design/dashboard-mock.html` does — same ramp, same spacing, same type, slots
in the same places. This is a conformance check against an approved file, not a taste
judgement, and it is the one frontend stop before the final walk. Nine tasks are built on
the answer, so it is held before commit.

## T14 — The shared quote poll

**Objective:** Build the single `QuoteService` that polls every symbol in the universe on one
RxJS interval and lets subscribers select from the result, and expose a method to force an
immediate refresh.

*It polls the universe rather than each subscriber's list because the dashboard wants a
handful and the markets table wants all forty. A service that polls per subscriber set
satisfies "one request per subscriber" and still issues two, which is the defect the previous
wording of O14 could not catch.*

**Outcome:** One `/quotes` request goes out per interval regardless of how many components
are mounted or which route is showing; `quotes$(symbols)` returns a selection over that one
stream and issues no request of its own; `refreshNow()` issues a request without waiting out
the interval. → serves **O14**, **O15**
**Reads:** `frontend/src/app/api/`
**Deliverables:**
- CREATE `frontend/src/app/core/quote.service.ts`
- ADD class `QuoteService` in `frontend/src/app/core/quote.service.ts`
- ADD function `allQuotes$()` in `frontend/src/app/core/quote.service.ts` — the single polled stream, every symbol
- ADD function `quotes$(symbols: string[])` in `frontend/src/app/core/quote.service.ts` — a selection over `allQuotes$()`, never a new request
- ADD function `refreshNow()` in `frontend/src/app/core/quote.service.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste `quote.service.ts`
in full and name the operator that multicasts the stream. Exactly one `interval` may appear
in the file, and `quotes$` must derive from `allQuotes$()` rather than call the API — a second
`interval`, or an API call inside `quotes$`, is the defect this evidence exists to expose.
**Deferred to human review:** with the watchlist and the detail view both open, the network
panel shows one `/quotes` request per interval, not two; and selecting a scenario produces a
`/quotes` request sooner than the interval. Recorded `UNVERIFIED`; held for human review
before commit.

## T15 — Portfolio summary

**Objective:** Fill the portfolio summary slot with total value, total return in currency and
%, and today's change.
**Outcome:** The summary shows value, return and today's change as one block, using
`day change %` as the Definitions define it. → serves no outcome directly; it is the
dashboard's first slot
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/format.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/portfolio/portfolio-summary.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component's
template showing the three figures bound through `format.ts`.
**Deferred to human review:** the summary renders value, return and today's change, and sits
above every other element. Recorded `UNVERIFIED`; carried to the final review walk, not held before commit.

## T16 — Macro drivers strip

**Objective:** Fill the macro strip slot with the five macro drivers, so the factor set is
visible as moving prices.
**Outcome:** Five tiles render, one per factor, in factor order, subscribed to the shared
poll rather than polling independently. → serves **O12**, **O14**
**Reads:** `frontend/src/app/core/quote.service.ts`, `frontend/src/app/api/`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/macro/macro-strip.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component and
confirm it injects `QuoteService` and creates no `interval` of its own.
**Deferred to human review:** five tiles render in factor order and update together.
Recorded `UNVERIFIED`; carried to the final review walk, not held before commit.

## T17 — Watchlist

**Objective:** Fill the watchlist slot — symbol, last price, day change %, sparkline — off
the shared poll, flashing green or red on change, and give it a starting set so the dashboard
is not blank on first load.

*It needs one because the markets table took the full universe. Before that the watchlist was
the only list and could not be empty; now it is a curated subset, and nothing has curated it
when the app opens.*
**Outcome:** Each row shows the four fields at a fixed row height, with price and change in
fixed-width decimal-aligned columns that do not move as values change width; a row whose
price rose since the previous poll flashes green and one that fell flashes red, for a single
transition of 120–300ms suppressed under `prefers-reduced-motion`; the sparkline redraws on
each poll without changing its box. On first load the list is the symbols held in
`GET /portfolio` plus `WATCHLIST_EXTRAS`, and it is never empty. → serves **O14**, **O22**
**Reads:** `frontend/src/app/core/quote.service.ts`, `frontend/src/app/api/`,
`frontend/src/app/core/format.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/watchlist/watchlist.component.ts`
- ADD var `WATCHLIST_EXTRAS` in `frontend/src/app/features/watchlist/watchlist.component.ts` — three symbols from sectors that move *against* the holdings, so the dashboard shows disagreement and not only the markets tab
- CREATE `frontend/src/app/features/watchlist/sparkline.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the row styles,
showing the fixed row height, the fixed numeric column widths, `font-variant-numeric:
tabular-nums`, and the `prefers-reduced-motion` block — all as token references.
**Deferred to human review:** a rising row flashes green and a falling row red; no column
boundary moves as prices cross a digit-width change. Recorded `UNVERIFIED`; held for human
review before commit.

## T19 — Instrument detail chart

**Objective:** Fill the detail slot with the line/candle chart, the timeframe toggle and the
scenario activation marker.
**Outcome:** Selecting an instrument renders its series; the toggle switches between 1m, 5m,
15m and session and the bar count changes accordingly; while a scenario is active a labelled
vertical marker is drawn at `activated_at`, and at baseline none is. → serves **O19**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/quote.service.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/detail/detail.component.ts`
- CREATE `frontend/src/app/features/detail/chart.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the marker's
render condition, showing it is driven by `activated_at` being non-null rather than by a
scenario simply being selected.
**Deferred to human review:** the four timeframes return visibly different bar counts; the
marker appears with a scenario active and is absent at baseline. Recorded `UNVERIFIED`; held
for human review before commit.

## T21 — Top movers

**Objective:** Fill the movers slot with gainers, losers and most active as three lists that
repopulate under a scenario.
**Outcome:** Three lists render in the order the API returns, with no client-side re-sorting.
→ serves **O11**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/quote.service.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/movers/movers.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component and
confirm no sort or `orderBy` is applied to the three lists client-side — the API's ordering is
the contract, and re-sorting here would silently mask a backend defect.
**Deferred to human review:** activating the oil supply shock visibly changes the membership
of at least one list. Recorded `UNVERIFIED`; carried to the final review walk, not held before commit.

## T22 — Scenario selector

**Objective:** Fill the scenario selector slot with the always-visible dropdown, the
active-scenario chip and the forced refresh on selection.
**Outcome:** The dropdown lists the library with "Reset to normal" first; selecting an item
POSTs and then calls `refreshNow()` rather than waiting out the interval; the active scenario
shows as a chip. → serves **O15**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/core/quote.service.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- CREATE `frontend/src/app/core/scenario.service.ts`
- UPDATE `frontend/src/app/features/scenario/scenario-selector.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the selection
handler, showing `refreshNow()` is called in the POST's success path and not merely alongside
it, and paste the literal string `Reset to normal` as the first option.
**Deferred to human review:** the watchlist visibly updates on selection without waiting out
the poll interval. Recorded `UNVERIFIED`; carried to the final review walk, not held before commit.

## T23 — Headlines ticker

**Objective:** Fill the ticker slot with the active scenario's canned headlines, so the
causality reads to a non-technical audience.
**Outcome:** The strip shows the active scenario's headlines, and the baseline's while at
baseline. → serves **O21**
**Reads:** `frontend/src/app/core/scenario.service.ts`, `frontend/src/app/api/`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/ticker/headline-ticker.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component and
confirm the headlines come from `GET /scenario` rather than from a copy held in the frontend.
**Deferred to human review:** the strip swaps to the new headlines within one refresh of a
scenario change. Recorded `UNVERIFIED`; carried to the final review walk, not held before commit.

## T24 — Impact panel

**Objective:** Fill the impact slot — plain language first, full attribution behind a
disclosure — and add the peer comparison.
**Outcome:** The default view shows the headline move, at most three bars and one
plain-language sentence per factor, and contains no exposure value such as `oil beta -0.9`;
expanding the detail reveals the full per-factor attribution including exposures; the peer
list ranks same-sector instruments by impact. → serves **O18**
**Reads:** `frontend/src/app/api/`, `frontend/src/app/features/detail/detail.component.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/impact/impact-panel.component.ts`
- CREATE `frontend/src/app/features/impact/peer-comparison.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the default view's
template and confirm it binds no beta or exposure field, and that the bar list is capped at
three in the template rather than by the data happening to be short.
**Deferred to human review:** the collapsed panel reads as plain language with no exposure
values; expanding reveals the full attribution; peers are same-sector and ranked by impact.
Recorded `UNVERIFIED`; carried to the final review walk, not held before commit.

## T26 — Markets table

**Objective:** Fill the `/markets` route with the full-universe table — every instrument,
grouped by sector, each group headed by its aggregate day change — so that a scenario reads
as market-wide rather than as something confined to a curated watchlist.

*This is the surface the factor model is visible on. The universe is built so that scenarios
disagree within a sector as well as between sectors — under an oil spike a producer gains
while an airline suffers, which a coarse sector rule would get wrong. Scattered through a flat
list that is invisible. Grouped, with energy rising above travel as the shock lands, it needs
no explanation.*

**Outcome:** The table lists every instrument the universe holds, grouped by sector, each
group headed by its aggregate day change; sector groups order by that aggregate and rows
order within a group by the selected column; the header row is sticky and the body scrolls
inside a pane whose height does not change and whose scroll position survives a poll; rows
track by symbol under `OnPush`; and static metadata comes from one `GET /symbols` at load
rather than from each poll. → serves **O14**, **O22**, **O25**
**Reads:** `frontend/src/app/core/quote.service.ts`, `frontend/src/app/api/`,
`frontend/src/app/core/format.ts`, `frontend/src/styles/tokens.css`
**Deliverables:**
- UPDATE `frontend/src/app/features/markets/markets.component.ts`
- CREATE `frontend/src/app/features/markets/market-row.component.ts`

**Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component
showing `ChangeDetectionStrategy.OnPush`, a `trackBy` keyed on symbol, the single
`GET /symbols` call outside the poll subscription, and the pane's fixed-height style with the
sticky header — all as token references.
**Deferred to human review:** the oil shock reorders the sector groups so energy sits above
travel; switching to this tab and back does not add a second poll; and the pane's scroll
position survives a poll without the pane resizing. Recorded `UNVERIFIED`; carried to the
final review walk, not held before commit.
