---
name: log-schema
description: The record of what happened when a spec's tasks were run — one JSON file per run, and nothing else.
dependencies:
  - spec-template.md
  - prompt-template.md
---

# Run log

What actually happened. The spec says what was asked for; this says what came back.
Keeping them apart is what lets you see the difference.

**The records are the log.** One JSON file per run holds the facts, and nothing else is
written. No prose summary accompanies them. This is because a run record is almost entirely
machine-gathered fact — ids, timings, shas, counts, exit codes — and mixing those with prose
produced a 657-line document for four tasks, most of it pasted command output nobody read.

**One run, one file, and the filename carries the sequence.** A task run twice gets two
files, because a retry that succeeded and a task that worked first time are different
things. Append-only is therefore a property of the filesystem rather than a rule someone
has to remember: you cannot overwrite a previous run when it is a different file.

**Joined to the spec by id.** `T1…Tn` and `O1…On` mean what they mean in the spec; the log
never restates their content.

---

## Layout

```
.spec-artifacts/logs/<spec-id>/
└── runs/
    ├── 001-T1.json
    ├── 002-T2.json
    ├── 003-T3.json         a refused dispatch is a run record
    ├── 004-T3.json         the re-run, its own file
    └── 005-T4.json
```

The sequence prefix orders the runs and prevents collision. It is not the task id: several
files may name the same task.

---

## The record

````json
{
  "seq": 4,
  "spec": "<spec-id>",
  "task": "T3",
  "dispatched": true,
  "prompt": ".spec-artifacts/prompts/<spec-id>/T3-<name>.md",

  "started": "2026-09-12T23:28:00Z",
  "ended": "2026-09-12T23:34:00Z",
  "duration_s": 524,

  "model":  { "requested": "claude-opus-5", "actual": "claude-opus-5" },
  "usage":  { "turns": 38, "input": 4200, "output": 25000,
              "cache_write": 180000, "cache_read": 1620000 },

  "gate":   { "passed": true, "defect": null },

  "deliverables": [
    { "path": "src/service.py", "found": true,
      "symbols": [ { "name": "_parse_granularity", "found": true, "line": 42 } ] }
  ],

  "evidence": [
    { "command": "python3 -m unittest discover -s tests -v",
      "exit": 0, "summary": "Ran 50 tests, OK (+12 from 38)", "verbatim": null }
  ],

  "status": { "run": "DONE", "deliverables": "MADE", "outcome": "PASSED" },
  "commits": { "deliverables": "2187bae", "log": "5ac23a0" },
  "escalations": [ "one line each, verbatim from the run" ]
}
````

**`verbatim` is `null` on success and carries the full output on failure.** A summary of a
*failing* test result is the thing the evidence existed to replace, so a failure is
reproduced exactly. A pass is already one line — `Ran 50 tests … OK` — and pasting more of
it buys nothing.

**A refused dispatch is a record.** `dispatched: false`, `status.run: "REFUSED"`,
`gate.passed: false`, and the defect named. Nothing else is populated because nothing else
happened. Without this the log shows a task that ran cleanly first time, and the defect the
gate caught — along with what catching it cost — is invisible.

---

## The vocabularies

**RUN** — how far the task got. Says nothing about success; a task can be `DONE` and have
failed everything.

- `DONE` — a reply came back.
- `REFUSED` — the prompt was read, found defective, and **nothing was dispatched**. No agent
  ran and no files were written. The task returns to whoever wrote the prompt and will run
  once it is fixed. Distinct from `CUT`, which will never run.
- `CUT` — the task will not run. The work is already live, or the intent changed. A cut task
  keeps its id, is marked cut in the spec, and names the ADR that cut it.

**DELIVERABLES** — whether the declared artefacts exist. **The orchestrator inspects; the
agent is not consulted.** This is the one field nothing can lie about, which is why the spec
encodes deliverables in the first place.

- `MADE` · `PARTIAL` · `MISSING` · `—` (the task declared none)

**OUTCOME** — the state of the evidence for the behavioural claim.

