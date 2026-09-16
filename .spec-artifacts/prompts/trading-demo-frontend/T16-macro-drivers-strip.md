---
name: macro-drivers-strip
description: Fill the macro strip with five tiles, one per factor, in factor order, off the shared poll.
task: T16
model: claude-sonnet-5
---

# Objective

Fill the macro strip slot with the five macro drivers, so the factor set is visible as moving
prices rather than as an abstraction.

# Outcome

Five tiles render, one per factor, in factor order, subscribed to the shared poll rather than
polling independently.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component and
  confirm it injects `QuoteService` and creates no `interval` of its own.
- **Deferred to human review:** five tiles render in factor order and update together.

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
- **Factor order** is the order of the factor keys: `market`, `rates`, `oil`, `usd`, `credit`.
  `GET /macro` returns its five in that order — render them as returned and do not sort.
- The keys are identifier-style. For display the tiles read **Market, Rates, Oil, USD,
  Credit**, as the mockup shows. Do not print the raw key.
- The tiles are how an audience sees the shock land: under an oil scenario the Oil tile moves
  hard and the others barely. That legibility is the point of the strip.

# Deliverables

- **UPDATE** `frontend/src/app/features/macro/macro-strip.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/macro/macro-strip.component.ts`


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
- Subscribe to `QuoteService`. A component that polls on its own breaks O14, which is checked
  by counting requests in the browser, not here.

# Response format

One line per deliverable, done or not done. Then the outcome with its evidence and the
deferred item reported as deferred. Then the build output and the component in full.
