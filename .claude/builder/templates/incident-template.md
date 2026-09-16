---
name: incident-template
description: One event that cost something — what happened, what caused it, what it cost, and which check would have caught it.
dependencies:
  - adr-template.md
  - log-schema.md
---

# Incident template

An incident record is written **after** something went wrong across more than one task, and its
job is to make the cause reusable. It is not an apology and it is not a status update.

**The operator declares an incident. Nothing else does.** No agent decides one has occurred,
and no step of the loop produces one — this template is not wired into the run. The
orchestrator records a failed or refused task as a run record and stops; whether that, or
anything else, amounts to an incident is a person's call, made explicitly. The table below is
how the operator tells the three artifacts apart once they have made it.

**Immutable once written**, for the same reason an ADR is: the account written while the run is
fresh is the thing worth keeping, and an account edited later to look tidier is worth nothing.

**Three artifacts, three jobs.** The common failure is writing one of these in another's place.

| Ask | If yes | It goes |
|---|---|---|
| Is it one task that failed? | it is an event with a run and a status | a run record — `log-schema.md` |
| Is it a choice between real alternatives? | it is a position someone took | a decision record — `adr-template.md` |
| Did something go wrong **across** tasks, specs or roles, and cost something? | this | `.spec-artifacts/incidents/<YYYY-MM-DD>-<slug>.md` |

A single refused dispatch is a run record. Three refused dispatches with one cause behind them is
an incident, and the cause is the whole reason to write it.

**Write one when the cause outlives the event.** If nothing about the next spec would change for
knowing this, there is nothing here to record.

---

````markdown
# Incident — <what happened, in a clause>

**Date:** <YYYY-MM-DD>
**Raised by:** <who noticed, and how — a person, a gate, a failing check>
**Spec:** <spec ids in play>
**Outcome:** <what state the work ended in>

## What happened

<The events, shortest first. Where there is more than one defect, a table — and the last
column is the one that matters.>

| # | Defect | Where | Caught by |
|---|---|---|---|
| 1 | <what was wrong, stated as a fact about an artifact> | <spec, task, file> | <the gate question, the agent, the person — and whether before or after anything acted on it> |

<Anything that belongs to another artifact is named and sent there, not absorbed: "a fourth
defect is the subject of ADR-0NN rather than of this record".>

## Cause

<The mechanism, not the mood. "I was careless" is not a cause and cannot be checked against
next time; a quoted command, a specific omission, a claim nobody verified, can be.>

<Where several defects share one shape, say the shape once and then give the exact instance —
the shape is what transfers, the instance is what makes it believable.>

## What it cost

<Both halves. What was spent, and what was *not* damaged — a record listing only the damage
reads as a catastrophe, and one listing only the containment reads as a defence.>

- <…>
- <what did not happen, and what stopped it>

## What was done

<The repair, and any deliberate departure from what was planned or instructed, with its
reason. A departure recorded here is a decision someone can disagree with; the same departure
unrecorded is a discrepancy someone will find.>

## What would have caught these earlier

<Checks, not intentions. "Be more careful" is not a control. A control is something a person
or a command could perform, named so specifically that its absence is visible.>

- <…>

## What is still open

<What this record does not close, so nobody reads it as the end of the matter.>
````

---

## How the parts work

**`Caught by` is the column the record exists for.** A defect caught by a gate before anything
acted on it says the safety net works and cost a cycle. The same defect caught after an agent
built on it says the net has a hole, and the hole is the finding. Two defects that look identical
in every other column are different incidents if this column differs, so never collapse them.

**The cause must name something checkable.** The test: could someone write a command, a gate
question or a checklist line from this sentence? *"An enumeration was asserted complete and never
verified"* passes — it becomes a question to ask of the next prompt. *"I rushed"* fails.

**Name the role, not to blame but because it changes the repair.** A defect made by the author is
repaired by changing what authoring asks; the same defect made by the implementor means the
prompt let it happen. The two lead to different fixes, and a record that says only "a mistake was
made" points at neither.

**`What it cost` is where honesty is cheapest and most often skipped.** Include the cycles spent,
the artifacts written to repair something rather than to build it, and the work discarded. Then
include what was contained: a defect that never reached a consumer was stopped by something, and
that something is worth knowing as much as the failure is.

**Controls, not resolutions.** The last two sections are what a reader takes away. A control names
the check; a resolution names a feeling about the check. If the control is *"a checker would have
caught this"*, say which defects it would mechanically catch and which it would not — a control
credited with more than it can do is worse than none, because it will be trusted.

> *Evidence (n=1).* Derived from one incident, on a run where two consecutive orchestrator
> dispatches were refused at the gate and a third defect surfaced only after an
> implementor had built on it. Three sections earned their place there and are the reason this
> template is not simply a run record with prose: the `Caught by` column, which separated the two
> classes of defect and showed that the one caught late had produced contract decided by the wrong
> role; `Cause`, where the useful sentence was a quoted shell command — an exhaustive search capped
> with `head -20`, whose truncated output was then written into two documents as a completeness
> claim; and `What it cost`, where "no incorrect code was committed and no wrong number reached a
> user" was as load-bearing as the cycles lost. The headings that did *not* earn their place, and
> are deliberately absent: severity, owner, and timeline.
