---
name: portfolio-summary
description: Fill the portfolio summary slot with value, return and today's change.
task: T15
model: claude-sonnet-5
---

# Objective

Fill the portfolio summary slot with total value, total return in currency and percent, and
today's change. It is the dashboard's first element and the first figure an audience reads.

# Outcome

The summary shows value, return and today's change as one block, using `day change %` as the
Definitions define it.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component's
  template showing the three figures bound through `format.ts`.
- **Deferred to human review:** the summary renders value, return and today's change, and sits
  above every other element.

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
- There is one currency across the universe and no FX rate, so this is **one block of
  figures**, not one per currency. `GET /portfolio` returns a single `totals` object.
- Return and today's change are signed, and their sign is the only thing that may carry
  colour.
- The mockup's summary is a row of four labelled figures — value, total return, today, cash —
  with the value largest. Match it.

# Deliverables

- **UPDATE** `frontend/src/app/features/portfolio/portfolio-summary.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/portfolio/portfolio-summary.component.ts`


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
- Read `GET /portfolio` once on init. It does not change between ticks in a way this surface
  needs to poll for.

# Response format

One line per deliverable, done or not done. Then the outcome with its evidence and the
deferred item reported as deferred. Then the build output and the component's template.
