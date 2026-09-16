# Incident — outcome clauses shipped with evidence that could not fail

**Date:** 2026-09-16
**Raised by:** the operator, on reviewing the run. Four of the defects below were caught by
the orchestrator's gate questions 1 and 3; two were found by an audit the author ran after
the third refusal; two more were found by the author only after the code was committed.
**Spec:** `trading-demo-backend`, `trading-demo-frontend`
**Outcome:** all defects repaired. 308 backend tests pass, the frontend builds, and no wrong
value reached the emitted contract or a user.

## What happened

| # | Defect | Where | Caught by |
|---|---|---|---|
| 1 | The prompt named fourteen response models and stated **no field for any of them**; the spec did not either. Its own constraint said to stop if a shape was not determinable, and none was. | T1 prompt, `trading-demo-backend` | The **implementor**, which derived all fourteen shapes from surrounding tasks and documented every judgement — *after* writing them. The orchestrator escalated rather than continuing. `001-T1.json` records the run as passed. |
| 2 | Evidence asserted the cap, the eviction order and the two session queries. A session-window query reads `t`, `close` and `volume` and nothing else, so the suite passed against a `Bar` carrying **no `contributions` and no `residual`** — the two fields holding O5's reconciliation. | T4 prompt **and** spec block | The **gate**, questions 1 and 3, before dispatch. `003-T4.json` REFUSED. |
| 3 | Per-factor shock, drift, half-life and the volatility multiplier were declared by T3's Objective and asserted by nothing. | T3 prompt and spec | The **author's audit**, prompted by defect 2, before dispatch. |
| 4 | `Quote.sparkline` was declared and read by no assertion; an empty list passed. | T6 prompt and spec | Same audit, before dispatch. |
| 5 | `GET /scenarios` listing the library, and `GET /scenario` carrying the headlines, were outcome clauses with no assertion. | T9 prompt and spec | Same audit, before dispatch. |
| 6 | Evidence never called `GET /symbols` without a query at all — the clause the prompt itself marks as load-bearing for a later task. Only the *exclusion* half of the fuzzy match was asserted; a matcher returning nothing for every query satisfied it. | T6 prompt and spec | The **gate**, questions 1 and 3. `011-T6.json` REFUSED. |
| 7 | The assertion added to close O1's other half — `assert app.router.lifespan_context` — **cannot fail**. FastAPI installs `_DefaultLifespan` when no `lifespan=` is passed, and it is truthy. | T5 prompt and spec | The **gate**, question 3, which ran it against the installed FastAPI rather than reasoning about it. `012-T5.json` REFUSED. |
| 8 | Four independent polling timers, where O14's entire content is one shared cadence for the application. | committed frontend | The **author**, checking outcomes by hand **after commit**. Nothing was gating. |
| 9 | O23 banned every `px` value. The approved mockup carries 53 of them, and a CSS media query cannot read a custom property at all — the rule was unsatisfiable by its own design target. | O23, the visual rule, T13's grep | The **author**, running the grep **after** writing ten components against the rule. |

A tenth defect — the engine stranding a scenario's shock level when another replaced it —
is the subject of ADR-003 and not of this record: it was a modelling position, not evidence
that failed to check something.

## Cause

**The shape:** an outcome was stated in prose, and its evidence was written from that same
prose in the same sitting. Evidence written that way asserts what is easy to assert rather
than what the outcome claims, and the gap is invisible to the author because both halves
came from one reading.

Three exact instances, because the shape is what transfers and the instance is what makes it
believable:

- **Defect 1** — the enumeration `Quote, Candle, SymbolMatch, …` was copied from the spec's
  deliverable line into the prompt's instruction step. Both documents then asserted the list
  was *complete*; neither ever asserted what any entry *contained*. The evidence checked that
  each model rejected a missing required field, which is true of a model with one field.
- **Defect 2** — the Definitions named eight `Bar` fields. The evidence named the queries.
  Nobody checked that the queries touch six of the eight.
