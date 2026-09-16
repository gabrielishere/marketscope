---
name: markets-table
description: The full-universe markets table, grouped by sector, ordered by aggregate day change.
task: T26
model: claude-opus-5
---

# Objective

Fill the `/markets` route with the full-universe table — every instrument, grouped by sector,
each group headed by its aggregate day change — so that a scenario reads as market-wide rather
than as something confined to a curated watchlist.

**This is the surface the factor model is visible on.** Under an oil spike a producer gains
while an airline suffers; scattered through a flat list that is invisible, but grouped, with
energy rising above travel as the shock lands, it needs no explanation.

# Outcome

The table lists every instrument the universe holds, grouped by sector, each group headed by
its aggregate day change. Sector groups order by that aggregate and rows order within a group
by the selected column. The header row is sticky and the body scrolls inside a pane whose
height does not change and whose scroll position survives a poll. Rows track by symbol under
`OnPush`. Static metadata comes from one `GET /symbols` at load rather than from each poll.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component
  showing `ChangeDetectionStrategy.OnPush`, a `trackBy` keyed on symbol, the single
  `GET /symbols` call **outside** the poll subscription, and the pane's fixed-height style
  with the sticky header — all as token references. Then paste the expression that computes a
  sector's aggregate and the one that orders the groups by it.
- **Deferred to human review:** the oil shock reorders the sector groups so energy sits above
  travel; switching to this tab and back does not add a second poll; the pane's scroll
  position survives a poll without the pane resizing.

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
- **`trackBy` and `OnPush` are what stop the table rebuilding every poll.** Without them 45
  rows re-render twice a second, the scroll position jumps, and the demo looks broken on the
  one surface that most needs to look solid.
- Static metadata — name, sector, currency, decimals — comes from `GET /symbols` with `q`
  omitted, called **once at load**. The poll carries only prices. Fetching metadata per poll
  is the defect the evidence is worded to catch.
- The pane has a fixed height with the body scrolling inside it, so the page does not grow and
  the header stays put.
- The mockup shows sector group headers as a sticky secondary row carrying the sector name and
  its aggregate, with rows beneath in the neutral ramp.

# Deliverables

- **UPDATE** `frontend/src/app/features/markets/markets.component.ts`
- **CREATE** `frontend/src/app/features/markets/market-row.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/markets/markets.component.ts`
2. CREATE `frontend/src/app/features/markets/market-row.component.ts`


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
- Subscribe through `QuoteService.quotes$`. Switching tabs must not create a second poll.

# Response format

One line per deliverable, done or not done. Then the outcome clauses with their evidence and
the deferred items reported as deferred. Then the build output, the component showing
`OnPush`, `trackBy`, the single `GET /symbols` call and the pane style, and the two ordering
expressions.
