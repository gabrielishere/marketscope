---
name: watchlist
description: Fill the watchlist — symbol, price, day change, sparkline — off the shared poll, flashing on change.
task: T17
model: claude-opus-5
---

# Objective

Fill the watchlist slot — symbol, last price, day change %, sparkline — off the shared poll,
flashing green or red on change, and give it a starting set so the dashboard is not blank on
first load.

# Outcome

Each row shows the four fields at a fixed row height, with price and change in fixed-width
decimal-aligned columns that do not move as values change width. A row whose price rose since
the previous poll flashes green and one that fell flashes red, for a single transition of
120–300ms suppressed under `prefers-reduced-motion`. The sparkline redraws on each poll
without changing its box. On first load the list is the symbols held in `GET /portfolio` plus
`WATCHLIST_EXTRAS`, and it is never empty.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the row styles,
  showing the fixed row height, the fixed numeric column widths,
  `font-variant-numeric: tabular-nums`, and the `prefers-reduced-motion` block — all as token
  references. Then paste `WATCHLIST_EXTRAS` and the expression that unions it with the
  portfolio's symbols.
- **Deferred to human review:** a rising row flashes green and a falling row red; no column
  boundary moves as prices cross a digit-width change; the sparkline's box does not resize as
  it redraws.

# Task context

- Anything below restated from the spec reproduces `## Definitions`, `## Visual design` and
  `## Frontend evidence` in `.spec-artifacts/specs/trading-demo-frontend.md`. **If this prompt
  and the spec disagree, the spec governs**, and the disagreement is a defect to report rather
  than one to resolve. Read that file if a term here is thinner than the work needs.
- **You have no browser.** An instruction to report what a rendered page does is one you
  cannot carry out, and you are required to say so rather than invent an observation. Every
  behavioural claim in this task is listed under *Deferred to human review* and is **not**
  yours to assert. Report it as deferred.
- **`.spec-artifacts/design/dashboard-mock.html` is the approved visual target.** Read it and
  find your component in it. Yours must read as its counterpart does: same ramp, same spacing,
  same type scale, same density. Where this prompt and the mockup differ on an appearance, the
  mockup governs.
- Every value is a `var(--token)` reference from `frontend/src/styles/tokens.css`. No raw hex,
  `px` or `ms` appears in a component — O23 is evidenced by a grep over `src/app`.
- Figures render through `frontend/src/app/core/format.ts` in a `tabular-nums` face. Never
  format a number inline; never let a column's width depend on its value.
- **It needs a starting set** because the markets table took the full universe. The watchlist
  is now a curated subset, and nothing has curated it when the app opens.
- `WATCHLIST_EXTRAS` is three symbols from sectors that move **against** the holdings, so the
  dashboard shows disagreement rather than everything moving together. Under an oil shock that
  is what makes the factor model legible on this surface rather than only on the markets tab.
- The flash is the single most noticeable motion in the app. One background transition, no
  easing flourish, and nothing at all under `prefers-reduced-motion`.
- **No layout shift on poll** is the highest-value visual rule here: a list that jitters every
  two seconds reads as broken however good the palette is.

# Deliverables

- **UPDATE** `frontend/src/app/features/watchlist/watchlist.component.ts`
- **ADD** var `WATCHLIST_EXTRAS` in the same file — three symbols moving against the holdings
- **CREATE** `frontend/src/app/features/watchlist/sparkline.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/watchlist/watchlist.component.ts`
2. ADD var `WATCHLIST_EXTRAS` in `frontend/src/app/features/watchlist/watchlist.component.ts`
3. CREATE `frontend/src/app/features/watchlist/sparkline.component.ts`


# Constraints

- Standalone component, **inline** template and styles. No separate `.html` or `.css` file —
  the grep evidencing O23 covers `*.ts` only.
- Every colour, size, space, radius and duration is a token reference.
- Colour carries signal only: green and red mean direction and nothing else. Everything else
  comes from the neutral ramp.
- Numeric columns are fixed-width and decimal-aligned, so a price crossing a digit width moves
  no boundary.
- Declare a loading state and an empty state. A pane awaiting its first response must not be
  blank.
- Subscribe through `QuoteService.quotes$`. No `interval` of your own.
- The sparkline is `list[float]` — recent closes, oldest first, latest last. Prices, not
  returns, drawn on their own scale.
- The list is never empty. If `GET /portfolio` fails, the extras still render.

# Response format

One line per deliverable, done or not done. Then the outcome clauses with their evidence and
the deferred items reported as deferred. Then the build output, the row styles, and
`WATCHLIST_EXTRAS` with one line saying which sector each symbol is in and which holding it
moves against.