- **Defect 7** — the evidence said "assert `lifespan_context` is set". `is set` is a
  property of the attribute, not of the application, and FastAPI sets it unconditionally.
  The author's second attempt — identity against the `lifespan` function — was *also* wrong,
  because `include_router` merges lifespan contexts, so both the attached and unattached
  cases become wrapper functions. No static check on that attribute can discriminate.

**The role matters and it is the same one throughout: the author.** Every defect above is in
a prompt or a spec, not in an implementation. The implementors and the orchestrator behaved
correctly in every instance, including the one where an implementor declined to stop and
documented its reasoning instead.

## What it cost

- **Four refused dispatches** — `003-T4`, `005-T4`, `011-T6`, `012-T5` — each stopping the
  run and requiring the author to re-open the spec and the prompts.
- **Two tasks rebuilt.** T1 ran twice (`001`, `002`) and T4 three times (`003` refused,
  `004`, `005` refused, `006`).
- **Six commits written to repair rather than to build**, across the spec, four prompts and
  the frontend.
- **Defects 8 and 9 reached committed code**, because the frontend was written without a
  gate — see PR-001. Both were repaired within the same session.

And what was contained:

- **No wrong value reached the emitted contract.** T11 froze `openapi.json` only after the
  response models had been authored into the spec, so the contract the frontend generates
  from was decided by an author, not derived by an implementor.
- **No incorrect number reached a user.** Every defect was in what the evidence *checked*,
  not in what the code *did*; the backend's arithmetic was correct throughout, and its
  reconciliation held to 1.68e-16 against a 1e-6 tolerance from the first run of T25.
- **The gate caught six of the nine before anything was built on them.** Defects 3, 4 and 5
  never reached a dispatch at all.

## What was done

Each defect's evidence was rewritten to read the thing the outcome claims, and — deliberately
— to carry the reason inline, so the next edit to that prompt cannot drop the assertion
without reading why it exists.

Two departures from what was planned, recorded because they are decisions someone can
disagree with:

- **After the third refusal, the author audited the remaining tasks for the same shape rather
  than waiting for the gate to find each one.** This found defects 3, 4 and 5. It spent
  author time to avoid three more refusal cycles.
- **Defect 7's repair abandoned static assertion entirely.** The test now enters the
  application's own lifespan through `TestClient` and watches the bars grow. It was verified
  by removing `lifespan=`, confirming the test fails, and restoring it — because two previous
  attempts at this assertion had both been vacuous, and asserting a third without proving it
  could fail would have been the same mistake a third time.

## What would have caught these earlier

- **For each outcome clause, name the assertion that reads it, and check the mapping is
  total.** Mechanically catches defects 2, 3, 4, 5, 6 — each is a clause with no assertion.
  It does **not** catch 1, 7, 8 or 9, where an assertion existed and was too weak.
- **For every assertion, describe the wrong implementation that would satisfy it.** This is
  already written in `prompt-template.md` under *Evidence must discriminate this task*, and
  it was not applied. Catches 1 (a model with one field), 7 (an app with no lifespan) and 6
  (a matcher returning nothing). Does not catch 3, 4 or 5, where nothing was asserted at all.
- **Run the negative case.** Delete the line the assertion is meant to protect and confirm
  the test fails. Catches 7 outright and would have caught 1. Costs one command per
  assertion and is the only control here that produces evidence rather than an opinion.
- **For an enumeration, assert its contents and not only its length.** Catches 1 directly.

## What is still open

- **The frontend has no equivalent of the gate**, by the decision recorded in PR-001. Defects
  8 and 9 were found by an author checking their own work, which is the arrangement that
  produced every defect in this record. Nothing has changed that for the frontend.
- **The "describe the wrong implementation" control exists in the template and was not
  used.** Why a written control went unapplied is not answered here, and a control that is
  available and ignored is worth no more than one that does not exist.
- **Defect 9 means O23 was wrong for the whole run**, not merely unenforced. Any other
  outcome asserted against an artifact nobody tried to satisfy may be in the same state; no
  audit of the remaining outcomes has been done.
