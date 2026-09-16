---
name: instruction-grammar
description: The language of instruction steps — the closed set of operations and targets, and the control flow allowed to wrap them.
---

# Instruction grammar

The language an instruction step is allowed to use. Every step names an
**operation** and a **target**, both drawn from the closed sets below, optionally
wrapped in **control flow**. The sets are closed — if the word you want isn't
here, the step is doing something the grammar doesn't cover, which usually means
it's doing more than one thing.

The point is verifiability, not brevity. `ADD function word_counter(...)` can be
checked against a diff; *"handle the counting"* can't.

---

## The grammar

```
[control flow]
  <file operation>    <path>
  <element operation> <element type> <name>   [in <path>]
```

Combined, one step reads:

```
UPDATE `src/main.py` — ADD function `analyze(path: str) -> Report`
```

The file operation says what happens to the file. The element operation says what
happens inside it. A step may use either alone: `CREATE src/parser.py` needs no
element clause; `REMOVE function legacy_parse()` needs no file clause when the
file is already established.

---

## File operations

What happens to the file as a whole.

| Verb | Means |
|---|---|
| `CREATE` | The file does not exist and will |
| `UPDATE` | The file exists and its contents change |
| `DELETE` | The file exists and will not |

## Element operations

What happens inside a file.

| Verb | Means |
|---|---|
| `ADD` | A new element that did not exist before |
| `REMOVE` | An existing element, gone |
| `MOVE` | The same element, at a different location or scope — original does not remain |
| `COPY` | A duplicate of an existing element — original remains |
| `REPLACE` | An existing element swapped for a new one in the same place |

There is no verb for *writing something at runtime*. A step describes what the
agent does to the codebase; "the report is written to `out.json`" is what the
code does when it runs, which is an **Outcome**, not a step. Read as an agent
action it is just `CREATE`/`UPDATE` on a file, which already exists above.

## Element types

What is being acted on.

| Type | Means |
|---|---|
| `var` | A variable or constant |
| `function` | A function or method |
| `class` | A class |
| `type` | A type, interface, schema, or dataclass |
| `file` | A file, when it is the object rather than the location |
| `default` | A default value or fallback |

---

## Control flow

Three constructs wrap a step. They exist so that repetition and branching don't
have to be written out longhand — five files times two operations is ten steps,
and a task that looks too big when it isn't.

| Construct | Means |
|---|---|
| `FOR EACH <collection>` | Apply the wrapped step(s) to every item. The collection must be enumerable — a named list, a glob, the files in Deliverables |
| `IF <condition> THEN … / ELSE …` | Branch. Both arms are steps in this grammar |
| `STOP` | Abort and report. The terminal arm of a condition that must hold |

```
FOR EACH file in `src/handlers/*.py`
  ADD function `validate(payload: dict) -> bool`

IF `tests/` does not exist THEN
  CREATE `tests/`
ELSE
  STOP — report that the layout is unexpected
```

### Conditions must be observable

**Name what you would look at to decide.** A condition is legal when a person or
a command could check it without judgement:

```
IF `tests/` does not exist                → legal, a path check
IF `ruff check` exits non-zero            → legal, an exit code
IF `Config` has no `timeout` field        → legal, readable in the source

IF the code is messy                      → not legal, no observable
IF it seems necessary                     → not legal, no observable
IF the tests are inadequate               → not legal, judgement dressed as a check
```

An unobservable condition is the model grading its own homework, and the step
stops being checkable — exactly what the closed sets exist to prevent.

### There is no loop

`UNTIL` and `WHILE` are deliberately absent. *"Retry until `pytest` passes"* is
unbounded, and an agent will grind on it. It also duplicates the evidence the
task already carries, which is what defines when the task is done — and
re-running after a failure is the harness's job, not the prompt's.

If you want a *tighter* bound than the agent's own, it's a Constraint, not a step:
*"one attempt only, then stop and report the failure."* A Constraint can lower an
agent's bound and cannot raise it — asking for more attempts than the role allows
is a defect the agent reports rather than an instruction it follows.

---

## Usage

- **One operation per step.** A step with two verbs is two steps. Control flow
  doesn't count as a verb — `FOR EACH … ADD …` is one operation, repeated.
- **Always name the target.** `REPLACE parser` is not a step — replace it with
  what? Give the element type and the name.
- **Verbs uppercase, targets in backticks.** Consistent shape makes a step
  scannable and makes the operation greppable across a set of prompts.
- **Cap a task at seven steps.** More than that and it is more than one task;
  split it rather than writing a longer list. A `FOR EACH` is one step against
  the cap, not one per item — if collapsing repetition is the only way to get
  under it, that's a signal the task is fine; if it still doesn't fit, the task
  is genuinely too big.

Legal:

```
CREATE `src/transcript_analytics/word_counter.py`
ADD function `word_counter(script: str, min_count_threshold: int = 10) -> WordCounts`
REMOVE var `LEGACY_STOPWORDS` in `constants.py`
REPLACE type `Config` with a frozen dataclass in `settings.py`
MOVE function `normalise()` from `main.py` to `text_utils.py`
FOR EACH file in `src/handlers/*.py` — ADD type hints to every public function
IF `pyproject.toml` has no `[tool.ruff]` section THEN ADD one
```

Not legal, and why:

```
Sort out the entry point                → no operation, no target
UPDATE and REFACTOR `main.py`           → two operations in one step
ADD the counting logic                  → target is not an element type
REPLACE `parser`                        → names no replacement
UNTIL `pytest` passes, fix the code     → unbounded; the evidence covers this
IF the module looks wrong THEN rewrite  → condition is not observable
FOR EACH thing that needs fixing        → collection is not enumerable
```
