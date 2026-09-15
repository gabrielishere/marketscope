"""The universe's shape: the counts, the metadata, the betas and the macro rows.

Every expected value below is a literal taken from the Outcome and the spec's
Definitions — 40 equities, exactly 7 sectors, none below 4, 45 in all, the five
factor keys, the five permitted beta values — rather than read back off
`instruments.json`. A test that asks the data what it contains cannot fail when the
data is wrong, so the sector names, the per-sector counts and the opposing oil pairs
are all written out here by hand.

No price level is asserted anywhere in this file, per Constraints. `start_price` is
checked only for the property O3 states — strictly greater than zero — and never
against a figure, because the only source for such a figure is the file under test.

The opposing-oil-beta tests name the sectors and the instruments they found in their
own parameter ids, so the pasted run shows *which* sectors carry the disagreement. A
universe that satisfies "at least two sectors" by accident cannot pass them: they
demand Energy, Industrials and Consumer Discretionary by name, and they demand that
Technology — whose members all carry an oil beta of 0.0 — is not among them.
"""

import pytest

from app.instruments import ALLOWED_BETAS, DATA_FILE, FACTORS, Instrument, load_instruments

# ── The literals, taken from the Outcome and the spec's Definitions ─────────

#: The five factor keys, in factor order. Identifier-style: these are the keys, not
#: the prose names (market, rates/duration, oil, USD, credit spread). `Bar` rejects a
#: `contributions` dict keyed any other way, so a divergent spelling here fails at T25.
THE_FIVE_FACTORS = ["market", "rates", "oil", "usd", "credit"]

#: The only permitted beta values.
THE_FIVE_BETAS = {-1.0, -0.5, 0.0, 0.5, 1.0}

EQUITY_COUNT = 40
MACRO_COUNT = 5
TOTAL_COUNT = 45
SECTOR_COUNT = 7
MINIMUM_PER_SECTOR = 4

#: The seven equity sectors and the number of instruments each holds. Written out so
#: that a sector renamed, emptied or split fails here rather than passing on a count
#: the data recomputed for itself. 6 + 6 + 6 + 5 + 6 + 6 + 5 = 40.
SECTOR_SIZES = {
    "Technology": 6,
    "Financials": 6,
    "Energy": 6,
    "Health Care": 5,
    "Consumer Discretionary": 6,
    "Industrials": 6,
    "Utilities": 5,
}

#: The macro drivers, one per factor, in factor order.
MACRO_DRIVERS = [
    ("SPX", "market"),
    ("US10Y", "rates"),
    ("WTI", "oil"),
    ("DXY", "usd"),
    ("CDXHY", "credit"),
]

#: The sectors built to hold a pair whose oil betas disagree, with the pair itself.
#: An oil shock lifts the first and sinks the second, inside the same sector.
OPPOSING_OIL_PAIRS = [
    ("Energy", "XOM", "VLO"),
    ("Industrials", "CAT", "DAL"),
    ("Consumer Discretionary", "TSLA", "CCL"),
]

#: A sector with no oil disagreement at all: every member's oil beta is 0.0. The
#: detector must not report it, or it is reporting every sector.
SECTOR_WITH_NO_OIL_DISAGREEMENT = "Technology"


# ── Fixtures and helpers ───────────────────────────────────────────────────


@pytest.fixture
def universe() -> dict[str, Instrument]:
    return load_instruments()


def equities(universe: dict[str, Instrument]) -> list[Instrument]:
    return [one for one in universe.values() if one.factor is None]


def macro_drivers(universe: dict[str, Instrument]) -> list[Instrument]:
    return [one for one in universe.values() if one.factor is not None]


def sectors_with_opposing_oil_betas(universe: dict[str, Instrument]) -> set[str]:
    """Sectors holding both a positive and a negative oil beta among their equities."""
    found = set()
    for sector in {one.sector for one in equities(universe)}:
        oils = [
            one.betas["oil"] for one in equities(universe) if one.sector == sector
        ]
        if any(beta > 0.0 for beta in oils) and any(beta < 0.0 for beta in oils):
            found.add(sector)
    return found


def an_instrument(**overrides: object) -> Instrument:
    """One instrument built from keyword literals, for the rejection tests."""
    fields: dict = {
        "symbol": "TEST",
        "name": "Test Holdings plc",
        "sector": "Industrials",
        "currency": "USD",
        "decimals": 2,
        "factor": None,
        "start_price": 100.0,
        "betas": {"market": 1.0, "rates": 0.0, "oil": 0.5, "usd": -0.5, "credit": 0.0},
    }
    fields.update(overrides)
    return Instrument(**fields)


# ── The counts: 40 equities, 7 sectors, none below 4, 45 in all ────────────


def test_the_universe_holds_forty_five_instruments(universe) -> None:
    assert len(universe) == TOTAL_COUNT


def test_forty_of_them_are_equities(universe) -> None:
    assert len(equities(universe)) == EQUITY_COUNT


