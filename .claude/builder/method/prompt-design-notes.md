---
name: prompt-design-notes
description: The reasoning behind the prompt template — why each slot exists, what goes in it, and when it doesn't apply.
dependencies:
  - ../templates/prompt-template.md
---

# Prompt design notes

The reasoning behind `prompt-template.md` — why the slots exist, what goes in
each, and how to tell when one doesn't apply. The template is the thing you copy;
this is the thing you read when a slot is unclear or a prompt isn't working.

Descriptive, not prescriptive. Few prompts need every slot — start from the
minimal core in the template, then add the optional slots the task actually calls
for. The ordering is deliberate: models attend well to instructions placed before
the data, and to a clearly stated output contract near the end.

---

## The core idea

A good prompt answers, unambiguously, seven questions:

1. **What** must the model do, and what for? (objective)
2. **What must be true afterwards?** (outcome)
3. **What must it know** to do it? (task context)
4. **What is it operating on?** (source material)
5. **What are the rules?** (constraints)
6. **What must exist on disk when it's finished?** (deliverables — if the task
   writes anything)
7. **What should the reply look like?** (response format)

Everything else — persona, examples, reasoning steps, tone — is in service of
making those seven unmistakable. When a model gives a poor answer, the fix is
almost always to sharpen one of these, not to add more words.

Three of these pairs are easy to collapse, and shouldn't be.

**2 and 6 are different — and this is the important one.** *Deliverables* is what
**exists**: files, functions, a commit. *Outcome* is what is **true**: the
behaviour of the system once the work lands. Every deliverable can be present and
the outcome still missed — the file is there, the function is there, and it
returns the wrong numbers. Existence is checkable by looking; behaviour is not.
Declaring both is what lets a reply say more than *"I made the files."*

**3 and 4 are different.** *Task context* is what the model must know — facts,
definitions, prior decisions. *Source material* is what it operates on — the
document, the transcript, the code. The test: **does the model process this text,
or does it merely need to know it?** If the answer is derived from the text, it's
source material. If the text only shapes how the work is done, it's task context.
The two behave differently — task context stays short and sits near the
instructions; source material can be enormous and moves accordingly.

**6 and 7 are different.** A task that changes files produces a *work product* —
files on disk, tests, a commit — and separately produces a *reply* in the
message. Specify both; don't let one stand in for the other. When the work
changes nothing, question 6 doesn't apply and the reply is the whole product.

---

## Principles

- **Be specific over polite.** "Summarise in exactly 3 bullets, ≤15 words each"
  beats "please give a short summary." Vague asks get vague answers.
- **Put the query last, and size the source material's position to its length.**
  Short source material goes after the instructions: a model that reads content
  before knowing the job has no criteria to read it against. Long source material
  — a full document, thousands of tokens — goes at the *top* instead, which
  measurably improves quality on long inputs. Either way the objective,
  instructions and response contract end up last, closest to where generation
  begins.
- **Delimit the source material.** Wrap pasted content in fences or tags
  (`"""…"""`, `<document>…</document>`) so the model never confuses *instructions*
  with *content to process*.
- **State outcomes so they could be caught out.** *"Results descend by count"* can
  be wrong in a way you would notice. *"The module works properly"* cannot, which
  makes it worth nothing in a prompt.
- **Show, don't just tell.** One or two examples of the desired input→output
  often outperform a paragraph of description.
- **Constrain the reply.** If you need JSON, give the schema and say "JSON only,
  no prose." If you need a length, state it. Don't leave format to chance.
- **Give the model room to think when the task is hard.** For multi-step
  reasoning, ask it to work through the steps before the final answer. For simple
  tasks, ask for the answer directly — reasoning is overhead.
- **Tell it what to do when unsure.** "If the document doesn't say, answer
  `unknown` — do not guess." This single line prevents most hallucination.
- **Positive instructions beat prohibitions.** "Respond only with the translated
  text" works better than a list of things not to do.
- **Don't repeat what the recipient already has.** If the target model runs with
  a system prompt that already sets the persona and the house conventions, stating
  them again per prompt duplicates them — and duplicated instructions drift apart.
  If you don't know what standing context the target has, assume none.
- **Iterate on the slots, not the model.** Draft, run it, inspect where it went
  wrong, tighten the responsible slot. Prompting is empirical; the model is
  a judgement made once, before the run.

---

## The frontmatter

Four fields sit above the slots. They describe the prompt itself rather than the
task, which is why they aren't numbered.

