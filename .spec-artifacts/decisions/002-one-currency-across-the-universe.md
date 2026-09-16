# ADR-002 — One currency across the universe, and no FX rate

**Date:** 2026-09-15
**Status:** accepted
**Affects:** `trading-demo-backend`, `trading-demo-frontend`

## Context

The specification originally carried multi-currency reporting as an outcome: *"The
portfolio response reports value, return and today's change as one set per currency, and no
field anywhere sums across currencies."* Instruments carried a native currency, there was
no FX rate anywhere, and the portfolio therefore had to report per-currency totals because
there was no honest way to combine them.

That rule was doing real work — a portfolio that adds dollars to sterling is wrong in a way
that looks fine on screen — but it was doing it for a demo whose subject is a factor model,
shown to a non-technical audience, where nobody will ask what currency anything is in.

The shape reached further than the outcome suggested: a `CurrencyTotals` type, a
per-currency grouping in the portfolio route, one summary block per currency in the
frontend, and a currency-labelled amount field on the trade ticket.

## Decision

We will denominate every instrument in the same currency and hold no FX rate. The portfolio
reports **one set of totals** — value, cash, return and today's change. Instruments keep a
`currency` field so the client has a symbol to render, and it is constant across the
universe.

## Alternatives

- **Keep multi-currency** — correct, and the source of a per-currency grouping in one
  backend route, a per-currency block in the summary, a currency label on the ticket, and
  an outcome asserting nothing sums across. All of it invisible to the audience.
- **Drop the `currency` field entirely** — the client then has no symbol to render and
  would hard-code one, which is the same constant in a worse place.
- **Keep the field and allow several currencies without an FX rate** — the portfolio could
  then only report per-currency totals again, which is the alternative above wearing a
  different hat.

## Consequences

- The portfolio surface is one block of figures rather than a repeated group, which is what
  the approved mockup shows.
- **The instrument universe cannot mix exchanges.** Adding an LSE-listed name alongside the
  NYSE ones would silently produce a portfolio total that adds two currencies — precisely
  the defect the original outcome prevented. The constraint in both specs is what stops it.
- `CurrencyTotals` became `PortfolioTotals`; T7, T15 and the trade ticket all simplified.
- Restoring multi-currency later means reinstating the outcome, the grouping and the
  per-currency block — not a large change, but not a free one either.
