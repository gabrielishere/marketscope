---
name: top-movers
description: Fill the movers slot with gainers, losers and most active, rendered in API order.
task: T21
model: claude-sonnet-5
---

# Objective

Fill the movers slot with gainers, losers and most active as three lists that repopulate under
a scenario.

# Outcome

Three lists render in the order the API returns, with no client-side re-sorting.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component and
  confirm no sort, `orderBy` or comparator is applied to the three lists client-side.
- **Deferred to human review:** activating the oil supply shock visibly changes the membership
  of at least one list.

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
- **The API's ordering is the contract.** `GET /movers` returns gainers descending by day
  change, losers ascending, most active descending by session volume. Re-sorting here would
  silently mask a backend defect — the list would look right while the API was wrong.
- The membership change under a scenario is the demo's payoff on this surface. It comes from
  the backend; this component's job is not to interfere with it.
- Three labelled groups in one panel, as the mockup shows — not three separate panels.

# Deliverables

- **UPDATE** `frontend/src/app/features/movers/movers.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/movers/movers.component.ts`


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
- Subscribe through `QuoteService` for prices. No `interval` of your own.

# Response format

One line per deliverable, done or not done. Then the outcome with its evidence and the
deferred item reported as deferred. Then the build output and the component in full.