def test_five_of_them_are_macro_drivers(universe) -> None:
    assert len(macro_drivers(universe)) == MACRO_COUNT
    assert EQUITY_COUNT + MACRO_COUNT == TOTAL_COUNT


def test_the_universe_is_keyed_by_symbol(universe) -> None:
    assert all(symbol == one.symbol for symbol, one in universe.items())
    assert len({one.symbol for one in universe.values()}) == TOTAL_COUNT


def test_the_equities_span_exactly_seven_sectors(universe) -> None:
    assert {one.sector for one in equities(universe)} == set(SECTOR_SIZES)
    assert len({one.sector for one in equities(universe)}) == SECTOR_COUNT


def test_each_sector_holds_the_number_of_instruments_it_was_built_with(
    universe,
) -> None:
    held = {sector: 0 for sector in SECTOR_SIZES}
    for one in equities(universe):
        held[one.sector] += 1

    assert held == SECTOR_SIZES
    assert sum(SECTOR_SIZES.values()) == EQUITY_COUNT


@pytest.mark.parametrize("sector", sorted(SECTOR_SIZES))
def test_no_sector_falls_below_four(universe, sector: str) -> None:
    # Four is the floor, not a target: the markets table groups by sector and a
    # sector holding one row renders as a header with nothing under it. Three would
    # fail this; four passes.
    held = [one for one in equities(universe) if one.sector == sector]

    assert len(held) >= MINIMUM_PER_SECTOR
    assert len(held) > 3


def test_the_macro_drivers_are_not_one_of_the_seven_equity_sectors(universe) -> None:
    # Counting sectors over the whole universe would give eight and put the drivers
    # in the markets table; they have their own strip.
    assert all(one.sector not in SECTOR_SIZES for one in macro_drivers(universe))


# ── The metadata every instrument carries ──────────────────────────────────


def test_every_instrument_carries_a_name(universe) -> None:
    for one in universe.values():
        assert one.name
        assert one.name != one.symbol


def test_every_instrument_carries_a_sector(universe) -> None:
    for one in universe.values():
        assert one.sector


def test_every_instrument_carries_a_currency(universe) -> None:
    for one in universe.values():
        assert one.currency


def test_the_currency_is_constant_across_the_universe(universe) -> None:
    # There is no FX rate anywhere; the field exists so the UI has a symbol to render.
    assert {one.currency for one in universe.values()} == {"USD"}


def test_every_instrument_carries_a_decimal_places_value(universe) -> None:
    # Carried, never inferred from the value, so a price does not gain or lose a
    # decimal as it moves.
    for one in universe.values():
        assert isinstance(one.decimals, int)
        assert one.decimals >= 0


def test_decimal_places_are_not_all_the_same(universe) -> None:
    # A single decimals value everywhere would be indistinguishable from a constant
    # in the renderer, which is what carrying the field exists to avoid.
    assert len({one.decimals for one in universe.values()}) > 1


def test_every_start_price_is_strictly_positive(universe) -> None:
    # The only price property asserted here. No price level is asserted anywhere in
    # this file: the sole source for such a literal is the data under test.
    for one in universe.values():
        assert one.start_price > 0.0


# ── The betas: the five keys, the five permitted values ────────────────────


def test_every_instrument_is_keyed_by_exactly_the_five_factors(universe) -> None:
    for one in universe.values():
        assert list(one.betas) == THE_FIVE_FACTORS


def test_the_module_factor_keys_are_the_five_in_factor_order() -> None:
    assert list(FACTORS) == THE_FIVE_FACTORS


def test_every_beta_is_one_of_the_five_permitted_values(universe) -> None:
    for one in universe.values():
        for factor, beta in one.betas.items():
            assert beta in THE_FIVE_BETAS, f"{one.symbol} {factor} = {beta}"


def test_the_permitted_set_is_exactly_the_five(universe) -> None:
    assert set(ALLOWED_BETAS) == THE_FIVE_BETAS


def test_the_universe_uses_the_range_and_not_just_one_value(universe) -> None:
    # Every beta being 0.0 would satisfy the value-set assertion above and leave
    # every instrument inert under every scenario.
    used = {beta for one in universe.values() for beta in one.betas.values()}

    assert used == THE_FIVE_BETAS


@pytest.mark.parametrize("beta", sorted(THE_FIVE_BETAS))
def test_a_permitted_beta_is_accepted(beta: float) -> None:
    accepted = an_instrument(
        betas={"market": beta, "rates": 0.0, "oil": 0.0, "usd": 0.0, "credit": 0.0}
    )

    assert accepted.betas["market"] == beta


@pytest.mark.parametrize("beta", [-2.0, -1.5, -0.75, -0.25, 0.25, 0.75, 1.5, 2.0])
def test_an_intermediate_or_out_of_range_beta_is_rejected(beta: float) -> None:
    with pytest.raises(ValueError):
        an_instrument(
            betas={"market": beta, "rates": 0.0, "oil": 0.0, "usd": 0.0, "credit": 0.0}
        )


