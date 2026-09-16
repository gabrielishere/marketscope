---
name: reading-the-input
description: The three passes between whatever arrived and a spec you can decompose — what to keep, what to read, and which decisions to settle before writing anything.
dependencies:
  - ../templates/spec-template.md
---

# Reading the input

Between *whatever arrived* and *a spec* there are three passes. They are the human's,
always: no agent runs them, and the artifacts below are written and read by people.

**These rules were derived from one run and have been validated once.** Each states a
general form with that run cited as evidence. A rule that only ever pays on work shaped
like its evidence should be cut the next time it fails to earn its place.

**Assume nothing about the form of the input.** A ticket, a brief, a paragraph in a thread,
notes from a call, one sentence said out loud. It will not be organised, it will not be
complete, and it will not distinguish what is decided from what is assumed. That is not a
defect in the input — **the useful information is as much in what it does not say as in
what it does.** A step that treats it as a form with missing fields produces a document
full of confident blanks.

---

## Pass 1 — Sort

Whatever arrived is several documents in one jacket, and only part of it is requirement.

**The destinations are the filter.** There are five, below. Sort every line into one of
them; **anything with no section to land in is dropped.** If you find yourself wanting a
sixth to fit something, that is the signal the something is process, rubric or metadata
rather than requirement.

```
What this is            one paragraph — what it does, and what exists because of it
Who it serves           the user by role · the decision it serves · and what would
                        make the answer wrong for that purpose
What is authoritative   where each input comes from, which source wins when two
                        disagree, and the conventions a value carries that its type
                        does not — units, timezone, currency, precision
Constraints             quoted, each with where it came from
Open questions          each with a person's name against it
```

**Where the requester is reachable you write none of this down** — you ask, and the answers
go into the spec's Constraints and into decision records. The five are a sorting frame
first and a document only when nobody is available to answer.

What typically has no home: instructions about how to work, acceptance criteria that
describe how the work will be judged, effort estimates, ticket fields, and whoever's
proposed solution.

> *Evidence (n=1).* In the run this came from, the input was an exercise brief. Only one
> quoted paragraph of it was requirement; roughly half the document was reflection prompts
> and an assessment rubric. The first intake had no destination test, absorbed the rubric,
> and filed the questions it was being assessed on as open questions needing an owner —
> converting the thing under assessment into a blocked ticket.

**Quote, do not paraphrase.** Where the input states a name, a number, a unit or a bound,
reproduce it exactly. A paraphrase of a quantity is a new quantity.

---

## Pass 2 — Read the system

The input says what someone wants. The existing system says what is true. Doing this after
writing the requirements produces a document whose unknowns were answerable from the code
all along.

**Scope it to the change surface** — what you are changing and what touches it, not the
repository. Four things to look for:

- **Dead things.** Config nothing reads, flags nothing sets, code nothing calls. Using them
  or not is a decision, so dead config is a decision waiting to be found.
- **What happens today at the boundary you are about to change.** Especially with input the
  system does not understand. Changing that is usually the only breaking change in an
  otherwise additive feature.
- **Extension points already present.** A field, a hook, a parameter someone left room for.
  These shape the design more than anything in the input does.
- **Verify empirically rather than by reading.** Run it, call it, open it, measure it. What
  this means depends on the work: the shape and coverage of the data a change reads, the
  real response of an API you are integrating, which of the existing tests actually pass,
  what the screen does in its empty state.

> *Evidence (n=1).* All four paid. A `quote_dp` field declared and read by nothing became
> the rounding decision. Unknown query parameters being silently ignored became the single
> most consequential decision in the build, reversing an earlier one that would have broken
> a live consumer. A response field already present shaped the whole interface. And
> measuring the supplied data produced the five literals that became the test suite's spine.
>
> A narrower pass — read only enough to fill *What is authoritative* — would have caught
> two of those and missed the other two, including the breaking change.

---

## Pass 3 — Enumerate the decisions

List every decision the work requires **before** writing the spec. Three sources:

1. the open questions the input left,
2. the degrees of freedom pass 2 turned up,
3. how the work will be done — the runner, the verification discipline, the commit
   boundary. The input will never raise these because they are not about the system.

Filter each: *would someone six months from now ask "why is it like this?"*, and *does the
choice outlive the task?* If yes, it cannot be delegated to whoever implements it, so it is
settled before any prompt names it. Then sort, leaving nothing as "we'll see":

- **decide now**
- **ask** — name a person, not a role
- **defer with a stated assumption**, recorded as one

**Any decision that introduces a per-item procedure: measure one item before committing to
it.**

> *Evidence (n=1).* Six substantive decisions were settled during that build, in waves, one
> of them superseding another. Checked afterwards, **all six were derivable from the input
> plus pass 2** before any code was written. The cost of not listing them was seven decision
> records, one supersede, three prompt revisions and two incident records.

---

## Then: the fork

- **The requester is reachable.** Ask the open questions. The answers go into the spec's
  Constraints and into decision records. **No requirements document is written.**
- **The requester is not reachable.** Write `requirements.md` to hold what you could not
  ask, then the spec.

The document exists to carry what you could not settle. If you settled everything, it has
no job.

---

## What this step must refuse

- **Resolving an ambiguity.** Where the input admits two readings, record both and raise the
  question. Choosing one and writing it down as the requirement hides a decision inside a
  document that reads as a transcription.
- **Raising a question with a default already attached.** *"I'm taking reading A — say the
  word if you want B"* is not a question, it is a notification, and the default answers it the
  moment nobody objects. **Ask without stating a preference.** If you have one it goes into the
  decision record *after* the answer, where it is visibly yours rather than apparently theirs.
  The failure is silent: nobody was put in a position where a reply was required, so the
  absence of one reads as agreement.
- **Supplying the conventional answer.** The most dangerous slots are the ones with an
  obvious default — the timezone is probably UTC, the quarter is probably a calendar
  quarter. A plausible default is indistinguishable from a stated fact once written in the
  same typeface, and it is *more* dangerous than a gap because nobody will ever ask about it.
- **Producing a spec.** Outcomes, tasks and deliverables are the next document down.

## Recognising a bad result

Two tests, in the order they catch things:

1. **Read the authoritative table against the source.** This is the slot most often
   invented, because every system has *some* source of truth and naming the obvious one
   feels like observation.
2. **Ask which sentence of the input, or which file and line, produced each answer.** An
   answer that can be traced to neither came from you.

> *Evidence (n=1).* Test 2 is the one that failed. A claim about what was computable from
> the supplied data was traceable to neither the input nor the code, and reached a decision
> record and a spec before a human challenge caught it.
