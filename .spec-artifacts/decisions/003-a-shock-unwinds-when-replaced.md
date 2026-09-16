# ADR-003 — A shock unwinds when the scenario that raised it is replaced

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-backend`

## Context

A scenario shocks a factor's **level**, and each tick carries the *change* in that level as
a return: the whole shock on the activation tick, and the opposite-signed decay of it
afterwards. The engine computed that change against the active scenario's own previous
level.

That is correct while one scenario runs and wrong the moment another replaces it. On a
switch, `activated_at` resets and the incoming scenario's level is applied from zero — but
the outgoing scenario's level, already in the prices, is never decayed by anyone, because
the engine only looks at the scenario currently active.

Observed live. XOM at 133.95 at baseline; 143.24 under the oil supply shock, +6.93%;
144.81 after switching to `risk_rally`, **+8.11% against baseline** — the oil move still
entirely present, with a rally's move stacked on top of it. Flipping through three
scenarios in a demo ratchets prices in one direction and makes every day-change figure
meaningless.

## Decision

We will track the shock level **currently applied to the prices**, per factor, and have
each tick move that level toward whatever the active scenario asks for, carrying the
difference as the return. Activation, decay, a switch between scenarios and a return to
baseline then become the same operation, and none of them can strand a level nobody is
decaying.

## Alternatives

- **Leave it: a shock permanently reprices the asset** — defensible as economics, and it is
  what the engine did. But a presenter flipping between scenarios is the demo's core
  interaction, and after three flips the prices carry three stacked shocks that no headline
  explains. The model would be arguable and the demo would be broken.
- **Forbid switching: require a reset to baseline between scenarios** — pushes the problem
  onto the presenter, who now has a two-click ritual and a demo that breaks when they
  forget. It also does not help, because returning to baseline had the same defect: the
  outgoing level was not unwound then either.
- **Unwind on `activate()` and `deactivate()` rather than per tick** — a discontinuity
  applied outside the tick loop, so the unwind would not appear in any bar's
  `contributions` and the reconciliation to 1e-6 would break.

## Consequences

- Switching scenarios behaves as an audience expects: the old event's effect comes out as
  the new one goes in. Verified live at 116.99 baseline, +6.64% under the oil shock,
  +1.16% after switching to the rally, +0.33% back at baseline.
- The unwind flows through `contributions`, so O5's reconciliation still holds by
  construction — the price is still derived from the numbers that are stored.
- A shock is now a *temporary* repricing in every case, including a persistent one with a
  null half-life: persistent means it does not decay while active, not that it survives its
  own scenario being replaced.
- `Engine` carries one more piece of state, `_applied_shock`, which must be reasoned about
  alongside `activated_at` when the engine is next changed.
