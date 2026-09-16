---
name: scenario-selector
description: The always-visible scenario dropdown, the active chip, and the forced refresh on selection.
task: T22
model: claude-opus-5
---

# Objective

Fill the scenario selector slot with the always-visible dropdown, the active-scenario chip and
the forced refresh on selection. **This is the control the entire demo is driven from** — it
is the thing a presenter clicks.

# Outcome

The dropdown lists the library with "Reset to normal" first. Selecting an item POSTs and then
calls `refreshNow()` rather than waiting out the interval. The active scenario shows as a
chip.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the selection
  handler, showing `refreshNow()` is called **in the POST's success path** and not merely
  alongside it. Then paste the literal string `Reset to normal` as the first option.
- **Deferred to human review:** the watchlist visibly updates on selection without waiting out
  the poll interval; the chip shows the active scenario's name.

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
- **The refresh must follow the POST, not race it.** Calling `refreshNow()` beside the POST
  rather than in its success path fetches quotes the server has not yet changed, and the
  audience sees nothing happen — then a delayed change three seconds later. That reads as a
  broken demo and it is the defect this evidence exists to catch.
- "Reset to normal" is the plain-language label for returning to baseline. It is first because
  it is the state a presenter returns to between scenarios.
- `DELETE /scenario` returns to baseline; `POST /scenario` activates one.
- The chip is always visible, including at baseline, and the mockup shows it in the toolbar
  with a coloured dot.
- `scenario.service.ts` is shared: T23's ticker reads the active scenario through it.

# Deliverables

- **CREATE** `frontend/src/app/core/scenario.service.ts`
- **UPDATE** `frontend/src/app/features/scenario/scenario-selector.component.ts`

# Instructions

1. CREATE `frontend/src/app/core/scenario.service.ts`
2. ADD class `ScenarioService` in `frontend/src/app/core/scenario.service.ts`
3. UPDATE `frontend/src/app/features/scenario/scenario-selector.component.ts`


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
- Never hold a client-side copy of the library or the headlines. Both come from the API.

# Response format

One line per deliverable, done or not done. Then the outcome clauses with their evidence and
the deferred items reported as deferred. Then the build output, the selection handler, and the
first option's literal text.
