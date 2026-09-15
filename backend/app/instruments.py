"""The instrument universe: the `Instrument` record and the loader that reads it.

The artefact that matters here is `data/instruments.json`. This module is small on
purpose: the universe is data, so a beta can be retuned, a name corrected or an
instrument's decimal places changed without touching Python. Nothing about the
universe is written into this file — `load_instruments()` opens the JSON on every
call rather than caching a module-level constant, so the file on disk is the only
source of truth for what the universe is.

The universe is 45 instruments: 40 equities spread across exactly seven sectors,
none of them holding fewer than four, plus the five macro drivers, one per factor.

Two properties of the data are load-bearing for surfaces built later and are
asserted where the data is made, in `tests/test_instruments.py`:

* **No sector below four.** The frontend's markets table groups by sector, and a
  sector holding one row renders as a header with nothing under it.
* **Opposing oil betas inside a sector.** A sector whose members all move together
  makes the table read as a sector model rather than a factor one. An oil shock has
  to lift a producer while it sinks an airline *inside the same market* — so
  Industrials holds CAT against DAL and LUV, Consumer Discretionary holds TSLA
  against CCL, and Energy holds the producers against VLO, a refiner for whom crude
  is an input cost.

Every instrument is denominated in the same currency and there is no FX rate
anywhere. The `currency` field exists so the UI has a symbol to render; it is
constant across the universe. `decimals` is carried on the instrument and never
inferred from the value, so a price does not gain or lose a decimal as it moves.
"""

import json
from dataclasses import dataclass
from pathlib import Path

#: The five factors, in factor order. Written out as literals rather than imported,
#: exactly as `app.buffer` writes them out, because this module depends on no other
#: module in the project. These identifier-style strings are the keys themselves —
#: of every instrument's beta map here, and of `Bar.contributions` at T25, which
#: rejects any other spelling — and are not the prose names (market, rates/duration,
#: oil, USD, credit spread) that describe the factors.
FACTORS: tuple[str, str, str, str, str] = (
    "market",
    "rates",
    "oil",
    "usd",
    "credit",
)

#: The only beta values the model admits. A beta is a coarse dial, not an estimate:
#: there is no historical data behind this universe and an intermediate value would
#: imply a precision nothing here has.
ALLOWED_BETAS: frozenset[float] = frozenset({-1.0, -0.5, 0.0, 0.5, 1.0})

#: The universe on disk, resolved relative to this module so the working directory
#: cannot change which file is read.
DATA_FILE = Path(__file__).resolve().parent / "data" / "instruments.json"


@dataclass(frozen=True, slots=True)
class Instrument:
    """One tradable instrument, or one macro driver, with its factor exposures.

    `factor` is `None` for the 40 equities and names the driven factor for each of
    the five macro drivers, which carry exposure 1.0 to their own factor and 0.0 to
    the other four — this is what `GET /macro` reports.
    """

    symbol: str
    name: str
    sector: str
    currency: str
    decimals: int
    factor: str | None
    start_price: float
    betas: dict[str, float]

    def __post_init__(self) -> None:
        if set(self.betas) != set(FACTORS):
            raise ValueError(
                f"{self.symbol}: betas must be keyed by exactly the five factors "
                f"{list(FACTORS)}; got {sorted(self.betas)}."
            )
        for factor, beta in self.betas.items():
            if beta not in ALLOWED_BETAS:
                raise ValueError(
                    f"{self.symbol}: beta to {factor!r} is {beta}, which is not one "
                    f"of {sorted(ALLOWED_BETAS)}."
                )
        if self.decimals < 0:
            raise ValueError(
                f"{self.symbol}: decimals is {self.decimals}; a price cannot have a "
                "negative number of decimal places."
            )
        if self.start_price <= 0.0:
            raise ValueError(
                f"{self.symbol}: start price is {self.start_price}; every price is "
                "strictly greater than zero at every tick."
            )
        if self.factor is not None:
            if self.factor not in FACTORS:
                raise ValueError(
                    f"{self.symbol}: {self.factor!r} is not one of the five factors "
                    f"{list(FACTORS)}."
                )
            expected = {one: (1.0 if one == self.factor else 0.0) for one in FACTORS}
            if self.betas != expected:
                raise ValueError(
                    f"{self.symbol} drives {self.factor!r}, so it carries exposure 1.0 "
                    f"to it and 0.0 to the other four; got {self.betas}."
                )
        # Held in factor order, whatever order the file wrote them in, so that a
        # surface iterating an instrument's betas gets market, rates, oil, usd,
        # credit — the order later tasks rank and display by.
        object.__setattr__(
            self, "betas", {factor: float(self.betas[factor]) for factor in FACTORS}
        )

    @property
    def is_macro_driver(self) -> bool:
        """True for the five macro drivers, false for the 40 equities."""
        return self.factor is not None


def load_instruments() -> dict[str, Instrument]:
    """Read the universe from `data/instruments.json`, keyed by symbol.

    The JSON is opened on every call — the universe is not embedded here and not
    cached — so an edit to the data file is the whole of an edit to the universe.
    Insertion order follows the file, which places the five macro drivers last and
    in factor order.
    """
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    universe: dict[str, Instrument] = {}
    for entry in raw["instruments"]:
        instrument = Instrument(
            symbol=entry["symbol"],
            name=entry["name"],
            sector=entry["sector"],
            currency=entry["currency"],
            decimals=entry["decimals"],
            factor=entry["factor"],
            start_price=entry["start_price"],
            # Passed through as the file wrote them, so a misspelled or missing
            # factor key is rejected rather than quietly dropped or defaulted.
            betas=dict(entry["betas"]),
        )
        if instrument.symbol in universe:
            raise ValueError(
                f"{instrument.symbol} appears twice in {DATA_FILE.name}; symbols key "
                "the universe and every route resolves through them."
            )
        universe[instrument.symbol] = instrument
    return universe
