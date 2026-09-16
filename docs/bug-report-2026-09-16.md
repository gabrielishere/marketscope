# Bug report — 2026-09-16

Two defects found by reviewing screenshots of the running application against the outcomes
the specification asserts. One is fixed; one is recorded and deliberately not fixed, with the
reason stated.

Neither was found by a test. Both were found by looking at the thing.

---

## BUG-001 — The markets table's volume column read `0` for every instrument

**Status:** fixed
**Severity:** the column presented a number that was always wrong
**Found:** reviewing `docs/screenshots/02-markets.png`, then confirmed by querying the
rendered DOM rather than by reading the image

### What was wrong

Every one of the forty-five rows in the markets table rendered `0` in its Volume column.
Confirmed against the live page rather than inferred:

```
instrument rows rendered: 45
sector groups rendered:   8
distinct volume values:   [ '0' ]
```

### Cause

`Quote` — the model `GET /quotes` returns, and the only per-poll payload the markets table
receives — carried no volume field. `SymbolMatch`, served by `GET /symbols`, carries the
static metadata; session volume is not static, so it was on neither.

The component was written against that gap with a placeholder:

```ts
dayChangePct: quote.day_change_pct,
sessionVolume: 0,          // ← nothing to bind, so a literal shipped
```

The placeholder was mine, written while building the component, and never revisited. Nothing
caught it because nothing asserted it: `Mover` carries `session_volume` and `/movers` was
tested for it, so the field existed in the contract — just not on the model this surface
reads.

### Why no test caught it

This is the defect class recorded in
`.spec-artifacts/incidents/2026-09-16-evidence-that-could-not-fail.md`: an outcome clause
with no assertion reading it. T26's outcome names the table's columns; its evidence checks
`OnPush`, `trackBy`, the single `GET /symbols` call and the pane's fixed height. None of
those touches a cell's value, so a column of zeroes passes every check the task declares.

The frontend also has no test framework by design, and was built without the cold gate — see
ADR-005 — so the only check available was a person looking, which is what eventually happened.

### Fix

`session_volume: float` added to `Quote`, populated from `RingBuffer.session_volume()` — the
same method `/movers` ranks on, so the two surfaces cannot disagree. The contract was authored
into the spec's `## Response models` first, then the model, then the route.

The spec now records *why* it sits on `Quote` rather than `SymbolMatch`: session volume
changes every tick, and `/symbols` is the call the markets table makes once at load, so a
volume column sourced from there would never move.

**A regression test was added**, because the field is read by exactly one surface and would
otherwise be free to go missing again:

```python
def test_every_quote_carries_its_session_volume(client, state, capsys) -> None:
    for entry in body:
        expected = state.buffers[entry["symbol"]].session_volume()
        assert entry["session_volume"] == pytest.approx(expected)
        assert entry["session_volume"] > 0.0, f"{entry['symbol']} reports no volume"
```

The `> 0.0` clause is the point. Equality with the buffer alone would pass if both were zero.

### Verification

The contract change was caught by the existing field-set assertion before anything else ran —
`test_model_carries_exactly_the_stated_fields[Quote]` failed, which is what that test exists
for. Schema re-emitted, client regenerated, component bound to the real field.

```
310 passed
distinct volume values: [ '12.52M', '5.11M', '8.75M', '6.36M', '7.02M' ]
```

`docs/screenshots/02-markets.png` was re-captured after the fix.

### One thing worth recording about the diagnosis

After the fix the column still read `0`. The source was correct, the API was correct, the
build succeeded — and `ng serve` had not rebuilt since well before the edit. Its watcher had
silently missed the change and it was serving stale code. Restarting it resolved it.

Worth knowing because it wasted a cycle and would waste another: **a green build from a
long-running dev server is not evidence that the running page contains your change.**

---

## BUG-002 — The scenario dropdown does not reflect an already-active scenario on load

**Status:** open, deliberately
**Severity:** cosmetic, and unreachable during normal use
**Found:** same review; characterised by driving the page rather than by reading the image

### What is wrong

When the page loads while a scenario is already active on the server, the toolbar chip shows
the scenario correctly and the dropdown falls back to "Reset to normal".

Clicking works. It is only the load path that desyncs:

```
after CLICKING "Credit crunch":
  select shows : Credit crunch      chip shows : Credit crunch      ✓
after RELOADING the page:
  select shows : Reset to normal    chip shows : Credit crunch      ✗   (API: credit_crunch)
```

### Cause

`[value]` on a `<select>` does not drive selection in Angular. The binding needs `[selected]`
on the options, or a form directive. The fix is roughly three lines.

### Why it is not fixed

A presenter drives this control by clicking it, and clicking is correct. The defect requires
loading the page against a scenario someone else already activated — which is exactly what a
headless screenshot run does, and is why it appeared in the first capture.

It is recorded rather than fixed because the fix touches the control the entire demo is driven
from, and there is no automated check on this surface that would catch a regression in the
click path. Changing it carries more risk than the defect does.

### My first description of it was wrong

I initially reported this as *"the dropdown doesn't reflect the active scenario"*, from the
screenshot alone. That overstated it — the click path was never broken. The distinction
matters because the overstated version points at rewriting the control, and the accurate
version points at three lines on a path nobody walks during a demo.

---

## Note on how both were found

Neither came from a failing test. Both came from generating screenshots of the running
application and reading them against what the specification asserts.

That is the check the frontend has, by the decision in ADR-005, and it is worth being plain
that it is a weaker one: it found these two because they were visible, and it would not have
found a wrong number that looked plausible.
