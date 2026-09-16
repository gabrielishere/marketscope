"""The library's shape: the counts, the baseline, the headlines, the enum and the
four fields the Objective declares and nothing else in this task reads.

Every expected value below is a literal taken from the Outcome and the spec's
Definitions — six or seven scenarios, two or three headlines, at least two named
factors, the five factor keys — rather than read back off `scenarios.json`. A test
that asks the data what it contains cannot fail when the data is wrong, so the bounds,
the baseline id and the oil supply shock's id are written out here by hand.

`shock`, `drift`, `half_life` and `vol_multiplier` are asserted twice over: once on
the loaded `Scenario`, and once on the raw JSON entry. The first alone would pass
against a loader that invented a default for a field the file never wrote, which is
exactly how a scenario silently becomes something other than its author meant.

No price level is asserted anywhere in this file, per Constraints.
"""

import json
import re
from dataclasses import fields

import pytest

from app.scenarios import (
    BASELINE_ID,
    DATA_FILE,
    FACTORS,
    MAX_HEADLINES,
    MIN_HEADLINES,
    FactorShock,
    Scenario,
    ScenarioId,
    _scenario_from_entry,
    load_scenarios,
)

# ── The literals, taken from the Outcome and the spec's Definitions ─────────

#: The five factor keys, in factor order. Identifier-style: these are the keys, not
#: the prose names (market, rates/duration, oil, USD, credit spread).
THE_FIVE_FACTORS = ["market", "rates", "oil", "usd", "credit"]

#: "The loader returns 6 or 7 scenarios."
MIN_LIBRARY_SIZE = 6
MAX_LIBRARY_SIZE = 7

#: "Every scenario, baseline included, carries 2 or 3 headlines."
MIN_HEADLINES_REQUIRED = 2
MAX_HEADLINES_REQUIRED = 3

#: "Each non-baseline scenario names at least two factors."
MINIMUM_NAMED_FACTORS = 2

#: The baseline, and the oil supply shock two later surfaces assume by name: the
#: movers review item and the markets table's sector reordering both demonstrate an
#: oil spike, so this id is required rather than merely likely.
BASELINE = "baseline"
OIL_SUPPLY_SHOCK = "oil_supply_shock"

#: Model vocabulary a headline never uses, matched as whole words — a headline naming
#: a factor reads as the simulation talking about itself rather than as news a
#: non-technical reader understands. Whole words, because "factory orders" is news and
#: "the oil factor" is not.
MODEL_VOCABULARY = re.compile(
    r"\b(markets?|rates?|oils?|usd|credits?|factors?|betas?)\b", re.IGNORECASE
)

#: A ticker-shaped token: two or more capitals in a row. Headlines carry no symbols.
TICKER_SHAPED = re.compile(r"[A-Z]{2,}")

#: A number written to more than one decimal place.
TOO_MANY_DECIMALS = re.compile(r"\d+\.\d{2,}")

#: Collected once, at import, only so that each scenario gets its own parametrised
#: test line in the pasted run. Every assertion is against the literals above.
LIBRARY_IDS = list(load_scenarios())


# ── Fixtures and helpers ───────────────────────────────────────────────────


@pytest.fixture
def library() -> dict:
    return load_scenarios()


@pytest.fixture
def entries() -> list[dict]:
    """The raw JSON entries, read here rather than through the loader."""
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))["scenarios"]


def zero_factors() -> dict[str, FactorShock]:
    return {
        factor: FactorShock(shock=0.0, drift=0.0, half_life=None)
        for factor in THE_FIVE_FACTORS
    }


def a_scenario(**overrides: object) -> Scenario:
    """One scenario built from keyword literals, for the boundary tests."""
    built: dict = {
        "id": "test_event",
        "name": "Test event",
        "description": "A scenario built by hand in a test.",
        "vol_multiplier": 1.0,
        "headlines": ("Something happened.", "Something else happened."),
        "factors": zero_factors(),
    }
    built.update(overrides)
    return Scenario(**built)


def an_entry(**overrides: object) -> dict:
    """One raw JSON-shaped entry, for the loader's required-field tests."""
    built: dict = {
        "id": "test_event",
        "name": "Test event",
        "description": "A scenario built by hand in a test.",
        "vol_multiplier": 1.0,
        "headlines": ["Something happened.", "Something else happened."],
        "factors": {
            factor: {"shock": 0.0, "drift": 0.0, "half_life": None}
            for factor in THE_FIVE_FACTORS
        },
    }
    built.update(overrides)
    return built