- **`name`** — a kebab-case id; what you'd call the prompt when referring to it.
- **`description`** — one line, so the prompt can be found later by someone who
  doesn't remember its name.
- **`task`** — optional. The spec task this prompt was assembled from, by id.
  Present on a prompt written to satisfy one task; absent on a standing prompt
  that belongs to no spec and is run many times against different inputs. It is
  the join: the spec declares `T3`, this prompt carries `task: T3`, the log
  records the run of `T3` and names this file.
- **`model`** — see below.

A prompt carries no role. Persona is a standing property of whoever runs the
task, so it lives in the agent definition it is dispatched to, and a prompt
that restates it has stated it twice. A prompt dispatched to no agent has no
role at all, which is a reason to give it a definition rather than a reason to
put one in the prompt.

**Neither effort nor tools is declared here, and both were once.** No dispatch
path observed so far can apply either. A field that is stated and cannot be
applied invites an agent to honour it as prose, which puts an unmeasured
instruction into the run with nothing recording that it was said. Tools come
from the agent definition the prompt is dispatched to; effort is a judgement
with nowhere honest to record it, and saying so beats a field that pretends
otherwise.

### Judging the model

`model:` is not bookkeeping. It records a judgement about how hard the task is,
and it should be made deliberately for each prompt rather than carried over from
the last one.

**Make the judgement after filling the slots, because the filled slots are the
evidence.** Which slots you needed, and how much went into them, is what tells
you how complex the task is.

`model-selection.md`, reached through the template, carries the complexity
signals, the tiers they map to, and the rules for choosing between them. It is
not repeated here.

---

## The slots, one by one

Slot numbers match the order in `prompt-template.md`.

### 1. Objective *(always)*
The single most important slot: one or two imperative sentences saying what to do
and what it is for. *"Extract every company name and its founding year from the
text below, so the dataset can be joined on founding date."*

The imperative comes first because it anchors everything after it. The purpose
comes second because it settles the questions the imperative leaves open — how
much to include, what to do at the edges, which reading to prefer when the
instruction admits two.

Name the artefact if there is one — a JSON object, a patch, a module — so the
reply's shape is anchored before the details arrive. If the work belongs to
something larger, this is the slice of it the task is responsible for; state that
slice, not the whole programme.

### 2. Outcome *(when the task changes how something behaves)*
What is observably true once the work lands. Not what exists — that's
Deliverables — but what the system now does:

> Counting a transcript excludes every word in `COMMON_WORDS_BLACKLIST`, drops
> any word appearing fewer than `min_count_threshold` times, and returns the
> remainder in descending order of count.

**Write it so a wrong result could be caught out.** That is the whole test. An
outcome you couldn't be shown to have missed is doing no work:

```
"'the' never appears in the output"        → an outcome; falsifiable
"results descend by count"                 → an outcome; falsifiable
"the module works properly"                → not an outcome; nothing to check
"the code is clean and maintainable"       → not an outcome; a preference
```

This is the slot that makes a completion report mean something. Without it, the
strongest thing a reply can say is *"the files exist"* — which is compatible with
the task having been done wrong in every particular. Omit it when nothing changes
behaviour: an extraction, a classification, a piece of writing.

**Evidenced by — how the outcome is shown to hold.** An outcome is a claim about
behaviour, and a claim needs backing. There are only three kinds:

1. **Something runs and you see the result.** The best case. `pytest
   tests/test_word_counter.py` — a command, run before replying, output pasted.
2. **An observation is made and reported.** No test exists, but the behaviour is
   still visible: *"run `analyze-transcript --help`; the flag appears with its
   description. Paste the output."* Weaker than a test, far stronger than nothing.
3. **Nothing can evidence it.** Then say so. The reply is an assertion, and
   labelling it as one is the honest move — a fabricated command that proves
   something adjacent is worse than an admitted gap.

**Before naming evidence, check the technique exists where the task will run.** A command, a
script, a package, a mocking facility — name one the workspace does not have and the run is
wasted discovering it. This is the most common way an otherwise good prompt fails.

The mistake to avoid is reaching for whatever command exists and calling it
evidence. `ruff check` passing tells you the file parses. It says nothing about
whether stopwords are excluded, and writing it under an outcome about stopwords
makes the prompt look verified when it isn't.

**This is why evidence sits here and not under Deliverables.** It backs a
behavioural claim, not a property of a file list — files existing is checkable by
looking, and needs no command at all.

