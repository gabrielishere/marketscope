# Incident — decisions authored in the spec that never reached the prompt

**Date:** 2026-09-16
**Raised by:** the operator, on reviewing the run. Both dispatch-stopping instances were
caught by the orchestrator's gate; one was caught only after an implementor had committed
against the gap.
**Spec:** `trading-demo-backend`
**Outcome:** repaired. All twelve backend prompts now carry the spec's path and a precedence
rule. T4 ran three times in total and passed on the third.

## What happened

| # | Defect | Where | Caught by |
|---|---|---|---|
| 1 | The prose "market, rates/duration, oil, USD, credit spread" appeared in the spec's Constraints and in four prompts. **None of them said how a factor is spelled as a key.** The canonical key set came to exist in committed code — `FACTORS` in `buffer.py`, enforced at runtime by `Bar` — and in no artifact. | spec Constraints; T2, T3, T4, T25 prompts | The **implementor**, which escalated rather than letting T2 inherit the spelling, and the **orchestrator**, which held before dispatching T2 rather than running it. But *after* T4 had committed the prose tuple: `004-T4.json` DONE/MADE/PASSED. |
| 2 | The **Buffer boundaries** decision was authored into the spec's Definitions and never copied into T4's prompt, which inlines its definitions. The prompt's Constraints therefore still instructed the implementor to **STOP** on a boundary case the author had just settled. | T4 prompt | The **gate**, question 5, before dispatch. `005-T4.json` REFUSED. |
| 3 | A prompt cited "the spec's *Response models* section" without naming the spec file, because the sentence identifying the spec had been removed in the same commit that added the reference. | T1 prompt | The **implementor**, which located it with one grep. No cost; reported in the run record. |
| 4 | T8 still described factor order with the prose names, while `/macro` sets `MacroDriver.factor` — a field that reaches the client as generated TypeScript. | T8 prompt | The **author's audit**, before dispatch. |

The choice of `market, rates, oil, usd, credit` over the prose spelling is a position with
real alternatives and is recorded in ADR-001, not here. This record is about how the
question came to be answered in committed code before it was answered in a document.

## Cause

**The shape:** every prompt **inlines** the spec's definitions rather than referring to
them. A spec edit therefore has to be hand-copied into however many prompts restate that
term, and a missed copy is **invisible from the spec side** — the spec reads correctly, the
prompt reads plausibly, and only dispatching the pair together reveals that they disagree.

Defect 2 is the exact instance. The commit that authored **Buffer boundaries** into
`## Definitions` touched the spec and did not touch T4's prompt, whose Task context
reproduces five other Definitions entries. The prompt was left in a state no reader of
either document alone would notice: its Constraints said *"if the definitions above leave a
boundary case undetermined … STOP"*, and "the definitions above" meant the prompt's own copy,
where the case was still undetermined.

Defect 1 is the same shape with the copy count at zero: the term existed in five places and
was never *settled* in any of them, so the first task that needed it settled it — in code.

**The role is the author in every case.** The implementors escalated correctly and the
orchestrator refused correctly. Defect 1 is the one worth dwelling on: it was caught by an
implementor's judgement, not by a check. An implementor that had simply reproduced the prose
and moved on would have left the key set undocumented and the run would have looked clean.

## What it cost

- **Two refused dispatches** — `005-T4` for defect 2, and the hold before T2 for defect 1.
- **T4 rebuilt twice.** `004-T4.json` passed and was then superseded, because its committed
  `FACTORS` held the prose spelling and `instruments.json` would have failed against it.
- **A commit's worth of spec and prompt edits** for each, plus the propagation of the key
  set into five prompts and two specs.

And what was contained:

- **The wrong key set never reached `instruments.json` or the contract.** T2 was held before
  dispatch, so no data file was written against the prose spelling and `openapi.json` was
  emitted with the authored keys.
- **No implementor silently resolved a term that more than one task reads.** In the one case
  where an implementor had to choose, it chose, said so, and named the decision as the
  author's to make.
- **Defect 3 cost nothing**, which is the useful comparison: a prompt that points at a file
  degrades to a grep, while a prompt that inlines a stale copy degrades to a wrong answer.

## What was done

T4's prompt was given the **Buffer boundaries** entry in full and its contradicting
constraint rewritten to say the boundary cases are settled. The factor keys were authored
into both specs' Definitions and propagated to five prompts.

The structural repair, and a deliberate departure from repairing only what the gate found:
**all twelve backend prompts — and later all twelve frontend prompts — now open their Task
context with the spec's path and the rule that where prompt and spec disagree, the spec
governs and the disagreement is a defect to report rather than resolve.**

That does not prevent a missed copy. It converts one from an invisible divergence into
something the agent holding the prompt can detect, which moves detection from the gate to
the dispatch and from the author to the reader.

## What would have caught these earlier

- **Grep the prompts for every term a spec edit touches, before committing the edit.** For
  `Buffer boundaries` this is one command and it catches defect 2 outright. It catches
  defect 4. It does **not** catch defect 1, because there was no term to grep for — the
  spelling had never been written down.
- **For any term more than one task reads, require it in Definitions before the first task
  that needs it is dispatched.** Catches defect 1. This is what `## Definitions` is already
  for; the failure was not noticing that a key spelling is such a term.
- **Prompts refer to the spec by path rather than inlining it.** Catches the whole class by
  making divergence impossible, and was rejected as a full repair: a prompt that carries
  nothing is a prompt an implementor cannot act on without reading two documents, and the
  method's own position is that the prompt is the whole instruction. The precedence rule is
  the compromise, and it is a mitigation rather than a control.

## What is still open

- **The precedence rule is untested.** No prompt has since diverged from its spec, so
  nothing has yet demonstrated that an agent reading it will actually report the divergence
  rather than follow the prompt.
- **Inlining remains the practice.** Every prompt still reproduces its definitions, so the
  hand-copy step that caused this still exists on every future spec edit.
- **Nothing checks that a Definitions entry appears in the prompts that need it.** The audit
  that found defect 4 was manual and was run once.
