# Full Stack Application Demo — Feature Specification

> **These notes were constructed during a call.** They are working notes taken while the
> requirements were being established — not a finished document, and not the specification.
>
> Their job was to capture what the thing needed to be, in the room, before any of it had
> been decided properly. Everything here was then migrated into the two specifications under
> `.spec-artifacts/specs/`, which are what the build actually ran from.
>
> Read this for **what was asked for**; read the specs for **what was built**. Where the two
> differ, the specs are authoritative and the difference is deliberate — several things here
> were cut, narrowed or settled differently once they were written down precisely, and those
> changes are recorded in `.spec-artifacts/decisions/`.

A trader-facing dashboard for observing price fluctuations of underlyings, in the
vein of Trading 212. Scope is a demo: credible-looking and complete in its core
flows, deliberately not production.

## Stack

- **Backend:** FastAPI (Python), Pydantic response models, no database
- **Frontend:** Angular (standalone components, RxJS, `HttpClient`)
- **Styling:** hand-rolled CSS, dark theme, no UI or styling packages
- **Transport:** HTTP polling (no WebSockets)
- **Contract:** OpenAPI, emitted by FastAPI and used to generate the Angular client

## Repository layout

```
/backend    FastAPI app, models, instrument and scenario data
/frontend   Angular workspace
/docs       spec
```

Frontend and API are cross-origin in dev — either `CORSMiddleware` or an Angular
dev proxy is required for requests to reach the API at all.

## Core features

- **Watchlist** — symbol, last price, day change %, sparkline
- **Instrument detail** — line/candle chart with timeframe toggle
- **Symbol search** — fuzzy match over the instrument list
- **Paper portfolio** — positions, average entry, unrealised P&L
- **Scenario selector** — dropdown of world events that visibly change the data

## Retail features

The reference product is built for retail investors, not professional traders:
long horizon, small balances, portfolio-level rather than instrument-level
attention. Three auxiliary features follow from that.

- **Portfolio summary** — total value, total return in currency and %, and
  today's change, displayed prominently above everything else. This is what a
  retail user opens the app to see.
- **Invest by amount** — the trade ticket takes "invest £100", not "buy 0.34
  shares". Quantity is derived from amount ÷ price.
- **Top movers** — gainers, losers and most active, as a sort over the quote
  set. Under a scenario this repopulates visibly, which makes the event read as
  market-wide rather than confined to the watchlist.

Invest-by-amount requires fractional quantities, so position size is a float
rather than an integer.

## Instrument universe

Roughly 25–40 equities across 6–8 sectors, chosen so that scenarios produce
visible disagreement within sectors as well as between them, plus the five
macro drivers. Loaded at startup with sector tags and factor exposures.

## State

No database. Nothing the audience sees depends on where state lives, and an
in-process store gives a deterministic reset on every restart — the same
starting portfolio each run, with no seed file to seed or stale state from an
earlier session.

| Data | Where it lives |
| --- | --- |
| Instruments, sectors, factor betas | JSON in the repo, loaded at startup |
| Scenario definitions | JSON in the repo, loaded at startup |
| Price bars and factor contributions | Bounded in-memory ring buffer |
| Portfolio, cash, trades | In-process |
| Active scenario | In-process |

Instruments and scenarios are config rather than data: betas get tweaked
constantly during calibration, and a text file is the right place for that.

Price history lives only in the ring buffer and is not persisted. The buffer is
capped and discards its oldest bars, so memory is bounded however long the demo
runs; a ticks table would grow without limit and buy nothing.

If a persistence layer is ever needed, swapping the in-process store for SQLite
behind the same accessors is about an hour. Do not abstract for it in advance.

## API surface

| Endpoint | Purpose |
| --- | --- |
| `GET /symbols?q=` | Symbol search |
| `GET /quotes?symbols=AAPL,TSLA` | Watchlist prices (polled endpoint) |
| `GET /candles/{symbol}?tf=1d` | Chart series |
| `GET /portfolio` | Paper positions plus summary totals |
| `POST /portfolio/trade` | Mutate paper positions; body takes an amount |
| `GET /movers` | Top gainers, losers, most active |
| `GET /macro` | Macro drivers strip: one instrument per factor |
| `GET /scenarios` | Scenario library: id, name, description |
| `GET /scenario` | Active scenario + `activated_at` |
| `POST /scenario` | Activate `{id}` |
| `DELETE /scenario` | Reset to baseline |
| `GET /impact/{symbol}` | Scenario impact breakdown for one instrument |
| `GET /impact/portfolio` | Scenario impact by holding |