### 3. Task context *(when the model needs facts it can't infer)*
Domain facts, definitions, the situation, prior decisions — **what the model must
know**, not what it processes. Keep it relevant and short; noise dilutes
attention.

If a piece of text is going to be read, analysed, or transformed, it isn't task
context — it's source material, and it belongs in slot 8. Ask which one it is
before pasting: *does the model process this, or merely need to know it?*

Reference anything large or fast-moving by identifier rather than pasting it — a
snapshot of a changing system goes stale immediately, and a stale snapshot
embedded in a prompt reads as current, which is worse than having none.

### 4. Deliverables *(when the task writes to disk)*
What must exist when the task is done: files to create or update, and the
elements involved. **These exist in order to make the Outcome true** — that
relationship is what stops the list becoming a shopping list.

Everything here is verifiable by looking. That's the difference from the Outcome
above: existence needs no command, behaviour does.

**The test is whether the task writes to disk.** Writing a module, editing a
config, making a commit — the product is the files, and the reply is only a
report about them. Summarising, classifying, extracting, drafting a paragraph —
nothing is written, so the reply *is* the entire product, this slot is empty, and
the Response format carries the whole contract.

This is not the same as asking whether the prompt is "agentic". A prompt that
calls a search tool to answer a question uses tools and writes nothing — no
Deliverables. If a task's product lands somewhere other than disk — a sent
message, a database row — treat it the same way and name it here.

It sits here, before the Instructions, for two reasons. The steps refer to these
files by name, so they have to be introduced first. And naming them bounds the
work: the model knows exactly what it may touch before it reads anything else.

Done is both halves together: **the deliverables exist and the outcome holds.**
This slot covers the first. Neither alone is completion — a full file list proves
nothing about behaviour, and a passing command proves nothing was left unwritten.

### 5. Instructions *(when the task has more than one move)*
The sequence, numbered, one action per step. Four rules keep this slot tight:

- **The ordering test.** If the steps don't have to happen in that order, they
  aren't Instructions. *"Add type hints to every public function"* isn't step 7;
  it's true throughout, so it's a Constraint. Everything that fails the test
  moves out.
- **One action per step, imperative, as operation + target.** `ADD function
  word_counter(...)` is checkable against a diff; *"handle the counting"* isn't.
  The operations and targets are closed sets, defined in `instruction-grammar.md`
  and reached through the template, so no step is open to interpretation.
- **Don't restate the Objective or the Deliverables.** The steps are the *how*.
- **Respect the step cap** defined in `instruction-grammar.md`, reached through
  the template. A task that needs more steps than that is more than one task.

Steps that repeat or branch wrap in control flow — `FOR EACH`, `IF … THEN … ELSE`,
`STOP` — with one restriction worth knowing before you reach for it: **conditions
must be observable.** *"If `tests/` does not exist"* is a step; *"if the code is
messy"* is the model grading its own homework. There is deliberately no loop
construct; bounded retry is a Constraint, and the Outcome's evidence already says
when the task is done.

Reasoning guidance belongs here too, when the task needs it: *"work through the
steps before answering, then give only the final answer."* Omit for easy tasks.

