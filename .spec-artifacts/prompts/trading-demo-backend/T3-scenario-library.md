---
name: scenario-library
description: Define the scenario library as JSON — per-factor shocks, drift, half-life, volatility multiplier and headlines — behind a typed id enum.
task: T3
model: claude-opus-5
---

# Objective

Define the scenario library as JSON with per-factor shock, drift and half-life plus a
scenario-level volatility multiplier and its headlines, and load it behind a typed id enum, so
that adding a scenario is a data edit and never a code change.

# Outcome

The loader returns 6 or 7 scenarios, including a baseline whose every shock and drift is zero
and an oil supply shock. Every scenario, baseline included, carries 2 or 3 headlines. Each
non-baseline scenario names at least two factors. The id enum's members equal the set of ids
present in the JSON.

- **Evidenced by:** `cd backend && uv run pytest tests/test_scenarios.py -v` — asserts the
  library size is 6 or 7, the baseline's shocks and drifts are all zero, that an oil supply
  shock is present by id, that every scenario's headline count is 2 or 3, that each
  non-baseline scenario names at least two factors, that the enum members and the JSON ids are
  the same set compared both ways, and that every scenario carries a per-factor shock, drift
  and half-life plus a scenario-level volatility multiplier. Those last four are declared by
  the Objective and read by nothing else in this task, so without asserting them a `Scenario`
  that omits them passes. Run before replying and paste the output.

# Task context

- The five factors are exactly: market, rates/duration, oil, USD, credit spread.
- **Baseline carries headlines like any other scenario.** The ticker shows the baseline's
  headlines while at baseline, so a baseline without them leaves the strip empty in the app's
  resting state — which is what an audience sees first.
- An oil supply shock is required by name because two later surfaces assume it: the movers
  review item and the markets table's sector reordering both demonstrate an oil spike.
- Half-life governs how a shock decays. A scenario with no half-life set is a persistent
  regime change rather than a decaying one; decide and state which your JSON means, and make
  the loader's handling of an absent value explicit rather than incidental.
- The enum exists so a route can reject an unknown scenario id with a 422 rather than a 500.

# Deliverables

- **CREATE** `backend/app/data/scenarios.json` — the library
- **CREATE** `backend/app/scenarios.py` — the types, the enum and the loader
- **Function(s):** `load_scenarios() -> dict[ScenarioId, Scenario]`
- **Evidence:** `backend/tests/test_scenarios.py`

# Instructions

1. CREATE `backend/app/data/scenarios.json`
2. CREATE `backend/app/scenarios.py`
3. ADD type `FactorShock`, `Scenario` in `backend/app/scenarios.py`
4. ADD type `ScenarioId` in `backend/app/scenarios.py`
5. ADD function `load_scenarios() -> dict[ScenarioId, Scenario]` in `backend/app/scenarios.py`
6. CREATE `backend/tests/test_scenarios.py`

# Constraints

- Adding a scenario must require editing JSON only. If your design needs a `.py` edit to
  register a new scenario, it is wrong — except for the enum, which is generated from or
  checked against the JSON rather than hand-maintained alongside it.
- Headlines are plain sentences a non-technical reader understands. No ticker symbols, no
  factor names, no numbers with more than one decimal.
- No price level is asserted in any test.
- If the enum cannot be kept in step with the JSON without hand-editing both, STOP and report
  the conflict rather than accepting a design that breaks the JSON-only rule.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted test output. Then the list of scenario ids and, for each, its
headline count.