## API contract

FastAPI generates the OpenAPI schema from the route signatures and Pydantic
models, served at `/openapi.json` with interactive docs at `/docs` and
`/redoc`. No hand-written schema.

The Angular client is generated from that schema rather than written by hand, so
the backend models are the single source of truth. Changing a response model and
regenerating surfaces every affected call site as a compile error — worth having
while the data shapes are still moving.

- Generator: `ng-openapi-gen` (npm, Angular-native, no Java toolchain). Wire it
  to an `npm run gen:api` script and commit the output so the frontend builds
  without the backend running.
- Every route declares a `response_model` and a tag; tags become the generated
  service boundaries.
- Set explicit `operation_id`s, or a `generate_unique_id_function`. The default
  derives names like `get_quotes_quotes_get`, which the generated client
  inherits verbatim.
- Model scenario ids as an enum so they generate as a TypeScript union rather
  than a bare string.

One known friction point: FastAPI emits OpenAPI 3.1 by default, and some
generators still expect 3.0. If the generator objects, pin
`app.openapi_version = "3.0.2"`.

## Data refresh

Angular polls `/quotes` on an RxJS interval (~2–3s) via a shared `QuoteService`,
so the watchlist and detail view share a single poll. The server decouples the
client poll rate from any upstream refresh rate:

```
Angular polls  →  FastAPI reads the buffer  ←  tick loop advances prices
    2-3s                                              1s
```

Reads are served from the current state of the tick loop, so the API is a
read-off-the-buffer operation with no upstream to wait on and no rate limits.
Client poll rate and tick rate are independent: polling slower than the tick
loop simply skips bars, and polling faster returns the same bar twice.

## Scenarios

The user picks a world event from a dropdown and the presented data changes
accordingly. This is the feature the demo is built around.

### Simulation core

Prices advance on a **server-side tick loop**, not computed from the clock on
request. One tick per second of wall time, representing one minute of market
time. Each tick every instrument takes a log return, its price updates
multiplicatively, and the bar is appended to a bounded ring buffer.

```
r_i,t     = Σ_k beta_ik · f_k,t  +  σ_i · vol_mult_t · ε_i,t
price_i,t = price_i,t-1 · exp(r_i,t)
```

- `beta_ik` — instrument *i*'s exposure to factor *k*, hand-assigned
- `f_k,t` — factor *k*'s return this tick, set by the active scenario
- `ε_i,t` — idiosyncratic noise from a run-seeded PRNG, drawn once per tick

Returns are in log space, so prices cannot go negative however severe the
scenario or however long the session runs.

### Factors and scenarios

Factors: market, rates/duration, oil, USD, credit spread.

Sector tags alone would not be realistic — under an oil spike a producer gains
while an airline suffers, and a coarse sector rule matches both. Exposures
separate them.

A scenario sets, **per factor**, a `shock` (one-off log return at activation), a
`drift` (per-tick log return) and a `half_life` (decay of both toward zero;
unset means a persistent regime change). It carries one scenario-level
`vol_mult`, set higher on downside scenarios than upside ones.

```
oil_shock:
  oil:      shock +0.16   drift +0.0004   half_life 40 ticks
  market:   shock -0.01   drift -0.0001
  credit:   shock +0.02
  vol_mult: 1.6
```

Drift is per-factor rather than per-scenario, so instruments drift in opposite
directions according to their exposures — the oil producer up while the airline
bleeds. Adding a scenario is a data entry, not a code change.

Correlation falls out of this for free — instruments with similar loadings
co-move — so no explicit correlation matrix is needed.

### History

The ring buffer **is** the history. Past bars are written once and never
recomputed, so activating a scenario changes only subsequent ticks: the chart
shows an inflection at the activation tick with everything before it untouched.
There is no retroactive rewriting to defend against and no need to anchor
regimes in time.

At startup the loop runs roughly 780 ticks at full speed — about two sessions —
so charts have history before anyone looks at them. The buffer caps at ~5000
bars per instrument and discards the oldest, so it is bounded and can run all
day.

