# ADR-001 — Factor keys are identifier-style, and are not the prose names

**Date:** 2026-09-16
**Status:** accepted
**Affects:** `trading-demo-backend`, `trading-demo-frontend`

## Context

The Constraints of both specs name the five factors in prose: *market, rates/duration,
oil, USD, credit spread*. Nothing said how those factors are spelled when used as **keys**.

They are keys in five places: `Bar.contributions`, an instrument's beta map in
`instruments.json`, a scenario's per-factor shocks in `scenarios.json`, `FACTOR_SENTENCES`,
and the `factor` field on `FactorContribution` and `MacroDriver`.

T4's implementor needed them to key `contributions`, was forbidden to import anything into
`app/buffer.py`, and so reproduced the prose character for character —
`("market", "rates/duration", "oil", "USD", "credit spread")` — and made `Bar` reject any
other spelling at runtime. It escalated rather than assuming, and the orchestrator held
before dispatching T2 rather than running it against a key set that existed in committed
code and in no document (run record `004-T4.json`).

The last two of those five places are on the wire. The `factor` field reaches the client
through `ng-openapi-gen` as a generated TypeScript value.

## Decision

We will use `market`, `rates`, `oil`, `usd`, `credit`, in that order, as the factor keys
everywhere. The prose names describe the factors and are not the keys; the specs say so
where they name them, and the key set is settled in both specs' Definitions under **Factor
keys**. Display labels — Market, Rates, Oil, USD, Credit — are a third thing again, and
belong to the client.

## Alternatives

- **The prose spelling, as T4 committed it** — `rates/duration` carries a slash and
  `credit spread` a space, and both reach generated TypeScript. A slash in a property name
  is not merely ugly; it forces bracket access wherever the client touches it, and it
  cannot appear unescaped in a path or query parameter if a later surface ever wants one.
  `USD` uppercase among four lowercase siblings is inconsistent for no reason.
- **Letting T2 pick, since it writes the first data file** — the keys are read by five
  tasks and by the whole frontend spec. Resolving a term that many tasks share inside one
  of them is the failure the Definitions section exists to prevent.
- **Separate wire keys and internal keys, with a mapping** — two vocabularies and a
  translation layer, for a five-element set that nothing else needs.

## Consequences

- The keys are safe in JSON, in TypeScript, in a URL and in a Python identifier, so no
  surface has to escape or translate them.
- Display labels must be supplied by the client, since `usd` is not something to show a
  user. `macro-strip.component.ts` and `impact-panel.component.ts` each carry the map.
- T4 had to be re-run: its committed `FACTORS` held the prose tuple and `Bar` enforced it,
  so `instruments.json` would have failed against it (run records `005-T4.json` refused,
  `006-T4.json` passed).
- A sixth factor is a data edit plus one line in each spec's Definitions, not a rename
  across five files.