def non_baseline_ids() -> list[str]:
    return [one for one in LIBRARY_IDS if one != BASELINE]


# ── The size: 6 or 7 ───────────────────────────────────────────────────────


def test_the_library_holds_six_or_seven_scenarios(library) -> None:
    # Both sides of the bound: five would fail the first, eight the second.
    assert len(library) >= MIN_LIBRARY_SIZE
    assert len(library) <= MAX_LIBRARY_SIZE


def test_the_library_is_keyed_by_scenario_id(library) -> None:
    assert all(key == one.id for key, one in library.items())
    assert len({one.id for one in library.values()}) == len(library)


def test_a_scenario_is_reachable_by_its_bare_id_string(library) -> None:
    # The enum is a StrEnum, so a member hashes and compares as its id. A route that
    # has validated a raw string does not have to coerce it to read the library.
    assert library[BASELINE].id == BASELINE
    assert library[OIL_SUPPLY_SHOCK].id == OIL_SUPPLY_SHOCK


# ── The baseline: every shock and every drift zero ─────────────────────────


def test_the_library_holds_a_baseline(library) -> None:
    assert BASELINE in library
    assert BASELINE_ID == BASELINE


@pytest.mark.parametrize("factor", THE_FIVE_FACTORS)
def test_the_baselines_shock_and_drift_are_zero_for_every_factor(
    library, factor: str
) -> None:
    at_rest = library[BASELINE].factors[factor]

    assert at_rest.shock == 0.0
    assert at_rest.drift == 0.0


def test_the_baseline_names_no_factor_at_all(library) -> None:
    assert library[BASELINE].named_factors == ()
    assert library[BASELINE].is_baseline


def test_exactly_one_scenario_in_the_library_moves_nothing(library) -> None:
    # The other side of the baseline test: a library where every scenario zeroed its
    # factors would pass the assertions above and move no price under any event.
    at_rest = [one.id for one in library.values() if one.is_baseline]

    assert at_rest == [BASELINE]


def test_the_baselines_shocks_are_zero_in_the_file_too(entries) -> None:
    baseline = next(one for one in entries if one["id"] == BASELINE)

    for factor in THE_FIVE_FACTORS:
        assert baseline["factors"][factor]["shock"] == 0.0
        assert baseline["factors"][factor]["drift"] == 0.0


# ── The oil supply shock, by id ────────────────────────────────────────────


def test_an_oil_supply_shock_is_present_by_id(library) -> None:
    assert OIL_SUPPLY_SHOCK in library
    assert ScenarioId(OIL_SUPPLY_SHOCK) in library
    assert library[OIL_SUPPLY_SHOCK].id == OIL_SUPPLY_SHOCK


def test_the_oil_supply_shock_actually_spikes_crude(library) -> None:
    # Two later surfaces demonstrate an oil spike. A scenario carrying the id and a
    # zero — or negative — oil shock would satisfy the id test and demonstrate nothing.
    shock = library[OIL_SUPPLY_SHOCK].factors["oil"]

    assert shock.shock > 0.0
    assert shock.is_named
    assert not library[OIL_SUPPLY_SHOCK].is_baseline


# ── The headlines: two or three, on every scenario ─────────────────────────


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_scenario_carries_two_or_three_headlines(
    library, scenario_id: str
) -> None:
    # Baseline included: the ticker shows the baseline's headlines at rest, and a
    # baseline without them leaves the strip empty in what an audience sees first.
    headlines = library[scenario_id].headlines

    assert len(headlines) >= MIN_HEADLINES_REQUIRED
    assert len(headlines) <= MAX_HEADLINES_REQUIRED


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_the_headline_count_matches_the_file(library, entries, scenario_id) -> None:
    written = next(one for one in entries if one["id"] == scenario_id)

    assert len(library[scenario_id].headlines) == len(written["headlines"])


def test_the_modules_headline_bounds_are_the_two_the_outcome_states() -> None:
    assert MIN_HEADLINES == MIN_HEADLINES_REQUIRED
    assert MAX_HEADLINES == MAX_HEADLINES_REQUIRED


@pytest.mark.parametrize("count", [MIN_HEADLINES_REQUIRED, MAX_HEADLINES_REQUIRED])
def test_two_and_three_headlines_are_accepted(count: int) -> None:
    accepted = a_scenario(headlines=tuple(f"Headline {n}." for n in range(count)))

    assert len(accepted.headlines) == count


