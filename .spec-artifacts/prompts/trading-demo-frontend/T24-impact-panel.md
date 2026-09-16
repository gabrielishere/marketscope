---
name: impact-panel
description: The impact panel — plain language first, full attribution behind a disclosure, and the peer comparison.
task: T24
model: claude-opus-5
---

# Objective

Fill the impact slot — plain language first, full attribution behind a disclosure — and add
the peer comparison. **This is the surface that turns a number into an explanation**, and the
one place the demo risks reading as a quant tool rather than a product.

# Outcome

The default view shows the headline move, at most three bars and one plain-language sentence
per factor, and contains no exposure value such as `oil beta -0.9`. Expanding the detail
reveals the full per-factor attribution including exposures. The peer list ranks same-sector
instruments by impact.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste the default
  view's template and confirm it binds **no** beta or exposure field, and that the bar list is
  capped at three **in the template** rather than by the data happening to be short. Then
  paste the expression the peer list renders from, showing it reads the response's `peers`
  field rather than issuing a request per peer.
- **Deferred to human review:** the collapsed panel reads as plain language with no exposure
  values; expanding reveals the full attribution; peers are same-sector and ranked by impact.

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
- **The default view is for someone who does not know what a beta is.** `oil beta -0.9`
  appearing there is the specific failure O18 exists to prevent — it is named in the outcome
  as the example to avoid.
- The sentences arrive pre-written on `FACTOR_SENTENCES` from the backend, one per factor,
  carrying no beta and no exposure value. Render them; do not compose your own.
- `SymbolImpact.peers` is a **field on the response**, already ranked. Do not issue one
  `/impact/{symbol}` call per peer.
- The cap of three bars is in the template because "the data happened to be short" is not a
  cap — a fourth factor with a real contribution would appear.
- The mockup shows the collapsed state as a large signed percentage, three sentences, and
  three bars diverging from a centre line; the expanded state as a plain table including the
  exposure column.

# Deliverables

- **UPDATE** `frontend/src/app/features/impact/impact-panel.component.ts`
- **CREATE** `frontend/src/app/features/impact/peer-comparison.component.ts`

# Instructions

1. UPDATE `frontend/src/app/features/impact/impact-panel.component.ts`
2. CREATE `frontend/src/app/features/impact/peer-comparison.component.ts`


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
- The disclosure is a native `<details>` or an equivalent that works without a UI package.

# Response format

One line per deliverable, done or not done. Then the outcome clauses with their evidence and
the deferred items reported as deferred. Then the build output, the default view's template,
and the peer list's binding expression.
