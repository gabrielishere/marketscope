# ADR-008 — Activating a scenario applies it before the endpoint responds

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-backend`, `trading-demo-frontend`

## Context

Selecting a scenario felt slow, and the operator noticed it in the running application rather
than in any test.

Measured rather than guessed. From the click, every request completed in **54ms**:

```
   9ms  POST /scenario
  18ms  ← 200
  19ms  GET /quotes, /movers, /impact, /scenario    ← refreshNow() firing correctly
  54ms  ← all four back
```

The first *visible* price change was at **1920ms**. The refresh worked exactly as designed
and returned stale prices.

The cause is a race the design could not see. `Engine.activate()` stamps `activated_at` as
the index of the **next bar to be written**; the shock does not exist until that bar exists,
and the engine writes one once a second on its own clock. So the endpoint returned success
while nothing had moved, the client refreshed 19ms later onto unchanged prices, and the
change surfaced only on the next scheduled poll. Confirmed server-side:

```
before POST:       120.2527
+0ms (POST done):  120.2527    ← activated, no bar written
+400ms:            128.6280    ← the tick lands, +7%
```

Worst case is about 3.5 seconds: up to 1s for the engine tick, plus up to 2.5s for the poll.

**O15 was satisfied throughout.** It requires that selecting a scenario "issues the POST and
refreshes quotes without waiting out the poll interval", and that is precisely what happened.
The outcome asserted the refresh, and what the audience needs is that the *data has changed*
by the time the refresh lands. An outcome can be met exactly and still miss the point.

## Decision

We will have `POST /scenario` and `DELETE /scenario` **advance the simulation one tick before
responding**, so the endpoint reports a state that is already true rather than one that is
about to become true.

## Alternatives

- **Delay `refreshNow()` by roughly a tick** — guesses at the race rather than removing it.
  It would be tuned against one machine's timing and would break whenever the tick interval
  changed, silently, by going back to showing stale prices.
- **Shorten the poll interval** — makes every surface busier to fix one interaction, and
  cannot fix it anyway: the refresh would still land before the engine had written the bar.
- **Leave it, and explain the lag** — defensible for a system where a scenario is a rare
  operation. Rejected because this is the demo's central interaction, performed live in front
  of an audience, and a control that appears to do nothing for two seconds reads as broken
  regardless of what it is doing underneath.
- **Apply the shock to current prices without writing a bar** — would make the change instant
  and break O5. Every contribution is stored on the bar whose price it produced; a price move
  with no bar behind it has no attribution, and the reconciliation would no longer hold by
  construction.

## Consequences

- **1920ms to 44ms**, measured the same way. The price moves inside the POST, so the refresh
  at 22ms fetches a market that has already changed.
- **An activation advances the market by one extra tick**, out of band from the once-a-second
  loop. Harmless here — the clock is synthetic and a tick is a minute of market time — but it
  means the tick count is no longer purely a function of elapsed time.
- **O6 still holds and its test is now stricter.** The outcome says bars *before*
  `activated_at` are byte-identical; the test had asserted that the entire buffer was
  unchanged, which passed only because the handler used to do nothing. It now compares the
  prior slice and separately asserts exactly one bar was appended per instrument, which is
  closer to what the outcome claims than the original was.
- **`DELETE` ticks too.** Returning to baseline unwinds the outgoing shock (ADR-003), and
  that unwind lands in a bar like any other, so without the same treatment "Reset to normal"
  would have had the identical lag.

## On how this was applied

Edited directly into the built application, not driven through a spec, a prompt or the
orchestrator. The same departure ADR-006 records for the artefacts, now for the code: the
build is finished, the defect was found by using the thing, and re-running a task to change
four lines would have cost more than it protected.

What that forfeits is the cold gate's reading of the change. In mitigation the regression is
covered by a test that fails without the fix — `test_activation_moves_prices_before_it_responds`
asserts every instrument repriced within the POST — and the suite caught the O6 interaction
by itself, which is how the outcome's own test came to be tightened.