@pytest.mark.parametrize("count", [0, 1, 4, 5])
def test_a_scenario_with_fewer_than_two_or_more_than_three_is_rejected(
    count: int,
) -> None:
    # The far side of both bounds: one headline is as wrong as four.
    with pytest.raises(ValueError):
        a_scenario(headlines=tuple(f"Headline {n}." for n in range(count)))


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_headline_is_a_plain_sentence(library, scenario_id: str) -> None:
    for headline in library[scenario_id].headlines:
        assert headline.strip() == headline
        assert headline.endswith(".")
        assert headline[0].isupper()
        assert len(headline.split()) >= 5


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_no_headline_carries_a_ticker_symbol_or_model_vocabulary(
    library, scenario_id: str
) -> None:
    # A headline a non-technical reader understands: no symbols, no factor names, and
    # no number written to more than one decimal place.
    for headline in library[scenario_id].headlines:
        assert not TICKER_SHAPED.search(headline), headline
        assert not TOO_MANY_DECIMALS.search(headline), headline
        named = MODEL_VOCABULARY.search(headline)
        assert named is None, f"{headline!r} carries {named.group(0)!r}"


@pytest.mark.parametrize(
    "written",
    [
        "The oil factor rose sharply this morning.",
        "Credit spreads widened against a rising dollar.",
        "Shares in XOM led the advance.",
        "The index slipped 0.125 per cent.",
    ],
    ids=["factor-name", "model-vocabulary", "ticker-symbol", "three-decimals"],
)
def test_the_detectors_catch_a_headline_that_breaks_the_rule(written: str) -> None:
    # The other side of the test above. A detector that matched nothing would pass
    # every headline in the library, including one reading "WTI beta 0.75".
    assert (
        TICKER_SHAPED.search(written)
        or TOO_MANY_DECIMALS.search(written)
        or MODEL_VOCABULARY.search(written)
    )


def test_the_detectors_let_ordinary_news_through() -> None:
    # And a detector that matched everything would be no test either.
    written = "Factory orders fell 3 per cent in a single quarter."

    assert not TICKER_SHAPED.search(written)
    assert not TOO_MANY_DECIMALS.search(written)
    assert not MODEL_VOCABULARY.search(written)


# ── Named factors: at least two, on every non-baseline scenario ────────────


@pytest.mark.parametrize("scenario_id", non_baseline_ids())
def test_every_non_baseline_scenario_names_at_least_two_factors(
    library, scenario_id: str
) -> None:
    named = library[scenario_id].named_factors

    assert len(named) >= MINIMUM_NAMED_FACTORS, f"{scenario_id} names {named}"
    assert set(named) <= set(THE_FIVE_FACTORS)


def test_the_library_holds_at_least_five_non_baseline_scenarios(library) -> None:
    # The test above vacuously passes over an empty parameter set. Six scenarios with
    # one baseline is five events; this is what makes the count non-vacuous.
    assert len([one for one in library.values() if not one.is_baseline]) >= 5


def test_a_factor_moved_by_a_shock_alone_is_named() -> None:
    factors = zero_factors()
    factors["oil"] = FactorShock(shock=0.05, drift=0.0, half_life=None)

    assert a_scenario(factors=factors).named_factors == ("oil",)


def test_a_factor_moved_by_a_drift_alone_is_named() -> None:
    factors = zero_factors()
    factors["usd"] = FactorShock(shock=0.0, drift=0.0001, half_life=None)

    assert a_scenario(factors=factors).named_factors == ("usd",)


def test_a_factor_with_a_zero_shock_and_a_zero_drift_is_not_named() -> None:
    # The other side: a counter that named every factor would make the two-factor
    # requirement unfalsifiable.
    assert a_scenario(factors=zero_factors()).named_factors == ()


def test_named_factors_come_back_in_factor_order() -> None:
    factors = zero_factors()
    factors["credit"] = FactorShock(shock=0.02, drift=0.0, half_life=None)
    factors["market"] = FactorShock(shock=-0.02, drift=0.0, half_life=None)

    assert a_scenario(factors=factors).named_factors == ("market", "credit")


# ── The enum: its members and the JSON ids, compared both ways ─────────────


def test_every_id_in_the_file_has_an_enum_member(entries) -> None:
    for entry in entries:
        assert ScenarioId(entry["id"]).value == entry["id"]


def test_every_enum_member_is_an_id_in_the_file(entries) -> None:
    written = [entry["id"] for entry in entries]

    for member in ScenarioId:
        assert member.value in written


def test_the_enum_members_and_the_file_ids_are_the_same_set(entries) -> None:
    written = {entry["id"] for entry in entries}

    assert {member.value for member in ScenarioId} == written
    assert len(list(ScenarioId)) == len(entries)