- `PASSED` — evidence was produced and it supports the outcome.
- `FAILED` — evidence was produced and it **refutes the outcome**. Note this is a claim about
  the outcome, not about an exit code: a task whose outcome is *"an assertion exists that
  fails against the unmodified implementation"* is `PASSED` when its command fails.
- `UNVERIFIED` — no evidence was produced; the claim rests on the agent's report.
- `—` — the task declared no outcome.

The two columns have different shapes on purpose. Deliverables has no unverified state
because inspection always works. Outcome has one because behaviour cannot be inspected, only
demonstrated — and `UNVERIFIED` exists so an unprovable outcome is not recorded as green
beside a tested one.

---

## Reading them

The records are meant to be read by whatever needs them — `jq` over `runs/*.json` answers
most questions directly, and cost across a spec is a sum rather than a document.

**A human-readable view is generatable and the method does not ship one.** Rendering a
status table, the escalations and the refused dispatches from these records is
straightforward and entirely deterministic, so a repository that wants one writes it for
itself, where it can name real paths and a real command. Specified as possible here,
not supplied.

Do not hand-write one. A prose log beside the records is a second account of the same run,
free to disagree with the first, and the disagreement will not be noticed.

---

## The metrics

`model` and every field of `usage` are **read from the run's own record, not reported by the
agent** — which is what puts them beside `deliverables` as fields
nothing can lie about, where `run` and `outcome` still rest on evidence and judgement.

Where that record lives, and which of its fields lie, is a property of whatever dispatches,
so it belongs to the role that reads it and not to this template. The orchestrator's
definition carries the path, the traps in it, and the one field that must never be read back
from the dispatch request.

`model.actual` is what the run used; `model.requested` is what the prompt asked for. A
mismatch is worth noticing, and recording both is what makes it visible.

**There is no effort field.** No observed dispatch path exposes a way to set it or read it
back, so nothing here records it. A field that can only be filled by copying the request is
the one thing these records exist to prevent.

**All four token counts are recorded, because three of them cannot be reconstructed from the
fourth and they are not billed alike.** `cache_write` costs more than plain input and
`cache_read` costs far less, so a record holding only output and cache_read counts tokens
without being able to say what the run cost. They come from the transcript's usage block —
`input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` —
and from nowhere else. A count you could not find there is one you invented, and the effort
field was left out of this schema for precisely that reason.

Tokens are recorded as tokens. Converting them to money needs a rate table that goes stale.

**A task with no subagent record was run inline, not dispatched.** Record it as such rather
than folding its cost into orchestration — the gap is a finding about how the work was done.

---

## Committing

**Commit at verification: two commits per task.** The deliverables first, then the run record
naming that commit's sha. One commit cannot satisfy both rules — a
record that names a sha cannot be inside the commit that has it. Both messages carry the spec
id and the task id, so the pair is identifiable and a revert takes both.

**The rule is the handbook's: commit when the work fits the acceptance criteria.** What that
has meant in practice, per record:

| Record reads | Commit |
|---|---|
| `DONE / MADE / PASSED` | Yes — this is the boundary |
| `DONE / MADE / UNVERIFIED` | Yes; the record carries the gap so history knows it was never shown to work |
| `DONE / PARTIAL / *`, or `FAILED` | No — not to the mainline. Branch it if it needs inspecting |
| `REFUSED` | The record only. There are no deliverables to commit beside it |

Per task rather than per spec, because task boundaries are where the failure information is:
if T5 fails and T3 and T4 shipped in the same commit, the log tells you which task broke but
git cannot revert only that one.

A project that wants something else — squash per spec, nothing committed before human
review — declares it in that spec's `Constraints`, since it changes how the orchestrator may
behave. That seam is how a spec varies any standing orchestrator behaviour, not only this
one.

**A failure is not an ADR.** `T3 FAILED` is an event and belongs here. If the response is to
change approach rather than retry, *that* is a decision, and it goes in an ADR — which is
then what justifies the commit that changes the spec.
