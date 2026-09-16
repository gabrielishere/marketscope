"""The scenario library: the `FactorShock` and `Scenario` records, the id enum and
the loader that reads them.

The artefact that matters here is `data/scenarios.json`. Adding a scenario is an edit
to that file and nothing else: `ScenarioId` is **generated from** the ids the file
holds rather than hand-maintained beside it, so a new entry brings its own enum
member with it. Nothing about any particular scenario is written into this module —
no id literal drives the loading, and `load_scenarios()` opens the JSON on every call
rather than handing back a cached library, so the file on disk is the only source of
truth for what the library is.

**What a scenario is.** Per factor: a `shock` — the jump in that factor's level at the
moment the scenario is activated — a `drift` — a per-tick addition to that factor's
log return for as long as the scenario runs — and a `half_life`. On the scenario
itself: a `vol_multiplier`, which scales every instrument's idiosyncratic volatility
while the scenario is active, and two or three `headlines`, which the ticker displays.

**What an absent half-life means.** A half-life is written in **ticks** — one tick is
one minute of market time — and a shock decays by `0.5 ** (ticks_since / half_life)`.
Writing `null` means **the shock does not decay at all**: the scenario is a persistent
regime change rather than a passing event, and `FactorShock.decay` returns 1.0 for it
at every tick. `rate_hike_surprise` and `dollar_surge` each carry one such factor —
a central bank's move and a currency's repricing do not fade on their own — while
every other factor in the library decays.

That reading is only honest if `null` is *written*. A **missing** `half_life` key is
therefore rejected by the loader rather than read as `None`: an author who forgot the
field and an author who meant a permanent regime change would otherwise be
indistinguishable, and the second is the rarer intent. The same goes for `shock` and
`drift`, which carry no defaults either — a scenario that omits them is a malformed
scenario, not a quiet baseline.

`ScenarioId` exists so the boundary can be typed: the scenario routes declare it and
FastAPI rejects an unknown id with a 422 rather than letting a `KeyError` become a
500. It is a `StrEnum`, so its members hash and compare as their id strings and the
library `load_scenarios()` returns can be indexed by either.
"""

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

#: The five factors, in factor order. Written out as literals rather than imported,
#: exactly as `app.instruments` and `app.buffer` write them out, because this module
#: depends on no other module in the project. These identifier-style strings are the
#: keys themselves — of every scenario's per-factor map here, of an instrument's beta
#: map, and of `Bar.contributions` — and are not the prose names (market,
#: rates/duration, oil, USD, credit spread) that describe the factors.
FACTORS: tuple[str, str, str, str, str] = (
    "market",
    "rates",
    "oil",
    "usd",
    "credit",
)

#: The library on disk, resolved relative to this module so the working directory
#: cannot change which file is read.
DATA_FILE = Path(__file__).resolve().parent / "data" / "scenarios.json"

#: The id of the scenario the application rests at. Naming it here is not registering
#: it — it is already in the JSON like any other — but T5 starts the state at it and
#: `DELETE /scenario` returns to it, and both need a name for the resting state.
BASELINE_ID = "baseline"

#: Every scenario carries two or three headlines, baseline included: the ticker shows
#: the active scenario's, so a scenario without them leaves the strip empty.
MIN_HEADLINES = 2
MAX_HEADLINES = 3