def test_the_libraries_keys_are_the_enum_members(library) -> None:
    assert set(library) == set(ScenarioId)


def test_an_unknown_scenario_id_is_rejected(library) -> None:
    # This is what a route turns into a 422 rather than a 500: an id nobody wrote
    # does not resolve to a member, so it never reaches a library lookup.
    assert "banana_shortage" not in {member.value for member in ScenarioId}
    with pytest.raises(ValueError):
        ScenarioId("banana_shortage")


def test_a_member_compares_and_hashes_as_its_id_string() -> None:
    assert ScenarioId(BASELINE) == BASELINE
    assert hash(ScenarioId(BASELINE)) == hash(BASELINE)


# ── The four fields the Objective declares and nothing else here reads ─────


def test_a_factor_shock_carries_exactly_shock_drift_and_half_life() -> None:
    assert {one.name for one in fields(FactorShock)} == {"shock", "drift", "half_life"}


def test_a_scenario_carries_a_scenario_level_volatility_multiplier() -> None:
    assert {one.name for one in fields(Scenario)} == {
        "id",
        "name",
        "description",
        "vol_multiplier",
        "headlines",
        "factors",
    }


@pytest.mark.parametrize("missing", ["shock", "drift", "half_life"])
def test_a_factor_shock_cannot_be_built_without_one_of_the_three(missing: str) -> None:
    # No defaults: a scenario that omits a field is malformed, not quietly zeroed.
    written = {"shock": 0.01, "drift": 0.0001, "half_life": 300.0}
    del written[missing]

    with pytest.raises(TypeError):
        FactorShock(**written)


def test_a_scenario_cannot_be_built_without_a_volatility_multiplier() -> None:
    with pytest.raises(TypeError):
        Scenario(
            id="test_event",
            name="Test event",
            description="A scenario built by hand in a test.",
            headlines=("Something happened.", "Something else happened."),
            factors=zero_factors(),
        )


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_scenario_carries_all_five_factors_in_factor_order(
    library, scenario_id: str
) -> None:
    assert list(library[scenario_id].factors) == THE_FIVE_FACTORS


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_factor_carries_a_shock_a_drift_and_a_half_life(
    library, scenario_id: str
) -> None:
    for factor in THE_FIVE_FACTORS:
        one = library[scenario_id].factors[factor]

        assert isinstance(one.shock, float)
        assert isinstance(one.drift, float)
        assert one.half_life is None or isinstance(one.half_life, float)
        assert one.half_life is None or one.half_life > 0.0


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_scenario_carries_a_positive_volatility_multiplier(
    library, scenario_id: str
) -> None:
    multiplier = library[scenario_id].vol_multiplier

    assert isinstance(multiplier, float)
    assert multiplier > 0.0


def test_the_volatility_multipliers_are_not_all_the_same(library) -> None:
    # A field carrying 1.0 everywhere is indistinguishable from no field at all.
    assert len({one.vol_multiplier for one in library.values()}) > 1


def test_the_file_itself_writes_all_four_fields_on_every_scenario(entries) -> None:
    # Asserted on the raw entries as well as the loaded objects: a loader inventing a
    # default for a field the file never wrote would pass every test above.
    for entry in entries:
        assert "vol_multiplier" in entry, entry["id"]
        for factor in THE_FIVE_FACTORS:
            written = entry["factors"][factor]
            assert set(written) == {"shock", "drift", "half_life"}, entry["id"]


def test_the_modules_factor_keys_are_the_five_in_factor_order() -> None:
    assert list(FACTORS) == THE_FIVE_FACTORS


@pytest.mark.parametrize(
    ("factors", "case"),
    [
        ({"market": 0, "rates": 0, "oil": 0, "usd": 0}, "one factor missing"),
        (
            {"market": 0, "rates": 0, "oil": 0, "usd": 0, "credit": 0, "momentum": 0},
            "a sixth key that is not a factor",
        ),
        (
            {"market": 0, "rates/duration": 0, "oil": 0, "USD": 0, "credit spread": 0},
            "the prose names rather than the identifier-style keys",
        ),
    ],
    ids=["missing-factor", "extra-key", "prose-names"],
)
def test_a_factor_map_keyed_any_other_way_is_rejected(factors: dict, case: str) -> None:
    built = {
        key: FactorShock(shock=0.0, drift=0.0, half_life=None) for key in factors
    }

    with pytest.raises(ValueError):
        a_scenario(factors=built)


# ── What an absent half-life means ─────────────────────────────────────────