@pytest.mark.parametrize(
    ("betas", "case"),
    [
        ({"market": 1.0, "rates": 0.0, "oil": 0.0, "usd": 0.0}, "one factor missing"),
        (
            {
                "market": 1.0,
                "rates": 0.0,
                "oil": 0.0,
                "usd": 0.0,
                "credit": 0.0,
                "momentum": 0.5,
            },
            "a sixth key that is not a factor",
        ),
        (
            {
                "market": 1.0,
                "rates/duration": 0.0,
                "oil": 0.0,
                "USD": 0.0,
                "credit spread": 0.0,
            },
            "the prose names rather than the identifier-style keys",
        ),
        ({}, "no entries at all"),
    ],
    ids=["missing-factor", "extra-key", "prose-names", "empty"],
)
def test_a_beta_map_keyed_any_other_way_is_rejected(betas: dict, case: str) -> None:
    with pytest.raises(ValueError):
        an_instrument(betas=betas)


# ── The five macro drivers' exposure rows ──────────────────────────────────


def test_the_macro_drivers_are_one_per_factor_in_factor_order(universe) -> None:
    assert [one.factor for one in macro_drivers(universe)] == THE_FIVE_FACTORS


def test_the_macro_drivers_are_the_five_named_ones(universe) -> None:
    assert [
        (one.symbol, one.factor) for one in macro_drivers(universe)
    ] == MACRO_DRIVERS


@pytest.mark.parametrize(("symbol", "factor"), MACRO_DRIVERS)
def test_a_macro_driver_carries_unit_exposure_to_its_own_factor_and_zero_to_the_rest(
    universe, symbol: str, factor: str
) -> None:
    driver = universe[symbol]

    assert driver.factor == factor
    assert driver.betas[factor] == 1.0
    for other in THE_FIVE_FACTORS:
        if other != factor:
            assert driver.betas[other] == 0.0, f"{symbol} {other}"


def test_no_equity_claims_to_drive_a_factor(universe) -> None:
    assert all(one.factor is None for one in equities(universe))


# ── The opposing oil betas, by name ────────────────────────────────────────


@pytest.mark.parametrize(
    ("sector", "rises", "falls"),
    OPPOSING_OIL_PAIRS,
    ids=[
        f"{sector.replace(' ', '-')}-{rises}-vs-{falls}"
        for sector, rises, falls in OPPOSING_OIL_PAIRS
    ],
)
def test_a_named_sector_holds_a_pair_whose_oil_betas_have_opposite_signs(
    universe, sector: str, rises: str, falls: str
) -> None:
    # The demo's whole point: an oil shock lifts a producer while it sinks an
    # airline inside the same market.
    up, down = universe[rises], universe[falls]

    assert up.sector == sector
    assert down.sector == sector
    assert up.betas["oil"] > 0.0
    assert down.betas["oil"] < 0.0


def test_at_least_two_sectors_hold_an_opposing_oil_pair(universe) -> None:
    assert len(sectors_with_opposing_oil_betas(universe)) >= 2


def test_the_sectors_holding_an_opposing_oil_pair_are_the_three_built_to(
    universe,
) -> None:
    # Named, not counted: a universe that reaches two by accident fails here.
    assert sectors_with_opposing_oil_betas(universe) == {
        "Energy",
        "Industrials",
        "Consumer Discretionary",
    }


def test_a_sector_whose_members_share_an_oil_beta_is_not_reported(universe) -> None:
    # The other side of the boundary. Every Technology member's oil beta is 0.0, so
    # the sector holds no disagreement and must not be counted as one.
    held = [one for one in equities(universe) if one.sector == SECTOR_WITH_NO_OIL_DISAGREEMENT]

    assert all(one.betas["oil"] == 0.0 for one in held)
    assert SECTOR_WITH_NO_OIL_DISAGREEMENT not in sectors_with_opposing_oil_betas(
        universe
    )


# ── The loader reads the file, and reads it at call time ───────────────────


def test_the_universe_lives_in_the_json_file() -> None:
    assert DATA_FILE.name == "instruments.json"
    assert DATA_FILE.is_file()


def test_two_calls_return_equal_universes(universe) -> None:
    again = load_instruments()

    assert list(again) == list(universe)
    assert all(again[symbol] == universe[symbol] for symbol in universe)


def test_the_loader_reads_the_file_rather_than_handing_back_a_cached_universe() -> None:
    # Emptying one caller's universe must not empty the next caller's. A module-level
    # constant handed back by reference would fail this.
    first = load_instruments()
    first.clear()

    assert len(load_instruments()) == TOTAL_COUNT


def test_mutating_one_instruments_betas_does_not_reach_a_later_load() -> None:
    first = load_instruments()
    first["DAL"].betas["oil"] = 1.0

    assert load_instruments()["DAL"].betas["oil"] < 0.0
