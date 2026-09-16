---
name: prompt-template
description: The fillable prompt skeleton — frontmatter plus nine ordered slots.
dependencies:
  - instruction-grammar.md
  - model-selection.md
---

# Prompt template

Copy this, delete every slot the task doesn't need, and keep the order — the
order is the contract, even when slots are missing.

Objective, Outcome and Deliverables are one chain: the objective is what and why,
the outcome is what changes, the deliverables are what exists to make it change.
A reply reports against the last two.

Instruction steps are written in
[`instruction-grammar.md`](instruction-grammar.md). The `model:` field is a
judgement about task complexity — make it with
[`model-selection.md`](model-selection.md), not from habit.

---

````markdown
---
name: <kebab-case-id>            # what this prompt is called
description: <one line>          # what it does, so it can be found later
task: <T3>                       # optional — the spec task this was assembled from
model: <model-id>                # chosen by judging task complexity, not by habit
#                                effort and tools are NOT declared here: no dispatch path
#                                observed so far can apply either, and a field that is stated
#                                and cannot be applied invites an agent to honour it as prose.
#                                Tools come from the agent definition the prompt is dispatched to.
#                                That definition also carries the standing rules a prompt does not
#                                restate, so a prompt is complete only when dispatched to the agent
#                                it was written for. Name that agent in the spec if it is not the
#                                default. `model:` is the full ID; dispatch maps it to a short
#                                alias per model-selection.md.
---

# Objective
<One or two imperative sentences stating what to do, then what it is for. The
single most important slot — everything below serves it. Name the artefact if
there is one: a JSON object, a patch, a module. If the work belongs to something
larger, this is the slice of it this task is responsible for.>

# Outcome                         [what changes in the system's behaviour]
<What is observably true once this is done — stated so a wrong result could be
caught out. "Results descend by count" is an outcome; "the module works" is not.
This is what the Deliverables are for; they exist to make it true.>
- **Evidenced by:** <how it is shown to hold — a command to run, or an
  observation to make and report. If nothing can evidence it, say so; the reply
  is then an assertion, not proof. **It must discriminate what this task added,
  not report accumulated state** — see below.>

# Task context                    [what the model must KNOW — not what it processes]
<Facts, definitions, prior decisions the model needs and cannot infer. Keep it
short. Reference large or volatile material by identifier — a version, a date, a
commit — rather than pasting it in.>

# Deliverables                    [only if the task writes to disk — omit otherwise]
- **CREATE/UPDATE** `path/to/file.ext`
- **Function(s):** `name(args) -> ReturnType` — what it does
- **Evidence:** `path/to/file.ext` — what demonstrates the behaviour holds

# Instructions                    [omit for a single-move task]
1. <One action. Imperative. Operation + target.>
2. <...>
3. <...>

# Constraints
- <length / scope / tone>
- <what to include or exclude>
- If <information is missing / input is invalid>, then <fallback — e.g. answer
  "unknown", do not guess>.

# Examples                        [when format or judgment is hard to describe]
Input: <example input>
Output: <exactly the desired output>

# Source material                 [what the model PROCESSES — move to the top if long]
"""
{{paste the content to be operated on here}}
"""

# Response format
<First, report against what was declared: one line per Deliverable, each marked
done or not done; then one line per Outcome with its evidence — the command
output, the observation, or a plain statement that none was available.>
<Then the exact shape of the reply: schema, template, length. State "X only, no
extra prose" if it will be parsed, or read by another agent.>
````

---

## Evidence must discriminate this task

A command whose output reflects the **accumulated** state of the workspace cannot show what
this task contributed. Two forms of the same defect:

- **The empty case passes.** A test runner over a directory with no tests prints a success
  line and exits zero. Declared as evidence, it is satisfied whether or not anything was
  written.
- **The inherited case passes.** Once earlier tasks have left tests behind, a green run and
  a non-zero count are true no matter what this task did.

**State the delta.** Not *"the suite passes"* but *"the suite passes and the count is higher
than N"*, naming N. Not *"a file exists"* but which symbol it now contains. Where the task
adds behaviour, name a value that is different because of it.

The check that catches this while it is still cheap: **describe the wrong implementation
that would satisfy every declared piece of evidence.** If you can write one, the evidence is
not yet discriminating, and the fix is to replace a description with a value only the
correct implementation produces.

---

## Minimal core

Most prompts whose only product is the reply need three slots:

```markdown
# Objective
<one or two imperative sentences>

# Source material
"""
{{content}}
"""

# Response format
<the exact shape you want back>
```

Add slots only when a run shows you need them.
