---
name: model-selection
description: Pick the model for a prompt from the shape of its task — signals, tiers, and the exact IDs.
source: https://platform.claude.com/docs/en/about-claude/models/choosing-a-model
retrieved: 2026-09-06
---

# Model selection

Everything needed to choose a model for a task. Read the task, pick an ID, move
on.

Do this **after** the slots are filled — they are the evidence — and never from
habit or from what the last prompt used.

---

## 1. Read the complexity off the filled slots

| Signal | Points toward |
|---|---|
| No Deliverables; short Source material; a closed output (one label, a fixed schema) | Lower |
| Deliverables naming one file; Instructions of one or two steps | Lower |
| Deliverables spanning several files, or five or more instruction steps | Higher |
| Steps with genuine interdependency — later ones only make sense after earlier ones | Higher |
| An Examples slot needed because judgment was too subtle to describe | Higher |
| Long Source material that has to be synthesised rather than scanned | Higher |
| The prompt will run unattended for a long stretch, or drive other agents | Higher |

Two or more "higher" signals is a genuinely complex task. None of them, and the
task is mechanical however long it looks.

## 2. Match the task to a model

Ordered by capability and cost. **`claude-opus-5` is the default** — choose
another only when the task clearly sits above or below it.

| Task shape | Model | Dispatches as | Context | $/1M in → out | Typical work |
|---|---|---|---|---|---|
| Mechanical, high-volume, closed output | `claude-haiku-4-5` | `haiku` | 200K | $1 → $5 | Extraction against a fixed schema, classification into a known label set, reformatting, sub-agent tasks |
| Everyday coding and analysis | `claude-sonnet-5` | `sonnet` | 1M | $2 → $10 | One well-specified module, a data transformation, ordinary agentic tool use |
| Complex agentic or enterprise work — **default** | `claude-opus-5` | `opus` | 1M | $5 → $25 | Multi-file changes, large refactors, complex systems work, long-horizon autonomous coding |
| Highest capability | `claude-fable-5-1` | `fable` | 1M | $10 → $50 | Sessions running for hours, multistep research, analysis carried through to a finished document or deck |

Use the ID strings exactly as written — they are complete. Never append a date
suffix.

**The `model:` field and the dispatch parameter are different vocabularies.** A
prompt records the full ID, because that is what pins a version against the price
and context columns above. The `Agent` tool's `model` parameter accepts only the
short aliases in the *Dispatches as* column, and the agent definitions in
`.claude/agents/` declare those aliases too. Whoever dispatches maps one to the
other using this table. Recording the alias in a prompt instead would make
dispatch literal but would lose the version, and the columns beside it would stop
meaning anything.

**When unsure, go up.** The judgement is made once, before the run, so there is
no cheap correction from below — an under-powered model produces a plausible bad
result that costs more to diagnose than the tier upgrade would have cost.

**Watch the context column.** Long source material rules out `claude-haiku-4-5`
regardless of how mechanical the task is.

---

*Tier guidance derived from
[Choosing the right model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model),
fetched 2026-09-06. Model IDs, context windows and prices are a snapshot taken
2026-06-24 and go stale — re-check them against the source above before relying
on a price.*