@dataclass(frozen=True, slots=True)
class FactorShock:
    """One factor's behaviour under one scenario.

    `shock` is the jump in the factor's level at activation, in log space. `drift` is
    added to the factor's log return every tick the scenario is active. `half_life` is
    in ticks, or `None` for a shock that never decays — see the module docstring.
    None of the three has a default: a scenario that omits one is malformed.
    """

    shock: float
    drift: float
    half_life: float | None

    def __post_init__(self) -> None:
        if self.half_life is not None and self.half_life <= 0.0:
            raise ValueError(
                f"half_life is {self.half_life}; it is a number of ticks and must be "
                "strictly positive. Write null for a shock that never decays."
            )
        object.__setattr__(self, "shock", float(self.shock))
        object.__setattr__(self, "drift", float(self.drift))
        if self.half_life is not None:
            object.__setattr__(self, "half_life", float(self.half_life))

    @property
    def is_persistent(self) -> bool:
        """True when the shock never decays — a regime change, not a passing event."""
        return self.half_life is None

    @property
    def is_named(self) -> bool:
        """True when the scenario says something about this factor.

        A factor with a zero shock *and* a zero drift is not moved by the scenario at
        all; every other factor is one the scenario names.
        """
        return self.shock != 0.0 or self.drift != 0.0

    def decay(self, ticks_since_activation: int) -> float:
        """The fraction of `shock` still standing `ticks_since_activation` ticks on.

        `0.5 ** (ticks / half_life)` — so 1.0 at activation and 0.5 after one
        half-life — or a flat 1.0 for a persistent shock, which is what an absent
        half-life means.
        """
        if ticks_since_activation < 0:
            raise ValueError(
                f"ticks_since_activation is {ticks_since_activation}; a scenario has "
                "no effect before it is activated."
            )
        if self.half_life is None:
            return 1.0
        return 0.5 ** (ticks_since_activation / self.half_life)


@dataclass(frozen=True, slots=True)
class Scenario:
    """One world event: what it does to each factor, and what the ticker says about it."""

    id: str
    name: str
    description: str
    vol_multiplier: float
    headlines: tuple[str, ...]
    factors: dict[str, FactorShock]

    def __post_init__(self) -> None:
        if set(self.factors) != set(FACTORS):
            raise ValueError(
                f"{self.id}: factors must be keyed by exactly the five factors "
                f"{list(FACTORS)}; got {sorted(self.factors)}."
            )
        if self.vol_multiplier <= 0.0:
            raise ValueError(
                f"{self.id}: vol_multiplier is {self.vol_multiplier}; it scales "
                "idiosyncratic volatility and must be strictly positive."
            )
        headlines = tuple(self.headlines)
        if not MIN_HEADLINES <= len(headlines) <= MAX_HEADLINES:
            raise ValueError(
                f"{self.id}: carries {len(headlines)} headlines; every scenario, "
                f"baseline included, carries {MIN_HEADLINES} or {MAX_HEADLINES}."
            )
        object.__setattr__(self, "headlines", headlines)
        object.__setattr__(self, "vol_multiplier", float(self.vol_multiplier))
        # Held in factor order, whatever order the file wrote them in, so that a
        # surface iterating a scenario's factors gets market, rates, oil, usd, credit.
        object.__setattr__(
            self, "factors", {factor: self.factors[factor] for factor in FACTORS}
        )

    @property
    def is_baseline(self) -> bool:
        """True when the scenario moves no factor: every shock and every drift zero."""
        return not any(one.is_named for one in self.factors.values())

    @property
    def named_factors(self) -> tuple[str, ...]:
        """The factors this scenario moves, in factor order."""
        return tuple(
            factor for factor, one in self.factors.items() if one.is_named
        )


def _read_entries() -> list[dict]:
    """The raw scenario entries as the file wrote them, in file order."""
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return list(raw["scenarios"])


def _required(entry: dict, key: str, where: str) -> object:
    """One field, present or an error naming it — never a silent default.

    `half_life` reaches here too: `null` is a value and means a persistent shock, but
    a missing key is an omission and is rejected, because the two would otherwise be
    the same thing written two ways.
    """
    if key not in entry:
        raise ValueError(
            f"{where}: {key!r} is missing. Every field is written out, including a "
            "null half_life for a shock that never decays."
        )
    return entry[key]


