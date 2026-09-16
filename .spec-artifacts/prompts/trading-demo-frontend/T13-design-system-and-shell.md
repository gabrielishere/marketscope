---
name: design-system-and-shell
description: Establish the token file from the approved mockup, the formatters, the shell and the dashboard composition, and stub eight feature slots.
task: T13
model: claude-opus-5
---

# Objective

Establish the token file, the shared formatters, the shell and the dashboard composition, and
stub every feature slot as a skeleton, so the app renders end to end from this task onward and
the nine that follow each fill one file nobody else writes.

**This is the task the whole visual system rests on.** Nine components are built against what
you produce here, and it is the one frontend task held for human review before commit.

# Outcome

`tokens.css` declares the neutral ramp, the two signal colours, the spacing scale, the type
scale, the radii and the motion durations as custom properties, with body text meeting 4.5:1
against its background. `format.ts` exports the price, quantity and signed-percentage
formatters, the last emitting U+2212 for negatives. The shell renders a toolbar containing the
exact string `Simulated feed` and a two-tab navigation — Dashboard and Markets — **outside**
the `router-outlet`, so no route can render without them. The dashboard composes all eight
feature slots with the portfolio summary first. Every slot renders a skeleton at its final
dimensions. No component source declares a hex colour, a `px` value or a millisecond duration.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then
  `grep -rnE '#[0-9a-fA-F]{3,6}\b|[0-9]+ms|font-size: *[0-9]+px|(padding|margin|gap)[a-z-]*: *[^;]*[0-9]+px' src/app --include='*.ts' | grep -v '/api/'`
  — must return no match, run from `frontend/` so the path resolves. Then paste `tokens.css` in full with
  the computed contrast ratio for body text on the page background, and the `dependencies`
  block of `package.json`. Then paste the shell's template, showing the tab navigation, the
  `router-outlet`, and the literal `Simulated feed` **outside** the outlet — so that it is
  structurally impossible for a route to render without it. Then paste
  `dashboard.component.ts`'s template, which must show all eight slot selectors with
  `portfolio-summary` first.
- **Deferred to human review:** the shell and the dashboard composition read as
  `.spec-artifacts/design/dashboard-mock.html` does — same ramp, same spacing, same type,
  slots in the same places. A conformance check against an approved file, not a taste
  judgement. Nine tasks are built on the answer, so this is held before commit.

# Task context

- Anything below restated from the spec reproduces `## Definitions`, `## Visual design` and
  `## Frontend evidence` in `.spec-artifacts/specs/trading-demo-frontend.md`. **If this prompt
  and the spec disagree, the spec governs**, and the disagreement is a defect to report rather
  than one to resolve. Read that file if a term here is thinner than the work needs.
- **You have no browser.** An instruction to report what a rendered page does is one you
  cannot carry out, and you are required to say so rather than invent an observation. Every
  behavioural claim in this task is listed under *Deferred to human review* and is **not**
  yours to assert. Report it as deferred.
- **`.spec-artifacts/design/dashboard-mock.html` is the approved visual target.** It is a
  static two-route reference — no framework, no data, no polling — showing the oil-shock
  scenario active. Read it. Your component must read as its counterpart does: same ramp, same
  spacing, same type scale, same density. Where this prompt and the mockup differ on an
  appearance, the mockup governs.
- **`tokens.css` is the mockup's `:root` block.** Copy it: the same custom-property names and
  the same values. You are not choosing a palette, a spacing scale or a type scale — one was
  approved and it is in that file. Below its `:root` the mockup itself contains no raw value,
  which is the rule O23 places on component source, so it demonstrates the convention it
  establishes.
- **The eight slot paths are exact.** T15–T24 each `UPDATE` one of them. A different directory
  breaks eight tasks.
- A skeleton at **final dimensions** means the placeholder occupies the space the finished
  component will, so the layout does not jump as later tasks fill it in. Take the dimensions
  from the mockup.
- The `Simulated feed` string is required on every view. Placing it in the shell outside the
  outlet is what makes that structural rather than a thing each route remembers.

# Deliverables

- **CREATE** `frontend/src/styles/tokens.css` — the mockup's `:root` block
- **UPDATE** `frontend/src/styles.css` — imports `styles/tokens.css`
- **CREATE** `frontend/src/app/core/format.ts`
- **Function(s):** `formatPrice(value: number, dp: number) -> string`,
  `formatQuantity(value: number) -> string`, `formatSignedPercent(value: number) -> string`
- **CREATE** `frontend/src/app/shell/shell.component.ts`
- **CREATE** `frontend/src/app/dashboard/dashboard.component.ts` — the eight slots in final order, portfolio summary first; routed at `/`
- **CREATE** `frontend/src/app/features/markets/markets.component.ts` — skeleton; routed at `/markets`
- **UPDATE** `frontend/src/main.ts`

# Instructions

1. CREATE `frontend/src/styles/tokens.css`
2. UPDATE `frontend/src/styles.css`
3. CREATE `frontend/src/app/core/format.ts`
4. ADD function `formatPrice(value: number, dp: number) -> string`, `formatQuantity(value: number) -> string`, `formatSignedPercent(value: number) -> string` in `frontend/src/app/core/format.ts`
5. CREATE `frontend/src/app/shell/shell.component.ts`
6. FOR EACH path in `features/portfolio/portfolio-summary.component.ts`, `features/macro/macro-strip.component.ts`, `features/watchlist/watchlist.component.ts`, `features/movers/movers.component.ts`, `features/scenario/scenario-selector.component.ts`, `features/ticker/headline-ticker.component.ts`, `features/detail/detail.component.ts`, `features/impact/impact-panel.component.ts`, `features/markets/markets.component.ts`, `dashboard/dashboard.component.ts` — CREATE it under `frontend/src/app/`
7. UPDATE `frontend/src/main.ts`

# Constraints

- Every value in a component is a `var(--token)` reference. The only file containing a raw
  hex, px or ms value is `tokens.css`.
- `formatSignedPercent` emits U+2212 MINUS SIGN for negatives, not a hyphen. Percentages are
  always signed, including positives.
- Numerals render in a `font-variant-numeric: tabular-nums` face wherever a figure appears, so
  digits occupy constant width.
- Components are standalone with **inline** templates and styles. The grep that evidences O23
  covers `*.ts` only, which is sound precisely because there are no separate `.html` or `.css`
  component files — do not introduce one.
- Do not implement a feature. Every slot is a placeholder rendering its loading state; the
  nine tasks that follow fill them.
- If the mockup's `:root` block does not carry a value some component needs, STOP and report
  which. Do not invent a token.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence, and the deferred item reported as deferred rather than asserted. Then the build
output, the grep result, `tokens.css` in full with the contrast ratio, the `dependencies`
block, the shell template and the dashboard template.