def test_a_null_half_life_is_a_persistent_regime_change() -> None:
    persistent = FactorShock(shock=0.03, drift=0.0001, half_life=None)

    assert persistent.is_persistent
    assert persistent.decay(0) == 1.0
    assert persistent.decay(390) == 1.0
    assert persistent.decay(5000) == 1.0


def test_a_half_life_halves_the_shock_over_its_own_length() -> None:
    # The literals are the definition of a half-life, not a reading off the code.
    decaying = FactorShock(shock=0.07, drift=0.0, half_life=240.0)

    assert not decaying.is_persistent
    assert decaying.decay(0) == 1.0
    assert decaying.decay(240) == pytest.approx(0.5)
    assert decaying.decay(480) == pytest.approx(0.25)
    assert decaying.decay(120) == pytest.approx(0.5**0.5)


def test_a_missing_half_life_key_is_rejected_rather_than_read_as_persistent() -> None:
    # `null` written out means persistent; a key nobody wrote means an omission. The
    # two would otherwise be the same scenario, and only one of them was intended.
    entry = an_entry()
    del entry["factors"]["oil"]["half_life"]

    with pytest.raises(ValueError):
        _scenario_from_entry(entry)


@pytest.mark.parametrize("missing", ["shock", "drift"])
def test_a_missing_shock_or_drift_is_rejected_rather_than_read_as_zero(
    missing: str,
) -> None:
    entry = an_entry()
    del entry["factors"]["oil"][missing]

    with pytest.raises(ValueError):
        _scenario_from_entry(entry)


def test_an_entry_writing_every_field_loads() -> None:
    # The other side of the four tests above: the same entry, nothing removed, loads.
    loaded = _scenario_from_entry(an_entry())

    assert loaded.factors["oil"].half_life is None
    assert loaded.vol_multiplier == 1.0


@pytest.mark.parametrize("half_life", [0.0, -1.0, -240.0])
def test_a_non_positive_half_life_is_rejected(half_life: float) -> None:
    with pytest.raises(ValueError):
        FactorShock(shock=0.05, drift=0.0, half_life=half_life)


@pytest.mark.parametrize("half_life", [0.5, 1.0, 240.0])
def test_a_positive_half_life_is_accepted(half_life: float) -> None:
    assert FactorShock(shock=0.05, drift=0.0, half_life=half_life).half_life == half_life


def test_the_library_holds_both_a_persistent_and_a_decaying_shock(library) -> None:
    # Both readings are exercised by the data, so neither branch is dead.
    events = [one for one in library.values() if not one.is_baseline]
    persistent = [
        (one.id, factor)
        for one in events
        for factor, shock in one.factors.items()
        if shock.is_persistent and shock.is_named
    ]
    decaying = [
        (one.id, factor)
        for one in events
        for factor, shock in one.factors.items()
        if not shock.is_persistent and shock.is_named
    ]

    assert persistent, "no scenario carries a persistent regime change"
    assert decaying, "no scenario carries a decaying shock"


# ── The metadata the scenario list and the dropdown read ───────────────────


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_scenario_carries_a_name_and_a_description(
    library, scenario_id: str
) -> None:
    one = library[scenario_id]

    assert one.name
    assert one.name != one.id
    assert one.description
    assert one.description != one.name


@pytest.mark.parametrize("scenario_id", LIBRARY_IDS)
def test_every_id_is_a_lower_case_identifier(scenario_id: str) -> None:
    # It becomes an enum member and reaches the client as a generated TypeScript
    # value, so a space or a slash in an id would travel.
    assert scenario_id.isidentifier()
    assert scenario_id == scenario_id.lower()


# ── The loader reads the file, and reads it at call time ───────────────────


def test_the_library_lives_in_the_json_file() -> None:
    assert DATA_FILE.name == "scenarios.json"
    assert DATA_FILE.is_file()


def test_two_calls_return_equal_libraries(library) -> None:
    again = load_scenarios()

    assert list(again) == list(library)
    assert all(again[key] == library[key] for key in library)


def test_the_loader_reads_the_file_rather_than_handing_back_a_cached_library() -> None:
    # Emptying one caller's library must not empty the next caller's. A module-level
    # constant handed back by reference would fail this.
    first = load_scenarios()
    first.clear()

    assert len(load_scenarios()) >= MIN_LIBRARY_SIZE


def test_mutating_one_scenarios_factors_does_not_reach_a_later_load() -> None:
    first = load_scenarios()
    first[OIL_SUPPLY_SHOCK].factors.clear()

    assert list(load_scenarios()[OIL_SUPPLY_SHOCK].factors) == THE_FIVE_FACTORS
