---
name: requirements-template
description: What the input and the system say, extracted and cited — the document intake fills and the spec is drawn from.
dependencies:
  - ../method/reading-the-input.md
  - spec-template.md
---

# Requirements template

**Read it before the input** — it names what to go looking for. **Fill it after** — the filled
document is intake's whole output. The double duty is the point: an extraction with no schema
finds whatever the reader happened to notice.

**Every line carries a citation** to something outside this method's own artefacts — a line of
the input, a file and line of the code, a measurement of the data. A line that cites neither
came from you, and it belongs in a decision record where it can be argued with.

**It holds observations, not conclusions.** What to build, which option won, how the work is
sequenced — those belong to the spec and to decision records. A second copy of a conclusion is
free to disagree with the first, and it will.

**A slot the input does not fill is recorded empty.** Not inferred, not filled with the
plausible answer. An empty slot under its own heading is a finding someone has to say out
loud; the same gap buried inside a sentence is one nobody notices.

---

````markdown
---
input: <the brief, ticket, thread or transcript this was read from>
---

# What this is
<One paragraph. What the thing does, and what exists because of it.>

# Who it serves
<The user, by role. Quoted where the input names one.>

# Decision workflow
<What the answer feeds — the decision someone makes with it — and what would make it wrong
for that purpose. Two different questions, and an input often answers only the second.
Record either one empty rather than inferring it.>

# What is authoritative
<Where each value comes from, which source wins when two disagree, and the conventions a
value carries that its type does not: units, calendars, timezone, currency, precision. A
convention the system does not model is recorded as absent, not supplied.>

# Scope choices
<What is in and what is out, each against the line of the input that draws the boundary.>

- in:  <…> — <citation>
- out: <…> — <citation>

# Assumptions
<Each one stated, with what breaks if it is wrong.>

- <assumption> — unverifiable because <…>; if wrong, <what it invalidates>

# Ruleset

## Bounds on the work
<What you may build with. Discharged by the thing you build: violate one and the
deliverable shows it.>

- "<quoted>" — <citation>

## Preserved behaviour
<What already exists and must survive. Discharged by nothing you build — its subject is
outside the spec, so it needs a task that captures it before anything modifies it.>

- "<quoted, or observed>" — <citation>
  referent:  <which surface, whose behaviour> — <citation>
  currently: <what it does today, measured>

# Open questions
<Each with a person's name against it.>

# Dropped
<What had no destination, and why. Recorded so a later reader can tell
considered-and-rejected from missed.>
````

---

## How the parts work

**The ruleset splits two ways because only one half can check itself.** A bound on the work —
a stack, a dependency limit, where files may go — is discharged by the deliverable: violate it
and the thing you built shows it. A bound on preserved behaviour is not. Its subject already
exists, the spec never describes it, and nothing you write can check it until something
captures what it currently does. That is why the second list names a **referent** and a
**currently**: the referent says whose behaviour, and `currently` is where the measurement
lands. An entry with a filled `currently` and no task against it is the shape of a regression
waiting to happen.

**Scope choices exist because inputs state the scope more than once.** A request quoted from
the requester, and a task line written by whoever scoped it. Sorting each into its own
destination files them both and compares neither — so diff them, and record any set one names
that the other does not.

> *Evidence (n=1).* A brief's task line said *"add monthly and quarterly granularity"* while
> the requester's quoted examples asked for months, quarters and a calendar year. Both were
> filed, neither was compared, and annual granularity shipped without the requester ever
> asking for it.

**Assumptions are not open questions.** An open question has someone's name against it and is
waiting for an answer. An assumption is something you could not verify and chose to proceed
on — so it carries what breaks if it is wrong, and that consequence is the thing a reader
needs. If you could have checked it and did not, check it; that is not an assumption, it is an
omission.

**`Decision workflow` is the slot most often filled with the plausible answer.** An input
usually says what the user *asks for* and what they *do today*, and rarely says what the
number is then used for. Recording it empty is the correct result, and it changes what you
build: without it, the strongest design you can justify is one that discloses its own
provenance and lets the user judge.

**What this document is not.** Not a decision list — those are sorted at Pass 3 and land in
decision records and the spec's `Constraints`. Not a plan. Not a restatement of what the spec
will say. If a line here would also be true of the spec, it belongs in the spec and nowhere
else.