Chart timeframes (1m, 5m, 15m, session) are aggregations over the buffer. Long
horizons are omitted deliberately: nothing interesting happened in synthetic
history before the demo started.

`Today's change` means since the start of the current session in market time,
which the backfill establishes.

### Attribution

Each tick stores its per-factor contributions alongside the price. Impact over
any window is the sum of the stored contributions across it, so a breakdown
reconciles **exactly** with the realised price move by construction, with the
idiosyncratic term appearing as a residual rather than as unexplained drift
between the chart and the panel beside it.

### Calibration

Betas are hand-assigned at coarse granularity, from {−1, −0.5, 0, +0.5, +1}, by
judgment rather than estimated from history. This is a plausible-looking demo
model, not a risk model, and the spec should not be read as claiming otherwise.

Scenario magnitudes are calibrated against historical analogues:

| Scenario | Analogue | Rough magnitude |
| --- | --- | --- |
| 25bp surprise hike | 2022 Fed cycle | market −1 to −2%, long-duration growth −3 to −4%, banks +1 to +2% |
| Oil supply shock | 2022 Russia/Ukraine | producers +6 to +10%, airlines −4 to −8%, broad −1% |
| Geopolitical escalation | Feb 2022 | defence +3 to +6%, oil +3 to +5%, broad −2% |
| Flash crash | Feb 2018 / Aug 2024 | −5 to −8% intraday, partial recovery via a short `half_life` |

### Macro drivers strip

One instrument per factor, pinned along the top of the dashboard: an index ETF
(market), a bond ETF (rates), WTI (oil), a dollar index (USD), a high-yield
credit ETF (credit). Each carries unit exposure to its own factor and zero to
the others, so the strip **is** the factor set made visible.

This makes the causal chain legible in a single view — oil spikes in the strip,
airlines bleed in the watchlist below it. The factors stop being abstract betas
and become moving things the viewer can watch. Costs five extra instruments.

### Investigating an entity

Selecting an instrument while a scenario is active opens an impact panel
explaining what the event did to it.

- Headline move since activation, read off the buffer
- Contribution breakdown — which factors drove the move, largest first, summed
  from the stored per-tick contributions and therefore exactly reconciling with
  the headline
- One plain-language sentence per factor, templated: "Higher fuel costs, which
  airlines cannot immediately pass through to ticket prices."
- Peer comparison — same sector ranked by impact, which is what makes "why is
  Shell up while TUI is down" land
- Chart with the activation marker, before and after
- Position impact in currency terms, if held

The same decomposition runs at portfolio level, contribution by holding, feeding
the portfolio summary.

**Presentation constraint.** The underlying model is a factor decomposition, but
the surface is retail. The default view is plain language and at most two or
three bars; the full per-factor attribution is an expandable detail. Exposure
values such as "oil beta −0.9" are a risk-desk artifact and do not belong on the
headline view.

### State

A single server-side active scenario, global to the instance. Per-session
scoping is a later variant if two people ever need to present simultaneously.

### Frontend

- Dropdown in the top toolbar, always visible; active scenario shown as a chip.
- On select, POST and then force an immediate `QuoteService` refresh rather than
  waiting out the poll interval — otherwise the feature does not feel causal.
- Vertical marker on the detail chart at `activated_at`, labelled.
- Row flash green/red on price change.
- "Reset to normal" as the first item in the dropdown.

### Library

Baseline · Central bank rate hike · Oil supply shock · Tech earnings beat ·
Geopolitical escalation · Recession print · Flash crash.

Six or seven, chosen so they visibly disagree with each other — the demo lands
when energy is green while airlines are red.

### Labelling

With scenarios the feed is unambiguously fabricated. Real tickers are fine to
use, but a "Simulated feed" label in the header is required, not optional.

### Out of scope for this feature

User-authored scenarios, timed multi-stage event sequences, estimating betas
from historical data.

## Optional — pick at most one

- Price alerts, evaluated on the same poll cycle
- Two or three canned headlines per scenario in a ticker strip — cheap, and it
  makes the causality legible to a non-technical audience

## Open questions

- **Push transport.** Not required now. If sub-poll latency is ever needed, the
  step is SSE (`sse-starlette` + `EventSource`), not WebSockets.

## Explicitly out of scope

WebSockets, offline support, Redis, multi-service deployment, options/greeks,
customisable multi-pane layouts, order matching against a simulated book.
