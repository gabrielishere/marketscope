# PR-001 — The main agent built the frontend directly, rather than dispatching it

**Date:** 2026-09-16
**Status:** accepted
**Kind:** process — how the work gets done, not what the system is

*Filed here and not in `.spec-artifacts/decisions/` deliberately. `adr-template.md`'s first
qualifying question separates decisions about the system from decisions about the runner and
the verification discipline, and sends the second kind anywhere but `decisions/` — because a
process decision filed among domain ones stops being scrutinised as process, and nobody
auditing a directory of system decisions thinks to ask what one of them costs per task.
There is also a mechanical reason: the orchestrator greps `decisions/` for the spec id
before every dispatch and reads what it finds as constraints on the work. This is not one.*

## Context

The backend ran through the full method — spec, prompt per task, cold orchestrator, gate,
implementor, run record, commit. It worked. Twelve tasks, 308 tests, and **four gate
refusals, every one of them a real authoring defect** that would otherwise have reached the
contract:

- T1's prompt named fourteen models and specified no field for any of them, so the API
  contract was being authored by an implementor filling a gap.
- T4's evidence never read `contributions` or `residual`, so a `Bar` carrying no attribution
  at all would have passed.
- T4 again: a Definitions entry the prompt did not reproduce, leaving a constraint telling
  the implementor to stop on a question that had just been answered.
- T5's lifespan assertion could not fail — `_DefaultLifespan` is truthy, so the check passed
  on an application that never had a lifespan attached.

Each refusal cost a round trip: the orchestrator stopped, reported, and waited while the
defect was fixed and the prompts re-authored. The run was correct and slow, and the operator
said so directly.

Two things then changed the calculus. The backend was six tasks from done, and its
remaining outcomes were the machine-checkable kind — reconciliation to 1e-6, route ordering,
an operation count. The frontend's were not: the spec itself states that no frontend test
framework is installed and none is to be added, that the implementor has no browser, and
that every frontend task's behavioural claim is **deferred to human review** and recorded
`UNVERIFIED`.

## Decision

We will have the main agent write the remaining backend tasks and the whole frontend
directly, using the twelve frontend prompts as a checklist rather than dispatching them.
The specs, the prompts and the approved mockup stand as the definition of the work; what is
dropped is the dispatch, the gate and the run record for those tasks.

## Alternatives

- **Run the frontend through the orchestrator as written** — twelve prompts and twelve
  gated dispatches, whose product would be twelve run records reading `UNVERIFIED`, because
  the gate cannot check what the frontend's outcomes assert. The ceremony without the check.
- **Abandon the method for the backend too, at the point it started costing round trips** —
  would have forfeited the four defects above, at least two of which (the unauthored
  contract, the unfalsifiable assertion) would have been frozen into `openapi.json` and
  generated into the client.
- **Hybrid: dispatch T12 and T13, write the rest directly** — T13 is the one frontend task
  with a real conformance gate, so this has some logic. Rejected as a half-measure that
  keeps the dispatch overhead for the two largest tasks while giving up the discipline
  everywhere it is cheap.

## Consequences

- **Faster, materially.** The entire frontend — workspace, generated client, design system,
  shell and ten components — landed in one pass, against six backend tasks that took several
  rounds.
- **The independent check is gone, and its absence is measurable.** Two real defects reached
  the committed frontend and were found only because the outcomes were checked by hand
  afterwards: four independent polling timers where O14's whole point is one shared cadence,
  and an O23 that banned every `px` when the approved mockup itself carries 53 of them,
  making the rule unsatisfiable by its own design target. A cold gate would have caught the
  second before a line was written.
- **The log has a hole.** Run records exist for T1–T11 and T25 of `trading-demo-backend` and
  for nothing else. The frontend's history is commits and this record. Anyone asking later
  what happened on T17 has the diff and no run.
- **The prompts were still worth writing.** They carried the mockup as the governing visual
  target, the no-browser split, and the reasons behind each visual rule — and they were the
  checklist the work was done against. Their cost was not wasted by not dispatching them.
- **Reversible.** The specs and prompts are on disk and unchanged. A later spec, or a
  re-run of this one, can be dispatched normally.
