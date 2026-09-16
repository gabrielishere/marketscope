---
name: instrument-detail-chart
description: Fill the detail slot with the chart, the timeframe toggle and the scenario activation marker.
task: T19
model: claude-opus-5
---

# Objective

Fill the detail slot with the line chart, the timeframe toggle and the scenario activation
marker. **The marker is the demo's visual payoff** — it is where an audience sees the world
event hit and the line change.

# Outcome

Selecting an instrument renders its series. The toggle switches between 1m, 5m, 15m and
session and the bar count changes accordingly. While a scenario is active a labelled vertical
marker is drawn at `activated_at`, and at baseline none is.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the marker's
  render condition, showing it is driven by **`activated_at` being non-null** rather than by a
  scenario simply being selected. Then paste the timeframe toggle's handler showing each of
  the four values is passed through to `GET /candles`.
- **Deferred to human review:** the four timeframes return visibly different bar counts; the
  marker appears with a scenario active and is absent at baseline; the marker is labelled with
  the scenario's name.

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
- `activated_at` is the tick index the active scenario was activated at. It arrives on
  `GET /scenario` and is `null` at baseline. It is **not** a field on a bar.
- The distinction the evidence asks for is real: a scenario being *selected* in a dropdown and
  a scenario being *active on the server* are different states, and only the second has an
  activation tick to draw at.
- Chart timeframes are exactly 1m, 5m, 15m and session.
- The mockup draws the marker as a dashed vertical rule with the scenario's name beside it, in
  a neutral tone — it is an annotation, not a signal, so it takes no green or red.
- Draw with inline SVG. No charting library: no UI or styling package is permitted.

# Deliverables

- **UPDATE** `frontend/src/app/features/detail/detail.component.ts`
- **CREATE** `frontend/src/app/features/detail/chart.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/detail/detail.component.ts`
2. CREATE `frontend/src/app/features/detail/chart.component.ts`


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
- The chart's box does not resize as the series updates.

# Response format

One line per deliverable, done or not done. Then the outcome clauses with their evidence and
the deferred items reported as deferred. Then the build output, the marker's render condition,
and the timeframe handler.
