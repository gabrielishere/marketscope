# ADR-004 — Hand-rolled CSS, and no UI or styling package

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-frontend`

## Context

Both specs carry the constraint *"Styling is hand-rolled CSS, dark theme. No UI or styling
package"*, and neither says why. It arrived from the original brief and was never argued,
which is exactly the case `adr-template.md` says needs a record: a constraint in a spec with
no obvious justification.

The frontend has to read as a professional trading product to a non-technical audience. A
trading surface has requirements most component libraries are not built around:

- **Tabular numerals everywhere**, so digits occupy constant width.
- **Fixed-width, decimal-aligned numeric columns**, so a price crossing `9.99 → 10.01` moves
  no boundary.
- **No layout shift on poll.** Forty-five rows reprice every 2.5 seconds; anything that
  resizes with its content jitters continuously.
- **Dense rows** at a fixed height, closer than a general-purpose library's defaults.
- **Colour reserved for direction.** Green and red mean up and down and nothing else; every
  other surface comes from a neutral ramp.

There is also a structural reason particular to this build. The design was approved as a
static mockup *before* any code was written, and `tokens.css` is that file's `:root` block
copied verbatim. O23 then asserts that no component source contains a hex colour, a
millisecond duration, or a `px` used as a type size or spacing value — a rule checkable by
one grep, and only because there is exactly one source of visual values.

## Decision

We will write every component's styles by hand, against the token file, and take no UI
framework, CSS framework, icon set or charting library. Runtime dependencies are Angular,
RxJS, `tslib` and `zone.js`, and nothing else.

## Alternatives

- **Angular Material** — brings Material Design's visual language, which reads as a Google
  product rather than a trading terminal, and its own type scale, spacing and elevation
  model. Meeting the requirements above means overriding most of that: the result is
  hand-rolled CSS anyway, layered on a bundle, with two sources of visual values fighting.
- **Tailwind** — utility classes are raw values wearing a different hat. Every spacing and
  size decision moves into the template, `tokens.css` stops being the single source, and
  O23's grep has nothing left to check. The rule and the tool are incompatible by design.
- **A charting library** — the chart is a polyline, three gridlines and a dashed vertical
  rule at the activation tick. A charting dependency for that brings its own palette and
  fonts to override, to draw something that is forty lines of SVG.
- **A headless library such as Angular CDK** — closer in spirit, and would have given the
  sticky-header and overlay behaviour. Rejected because the components actually needed are
  native elements: a `<table>`, a `<select>`, and a `<details>` for the attribution
  disclosure.

## Consequences

- **446 lines of component CSS across 15 components**, plus a 66-line token file. More code
  than importing a library, and all of it ours to maintain.
- **No dependency surface.** `package.json` lists nine runtime packages, all first-party
  Angular or its direct runtime. Nothing to audit, pin or upgrade for styling; the built
  bundle is 308 kB of JS.
- **O23 is enforceable.** One token file means one grep, and the rule is checked rather than
  asserted.
- **Accessibility and browser behaviour are ours to get right**, with nothing doing it for
  us. The contrast ratios, the `prefers-reduced-motion` suppression on the price flash, and
  the sticky header over a scrolling pane were each written and checked by hand.
- **This is scoped to a demo.** A product growing past ten components — needing dialogs,
  menus, date pickers, focus management — would likely want a headless component library.
  That is a different decision on different evidence, and this record does not settle it.
