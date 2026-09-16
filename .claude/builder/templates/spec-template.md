---
name: spec-template
description: The system specification an orchestrator works from — objective, outcomes, constraints, and the tasks that satisfy them.
dependencies:
  - instruction-grammar.md
  - prompt-template.md
---

# Specification template

What the system must be, and the tasks that get it there. This is the document an
orchestrator holds while it dispatches work — every thread gets a slice of it.

**It is stateless.** Nothing here records what happened: no ticks, no status, no
notes from a run. It reads identically before the first task and after the last.
Run state lives in the log, joined by task id.

**Change of intent is a commit.** The spec at HEAD is current intent; what was
originally asked for is in the history. That only works if the spec never absorbs
what *happened* — the gap between what you asked for and what you got is the only
signal that something went wrong, and editing the spec to match the result erases
it.

**Ids are the join.** `O1…On` for outcomes, `T1…Tn` for tasks. The log references
them, prompts are assembled from them, and an ADR that changes one names it. Ids
are never reused or renumbered.

---

````markdown
---
spec: <kebab-case-id>
---

# Objective
<What the system is for, in one or two sentences. The reason the work exists.>

# Outcomes
<What is observably true when this is built — the behaviour, not the parts.
Each gets an id so tasks can point at it. Write them so a wrong result could be
caught out: "counts exclude common words" is an outcome, "the counting works" is
not.>

- **O1** <…>
- **O2** <…>

# Constraints
<Bounds on how the system is built: stack, dependency limits, what is off-limits,
interfaces that must not change. Not coding standards — those are standing
context. Not reasons — those are ADRs.

Name what the run must be permitted to do — the commands its tasks give as evidence.
A permission granted for earlier work is not a permission this spec has.>

- <…>

# Shared
<Anything more than one task depends on that does not exist yet. Name it, and the
task that creates it. Every other task reads it.>

- `<name>` — created by **T3**

# Tasks
<Ordered for reading, not for execution — the orchestrator derives what can run
in parallel from Reads and Deliverables below.>

## T1 — <short title>
**Objective:** <one or two imperative sentences: what to do, and what for.>
**Outcome:** <what is true once this lands.> → serves **O1**
**Reads:** <what it needs that already exists — files, symbols, interfaces. **Not
decision records:** an ADR declares which tasks it bears on in its own `Affects:` line,
and the orchestrator finds them by grepping for the spec id before it dispatches. Listing
them here is a second copy of that fact, maintained by hand, and the two drift.>
**Deliverables:**
- CREATE `path/to/file.ext`
- ADD function `name(args) -> ReturnType` in `path/to/file.ext`

**Evidenced by:** <a command to run, or an observation to make and report. If
nothing can evidence it, say so — the result is then a claim, not a proof.>
**After:** <task ids — only when the ordering can't be derived from Reads and
Deliverables. Omit otherwise.>

## T2 — <short title>
**Objective:** <…>
**Outcome:** <…> → serves **O2**
**Reads:** <…>
**Deliverables:**
- UPDATE `path/to/file.ext`
- ADD function `name(args) -> ReturnType` in `path/to/file.ext`

**Evidenced by:** <…>
````

---

## How the parts work

**A task's Deliverables must be able to discharge the Outcome it claims.** An outcome saying
several messages appear at once cannot be satisfied by a function returning one; an outcome about
an address cannot be satisfied by a file nothing mounts. Pointing at an outcome is not the same as
being able to make it true, and the gap between them is invisible until something runs.

**A task that will not run is marked, not deleted.** Work already live, or intent
that changed, cuts a task — write `**Cut:** ADR-0NN` in its block and leave the id
alone. Deleting it renumbers nothing and loses the record; leaving it unmarked
makes it indistinguishable from a task that was forgotten, since a cut task has no
prompt and no run record either. `CUT` is the run status the log then shows for it.

**Anything two tasks depend on is named under Shared, with its owner.** A task that
needs something nobody owns will build it shaped for itself, and the next task that
needs it cannot use it. Naming the owner costs a line; renegotiating it afterwards
costs a decision record.

**Objective → Outcomes → Tasks is one chain, and it repeats at task level.** The
system's objective is why it exists; the outcomes are what will be observably
true; each task takes a slice of one or more outcomes and produces the artefacts
that make it true. Every task points at the outcome it serves — an orphan task
serves nothing and should be cut.

**Deliverables are encoded, not described.** Operation, target type, name,
location — drawn from [`instruction-grammar.md`](instruction-grammar.md):

```
CREATE `src/word_counter.py`
ADD function `word_counter(script: str, threshold: int = 10) -> WordCounts` in `src/word_counter.py`
```

That form is checkable without a model in the loop. The orchestrator stats the
path and greps the symbol, so *"were the deliverables made"* is answered by
inspection rather than by asking the agent. Prose deliverables give it nothing to
check.

**Keep them minimal — only what the outcome requires.** A deliverable list is not
a prediction of the final file tree. Whatever else the agent needs to create is
its business, and if it produces something unexpected and good, that surfaces in
the run, and becomes intent by being committed to the spec.

**Reads and Deliverables are the read and write sets**, and the execution order
falls out of them: a task that reads what another writes comes after it, and two
tasks writing the same file are serialised even when they are otherwise
independent. `After:` exists only for orderings with no shared artefact — *"run
the migration before the backfill"* — which nothing can compute.

**What this template does not hold:**

| | Where it goes |
|---|---|
| Coding standards, house conventions | Standing context — the harness supplies them |
| Why a constraint was chosen | An ADR |
| What happened when a task ran | The log |
| A list of files that exist now | Nowhere — the orchestrator can look |
| The prompts themselves | Assembled per task from `prompt-template.md` |

The last one matters most. A spec that contains its prompts cannot be frozen:
change the implementation and the spec is silently wrong. Tasks declare intent;
prompts carry execution detail — instructions, constraints, response format and
model.

**Satisfied when every Outcome holds.** There is no separate acceptance section,
because it would restate the outcomes; that is what they are for.
