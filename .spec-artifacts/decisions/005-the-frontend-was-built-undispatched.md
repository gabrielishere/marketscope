# ADR-005 — The frontend was built by the main agent, not dispatched through the gate

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-frontend`
**Scope:** records how the work was done. **It places no constraint on any task** — an
orchestrator surfacing this at a gate should note it and dispatch normally.

## Context

The backend ran through the whole method: a prompt per task, a cold orchestrator, a gate, an
implementor, a run record, a commit. It worked, and it caught four real authoring defects
that would otherwise have reached the emitted contract — recorded in
`incidents/2026-09-16-evidence-that-could-not-fail.md`. It was also slow: every refusal
stopped the run and required the author to re-open the artefacts, and the operator said so
directly.

Two facts about the frontend differ from the backend, and they are the reason this decision
is confined to it:

- **Nothing generates from it.** The contract was frozen by T11 and the client generated from
  it. A frontend mistake propagates nowhere — there is no downstream consumer to poison.
- **It holds no durable state.** What client state exists — the shared poll's replay buffer,
  the previous prices the watchlist flashes against — dies with a refresh. No bad value
  outlives the tab.

And one fact about what the gate could actually check there: the spec itself states that no
frontend test framework is installed, that the implementor has no browser, and that **every**
frontend task's behavioural claim is deferred to human review and recorded `UNVERIFIED`.

## Decision

We will have the main agent write the frontend directly, using the twelve frontend prompts
as a checklist rather than dispatching them. The specs, the prompts and the approved mockup
remain the definition of the work; what is given up is the dispatch, the gate and the run
record for those twelve tasks.

This is scoped to `trading-demo-frontend`. It is **not** a general position that agents
should build undispatched, and the backend half of this same build is the argument against
generalising it.

## Alternatives

- **Dispatch the frontend as written** — twelve prompts and twelve gated dispatches, whose
  product would be twelve run records reading `UNVERIFIED`, because the gate cannot check
  what the frontend's outcomes assert. The ceremony without the check.
- **The same decision for the backend too, taken when it started costing round trips** —
  would have forfeited the four defects in the incident record, at least two of which would
  have been frozen into `openapi.json` and generated into the client.
- **"The main agent's context is rich enough to thread it correctly"** — considered and
  **rejected as a justification**, though the decision it was offered for stands on the two
  grounds above. `orchestrator.md` takes the opposite position explicitly: *"You are
  dispatched cold, and that is the point. The session that authored the spec has been
  running for hours: it holds decisions taken aloud, questions half-settled, and context
  nobody wrote down."* Rich context is the hazard the cold gate exists to catch, not a
  qualification for going without it — a long context fills gaps from memory without
  noticing that it is doing so. This run is the evidence: the author had written both specs,
  all twenty-four prompts, the entire backend and the approved mockup, and still put two
  defects into committed frontend code. Crediting a control with more than it can do is
  worse than having none, because it will be trusted next time.

## Consequences

- **Faster, materially.** The whole frontend — workspace, generated client, design system,
  shell and ten components — landed in one pass.
- **Two defects reached committed code**, and would not have survived a cold gate: four
  independent polling timers where O14's entire content is one shared cadence, and an O23
  that banned every `px` while the approved mockup carries 53, making the rule unsatisfiable
  by its own design target. Both were found by the author checking outcomes afterwards —
  the same arrangement that produced them.
- **The log has a hole.** Run records exist for `trading-demo-backend` and for nothing else.
  Anyone asking later what happened on T17 has the diff and no run.
- **The blast radius was genuinely small, which is the decision's own premise.** Both
  defects were visible on inspection, neither could reach a stored value, and both were
  repaired the same session. Had the same arrangement been used for the backend, the
  equivalent defects were an unauthored API contract and an assertion that could not fail.
- **Reversible.** The specs and the twelve prompts are on disk, unchanged and unused. A
  re-run can be dispatched normally.

`process/001-the-main-agent-built-the-frontend.md` was written first and filed as a process
record, on the reading that this is a decision about how work gets done rather than about
the system. The operator has since determined that it is a decision taken mid-development
and belongs here. That record is immutable and stands; it carries the fuller cost
accounting, and this one carries the position.