### 6. Constraints *(almost always worth a few)*
The boundaries: length, scope, tone, what to include or exclude, edge-case
handling, and the unsure-case rule (*"if the text doesn't state it, say
`unknown`"*). Prefer positive phrasing. Standing rules that apply throughout the
task live here, not in Instructions. Tone and register go here when they matter.

### 7. Examples *(when format or judgment is hard to describe)*
One to a few input→output pairs showing exactly what you want — the most powerful
lever for format-sensitive or nuanced tasks. Keep them short, varied, and
representative, including a tricky case if one matters.

```
Input: "Acme was started in 1999."
Output: {"company": "Acme", "founded": 1999}
```

### 8. Source material *(whenever the model operates on supplied content)*
The actual content to be processed — **what the model reads, analyses, or
transforms**, as opposed to the framing facts in slot 3. Always delimited:

```
<document>
{{paste content here}}
</document>
```

**This is the one slot whose position depends on its size.**

- **Short** — a paragraph, a snippet, a handful of records. Leave it here, second
  to last, just before the response contract. The instructions arrive first and
  give the model criteria to read it against.
- **Long** — a full document, a transcript, thousands of tokens. Move the whole
  slot to the **top**, above the Objective. Placing longform material at the top
  of the prompt measurably improves quality on long inputs, and it also puts the
  bulk in a stable prefix that prompt caching can reuse across repeated queries.

When you move it up, state the job in one line before it — *"You will answer
questions about the transcript below"* — so it still isn't read blind, then put
the full Objective, Instructions and Response format after it. The query always
ends up last, whichever way the material goes.

### 9. Response format *(almost always)*
The exact shape of the reply: a schema, a template, a length. It goes last
because it's read closest to where generation begins — it shapes the first token.

**Where there are Deliverables and Outcomes, the reply reports against them
first** — one line per deliverable marked done or not done, one line per outcome
with its evidence. That is the self-check, and it is worth having because it is
*specific enough to be caught out*: a list of declared items forces the model to
walk them one at a time, and "not done" is an available answer, so a partial
result reports itself instead of being summarised over.

Demanding evidence beats demanding compliance. *"Confirm you ran the tests"* can
be satisfied by saying you did; *"the test output verbatim"* cannot.

If the output is parsed downstream, or read by another agent, be strict:

> *"One line per deliverable, then each outcome's evidence verbatim. Nothing
> else."*

For agentic tasks, keep it short on purpose. An agent that writes five hundred
words about what it just did is burning context someone has to read.

---

## Worked example

A task that changes files, filled in. Note how few slots it needs: no Examples
and no Source material — the model isn't processing a document here, it's
writing one, so slot 8 is empty and slot 3 carries the little it needs to
know.

````markdown
---
name: word-counter
description: Word frequency counter with stopword filter and count threshold.
model: claude-opus-5
---

# Objective
Implement the word counter for the transcript analytics CLI, so a transcript can
be reduced to the words that actually characterise it.

# Outcome
Counting a transcript excludes every word in `COMMON_WORDS_BLACKLIST`, drops any
word appearing fewer than `min_count_threshold` times, and returns the remainder
in descending order of count.
- **Evidenced by:** `pytest tests/test_word_counter.py` — run before replying,
  output pasted.

# Task context
`WordCounts` is defined in `data_types.py` and `COMMON_WORDS_BLACKLIST` in
`constants.py`; both already exist. Neither file changes in this task.

# Deliverables
- **CREATE** `src/transcript_analytics/word_counter.py`
- **Function(s):** `word_counter(script: str, min_count_threshold: int = 10) -> WordCounts`

# Instructions
1. CREATE `src/transcript_analytics/word_counter.py`.
2. ADD function `word_counter(script: str, min_count_threshold: int = 10) -> WordCounts`.
3. Normalise the input: lowercase, strip punctuation, split on whitespace.
4. REMOVE any word present in `COMMON_WORDS_BLACKLIST`.
5. Drop words whose count is below `min_count_threshold`.
6. Sort descending by count and return `WordCounts`.

# Constraints
- Standard library only.
- Type hints and a docstring on every public function.

# Response format
One line per Deliverable, marked done or not done. Then the Outcome with its
evidence — the `pytest` output verbatim. No summary.
````

Steps 3–6 are genuinely ordered — you can't filter stopwords before normalising
case, and thresholding before filtering gives a different answer. That is the
ordering test passing. Compare the prose version that usually gets written —
*"create a word counter module that counts words, filtering common words and
respecting a threshold, sorted by count"* — one sentence holding six decisions,
none of them individually verifiable.

Note what the Outcome adds. Without it, the strongest report available is *"I
created the file and the function"* — true of an implementation that sorts
ascending, or forgets the threshold entirely. With it, the reply has to say what
makes each behaviour true, and a miss has somewhere to show up.

---

## Quick patterns

- **Task that changes files** — Objective + Outcome (with its evidence) + Task
  context + Deliverables + Instructions (ordered, operation + target) +
  Constraints + a strict, short Response format reporting against both.
- **Extraction / structured output** — Objective + delimited Source material +
  strict schema + "JSON only" + unsure-rule. One example if the schema is
  non-obvious. No Outcome — nothing changes behaviour.
- **Generation (write something)** — Objective + Task context + Constraints
  (length, tone, must-include) + Response format. The persona is the agent's,
  not the prompt's. Few-shot if you have a house style.
- **Classification** — Objective + the label set with one-line definitions +
  "choose exactly one" + an example per ambiguous label + Response format (the
  label only).
- **Analysis / reasoning** — Objective + Source material + "think step by step,
  then give the final answer as <format>." Separate the working from the
  conclusion.
- **Long-document Q&A** — Source material *first*, preceded by a one-line
  statement of the job, then Objective + Constraints + Response format at the end.
