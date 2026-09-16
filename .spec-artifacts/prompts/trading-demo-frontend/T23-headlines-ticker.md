---
name: headlines-ticker
description: Fill the ticker with the active scenario's headlines, so the causality reads in plain language.
task: T23
model: claude-sonnet-5
---

# Objective

Fill the ticker slot with the active scenario's canned headlines, so the causality reads to a
non-technical audience. **This is how the demo explains itself** — the prices move, and the
strip says why in words anyone understands.

# Outcome

The strip shows the active scenario's headlines, and the baseline's while at baseline.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the component and
  confirm the headlines come from `GET /scenario` rather than from a copy held in the
  frontend.
- **Deferred to human review:** the strip swaps to the new headlines within one refresh of a
  scenario change.

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
- Baseline carries headlines like any other scenario, so the strip is never empty. Do not
  special-case it.
- The headlines are written for a non-technical audience. Render them as they arrive — no
  truncation that cuts a sentence, no symbol substitution, no jargon added.
- The mockup shows them as one line separated by bullet marks, quiet against the page, with
  the first slightly brighter. It is context, not a signal, so it takes no green or red.
- Read the active scenario through `ScenarioService`, which T22 creates.

# Deliverables

- **UPDATE** `frontend/src/app/features/ticker/headline-ticker.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/ticker/headline-ticker.component.ts`


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
- No client-side copy of any headline. A stale copy is worse than an empty strip.

# Response format

One line per deliverable, done or not done. Then the outcome with its evidence and the
deferred item reported as deferred. Then the build output and the component in full.