def _factor_shock_from_entry(entry: dict, where: str) -> FactorShock:
    """One `FactorShock` from one factor's raw object."""
    return FactorShock(
        shock=_required(entry, "shock", where),  # type: ignore[arg-type]
        drift=_required(entry, "drift", where),  # type: ignore[arg-type]
        half_life=_required(entry, "half_life", where),  # type: ignore[arg-type]
    )


def _scenario_from_entry(entry: dict) -> Scenario:
    """One `Scenario` from one raw entry, with every field required explicitly."""
    scenario_id = str(_required(entry, "id", "a scenario entry"))
    raw_factors = _required(entry, "factors", scenario_id)
    if not isinstance(raw_factors, dict):
        raise ValueError(f"{scenario_id}: 'factors' must be an object keyed by factor.")
    return Scenario(
        id=scenario_id,
        name=str(_required(entry, "name", scenario_id)),
        description=str(_required(entry, "description", scenario_id)),
        vol_multiplier=_required(entry, "vol_multiplier", scenario_id),  # type: ignore[arg-type]
        headlines=tuple(_required(entry, "headlines", scenario_id)),  # type: ignore[call-overload]
        factors={
            factor: _factor_shock_from_entry(raw, f"{scenario_id}.{factor}")
            for factor, raw in raw_factors.items()
        },
    )


def _member_name(scenario_id: str) -> str:
    """The enum member name for an id — the id upper-cased, and nothing else.

    The value stays the id verbatim, so `ScenarioId('oil_supply_shock')` resolves and
    a member compares equal to the string the JSON and the wire both carry.
    """
    if not scenario_id.isidentifier() or scenario_id != scenario_id.lower():
        raise ValueError(
            f"{scenario_id!r} is not a usable scenario id: an id is a lower-case "
            "identifier, because it becomes an enum member and reaches the client as "
            "a generated TypeScript value."
        )
    return scenario_id.upper()


def _scenario_ids() -> list[str]:
    """Every id in the file, in file order, rejecting a duplicate."""
    ids = [str(_required(entry, "id", "a scenario entry")) for entry in _read_entries()]
    duplicates = {one for one in ids if ids.count(one) > 1}
    if duplicates:
        raise ValueError(
            f"{sorted(duplicates)} appear more than once in {DATA_FILE.name}; ids key "
            "the library and the scenario routes validate against them."
        )
    return ids


#: The scenario ids as a type. **Generated from the JSON, never hand-written**: the
#: members are exactly the ids `data/scenarios.json` holds, in file order, so adding a
#: scenario to the file adds its member and this module needs no edit. The scenario
#: routes declare this type, which is how an unknown id becomes a 422 rather than a
#: 500. As a `StrEnum` its members hash and compare as their id strings, so the
#: library can be indexed by a member or by the bare id.
ScenarioId = StrEnum(
    "ScenarioId",
    {_member_name(one): one for one in _scenario_ids()},
    module=__name__,
)
ScenarioId.__doc__ = (
    "The ids in data/scenarios.json, generated from the file at import."
)


def load_scenarios() -> dict[ScenarioId, Scenario]:
    """Read the library from `data/scenarios.json`, keyed by `ScenarioId`.

    The JSON is opened on every call — the library is not embedded in this module and
    not cached — so an edit to the data file is the whole of an edit to the library.
    Insertion order follows the file, which places the baseline first.
    """
    library: dict[ScenarioId, Scenario] = {}
    for entry in _read_entries():
        scenario = _scenario_from_entry(entry)
        library[ScenarioId(scenario.id)] = scenario
    if BASELINE_ID not in library:
        raise ValueError(
            f"{DATA_FILE.name} holds no {BASELINE_ID!r} scenario; the application "
            "rests at it and DELETE /scenario returns to it."
        )
    if not library[ScenarioId(BASELINE_ID)].is_baseline:
        raise ValueError(
            f"{BASELINE_ID!r} moves a factor; the resting state shocks nothing, so "
            "every one of its shocks and drifts is zero."
        )
    return library
