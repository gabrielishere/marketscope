# ADR-007 — The frontend is verified by driving the running application, not by reading its source

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-frontend`
**Scope:** records how the work is checked. **It places no constraint on any task** — an
orchestrator surfacing this at a gate should note it and dispatch normally.

## Context

The frontend had no check between "it compiles" and "somebody notices in a demo".

Three decisions, each sound on its own, combined to leave that hole:

- Both specs forbid a frontend test framework, and the implementor has no browser. Every
  frontend task's behavioural claim is therefore **deferred to human review** and recorded
  `UNVERIFIED`. That is the spec working as designed.
- ADR-005 built the frontend without dispatching it, so the cold gate — which caught four
  authoring defects on the backend — never ran against it.
- The human review those first two lean on had not happened, because the application had
  only just been built.

The result was not hypothetical. Four defects reached committed frontend code:

| Defect | Found by |
|---|---|
| Four independent polling timers, where O14's whole content is one shared cadence | the author re-reading the outcomes after committing |
| O23 banning every `px`, unsatisfiable by the mockup it governs | the author running the grep after writing ten components |
| The markets table's volume column reading `0` for all forty-five rows | driving the page and reading a screenshot |
| The scenario dropdown not reflecting an already-active scenario on load | the same screenshot, then a DOM probe to characterise it |

Reading the source had not found any of them. Two were invisible in a diff by nature — a
column of zeroes and a stale `<select>` look exactly like working code.

## Decision

We will verify the frontend by **driving the running application headlessly** — capturing
screenshots and probing the rendered DOM — and reading what comes back against the outcomes
the specification asserts. The screenshots are committed, so the state that was reviewed is
part of the record rather than a thing someone once saw.

Both halves are required and they do different jobs:

- **The DOM probe** answers what is machine-checkable: how many rows rendered, what distinct
  values a column holds, what a `<select>` reports as its value against what the API says is
  active.
- **The screenshot** answers what is not: whether the collapsed impact panel reads as plain
  language, whether a column boundary moves, whether the thing reads as a professional
  trading product rather than a demo of one.

## Alternatives

- **Human review alone**, which is what the spec originally specified. It is not wrong, and
  it remains the final check — but it is a check that happens once, late, in front of an
  audience, and it had found none of the four defects above at the point they were committed.
- **Add a frontend test framework** — forbidden by both specs, and the ban is deliberate
  rather than incidental. A unit test asserts a component's internals; the outcomes here are
  about what renders, and a component can satisfy every internal assertion while rendering a
  column of zeroes.
- **DOM assertions only, without screenshots** — stronger where a claim is checkable, and it
  is the half that did the real work on BUG-001. Rejected as a *replacement* because the
  outcomes that matter most on this surface are appearance claims. No assertion expresses
  "no exposure value appears outside the expanded detail" as well as looking at the panel.
- **Screenshots only, without probing** — rejected on evidence from this run. Reading images
  alone produced **two wrong conclusions**: that the markets table rendered only four sector
  groups, when the pane was simply scrolled and all eight were there; and that the scenario
  dropdown was broken, when only its load path desyncs and clicking works. Both were
  corrected by probing. An image tells you something looks wrong; it does not tell you what
  is wrong, and acting on the image alone sends you rewriting the wrong thing.

## Consequences

- **It finds defects nothing else on this surface would.** BUG-001 was a column presenting a
  number that was always wrong, in code that compiled, passed every declared check, and read
  correctly in review.
- **The screenshots double as documentation.** Three are in the README, so the artefact that
  verifies the work is the same one that shows it.
- **It is weaker than it looks, and this is the important consequence.** It finds *visible*
  defects. A wrong number that looks plausible survives it completely — a day change computed
  from the wrong baseline would render beautifully. This is a check against the absurd, not
  against the incorrect, and it must not be credited with more than that.
- **It has a setup step that can itself be wrong.** The screenshots are only useful against
  an interesting state, so a scenario has to be activated first. One capture in this run
  showed a shock that had already decayed to nothing, which is a picture of the application
  working and of the demo failing.
- **A green build is not evidence the running page contains the change.** `ng serve` silently
  stopped rebuilding during this run and served stale code for a cycle, which made a
  correct fix look like a failed one. The loop must drive a server known to be current.
- **Binary files enter the repository.** Five PNGs, about 1 MB. They will go stale as the
  application changes, and a stale screenshot in a README is worse than none.
