# ADR-006 — Specs and prompts are repaired by hand, mid-run, at the operator's direction

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-backend`, `trading-demo-frontend`
**Scope:** records how the work was done. **It places no constraint on any task** — an
orchestrator surfacing this at a gate should note it and dispatch normally.

## Context

The orchestrator stops on a defect and reports it; by its own definition it never fixes one.
That leaves an open question the method does not answer: when a gate refuses, **what
happens next, and who does it.**

It came up four times on `trading-demo-backend` — run records `003-T4`, `005-T4`, `011-T6`,
`012-T5` — and each time the orchestrator handed back a defect in a prompt or a spec and
paused, holding the spec, the derived task order and its results, waiting.

The artefacts were not in a state where any single repair was obviously right. Some defects
were in one prompt (`005-T4`: a Definitions entry the prompt never received). Some were in a
prompt *and* its spec block, identically (`003-T4`: evidence that read neither
`contributions` nor `residual`). One was in neither — the factor key strings existed only in
committed code and in no document at all.

The operator directed that the artefacts be edited in place and the paused orchestrator
resumed, rather than any of the alternatives below.

## Decision

We will repair specs and prompts **by hand, in place, while the run is paused**, and resume
the same orchestrator, which re-reads the affected artefacts from disk and re-gates from the
top. Each repair is a commit against the spec at HEAD, and the reason for the repair goes in
the commit message.

## Alternatives

- **Re-author the affected artefacts from the original input** — the specs were derived from
  `input/app-features.md` through the method's three reading passes. Re-running those for a
  single-clause defect discards the intervening decisions, several of which are the ADRs in
  this directory, and risks re-introducing what was already fixed.
- **Restart the run from T1 after each repair** — clean, and it throws away every passing
  task to fix one prompt. T1 and T4 were re-run because their *deliverables* were genuinely
  invalidated; re-running T2 because T6's prompt was wrong would be waste with no
  corresponding safety.
- **Accept the defect and carry on** — available in every case, since all four were caught
  before anything was built on them. Rejected because every one of them was an assertion that
  could not fail, and the log would then have recorded outcomes as evidenced that were not.
- **Have the orchestrator repair what it finds** — forbidden by its own definition, and for
  the right reason: the role that reports a defect and the role that fixes it must differ, or
  the report stops being independent.

## Consequences

- **The spec at HEAD is current intent, and its history carries the change.** This is what
  `spec-template.md` asks for — *"Change of intent is a commit"* — so a hand repair is the
  compliant path rather than a deviation from it.
- **The spec and the early run records are deliberately out of step.** `001-T1.json` records
  a task that passed against a prompt which has since been rewritten. That gap is the signal
  the method exists to preserve: it is how anyone can see that T1's first pass was against an
  unauthored contract. Editing the record to match would erase it.
- **Repairs are as good as the author, with nothing checking them.** Twice the repair was
  itself defective: T5's lifespan assertion was rewritten to something vacuous and refused
  again at `012-T5`, and its second version — identity against the `lifespan` function —
  was also wrong, because `include_router` merges lifespan contexts. The gate caught the
  first; a test caught the second.
- **It preserves the run.** The orchestrator holds the spec, the derived order and its
  results across a pause, so a repair costs one re-gate rather than a cold restart.
- **Nothing records a repair as an event.** A hand edit between two dispatches appears as a
  commit and in no run record, so the log shows a refusal followed by a pass with no account
  of what changed. The commit message is the only account, and the incident records were
  written afterwards to cover it.
