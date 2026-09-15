---
name: instrument-universe
description: Define 45 instruments as JSON across 7 sectors with factor betas, and load them behind a typed record.
task: T2
model: claude-opus-5
---

# Objective

Define the instrument universe as JSON and load it at startup, so that scenarios have
something to act on and betas can be tuned without touching code. The data file is the
artefact that matters here; the loader is small.

# Outcome

The loader returns 40 equities across exactly 7 sectors with at least 4 in every sector, plus
the 5 macro drivers, for 45 instruments total. Every instrument carries a name, a sector, a
currency, a decimal-places value and a beta for each of the five factors. Every beta is one of
{-1.0, -0.5, 0.0, 0.5, 1.0}. Each macro driver has exposure 1.0 to its own factor and 0.0 to
the other four. At least two sectors contain a pair of instruments whose oil betas have
opposite signs.

- **Evidenced by:** `cd backend && uv run pytest tests/test_instruments.py -v` — asserts the
  counts (40 equities, 7 sectors, no sector below 4, 45 total), that every instrument has a
  name, sector, currency and decimal-places value, the beta value set, the five macro drivers'
  exposure rows, and that at least two sectors contain a pair with opposite-signed oil betas.
  The opposing-beta assertion must name the two sectors it found, so a universe that happens
  to satisfy it by accident is distinguishable from one built to. Run before replying and
  paste the output.

# Task context

- Anything below restated from the spec reproduces `## Definitions` and `## Response models`
  in `.spec-artifacts/specs/trading-demo-backend.md`. **If this prompt and the spec
  disagree, the spec governs**, and the disagreement is a defect to report rather than one
  to resolve. Read that file if a term here is thinner than the work needs.
- The five factors, by key, are exactly `market`, `rates`, `oil`, `usd`, `credit`, in that
  order — see **Factor keys** in the spec's Definitions. Use the key strings verbatim. Factor
  order is that order, and later tasks rank and display by it.
- The per-sector minimum of 4 and the opposing-beta pair are load-bearing for the frontend
  spec's markets table, which groups by sector. A sector holding one row renders as a header
  with nothing under it. A sector whose members all move together makes the table read as a
  sector model rather than a factor one — the demo's whole point is that an oil shock lifts a
  producer while it sinks an airline **inside the same market**, so at least one sector must
  contain that disagreement.
- Every instrument is denominated in the same currency. The currency field exists so the UI
  has a symbol to render; it is constant across the universe.
- Decimal places are carried on the instrument and never inferred from the value, so a price
  does not gain or lose a decimal as it moves.

# Deliverables

- **CREATE** `backend/app/data/instruments.json` — the universe
- **CREATE** `backend/app/instruments.py` — the record type and the loader
- **Function(s):** `load_instruments() -> dict[str, Instrument]` — keyed by symbol
- **Evidence:** `backend/tests/test_instruments.py`

# Instructions

1. CREATE `backend/app/data/instruments.json`
2. CREATE `backend/app/instruments.py`
3. ADD type `Instrument` in `backend/app/instruments.py`
4. ADD function `load_instruments() -> dict[str, Instrument]` in `backend/app/instruments.py`
5. CREATE `backend/tests/test_instruments.py`

# Constraints

- Betas are drawn only from {-1.0, -0.5, 0.0, 0.5, 1.0}. No intermediate value.
- Each instrument's beta map is keyed by the five factor keys exactly. `Bar` rejects a
  `contributions` dict keyed any other way, so a divergent spelling here fails at T25.
- Use real-looking symbols, names and sectors. The demo is shown to a non-technical audience
  and `SYM1`/`Sector A` reads as a toy.
- No price level is written into this file as an assertion in any test. Starting prices may
  appear in the JSON; a test must not assert one.
- The loader reads the JSON at call time. Do not embed the universe in Python.
- If the constraint set cannot be satisfied — 40 equities, 7 sectors, minimum 4 each, two
  sectors with opposing oil betas — STOP and report which constraint conflicts, rather than
  relaxing one silently.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output, and separately the two sector names the opposing-beta
assertion found.
