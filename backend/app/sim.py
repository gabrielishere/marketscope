"""The tick engine: the factor model, the multiplicative price update and the
per-factor attribution stored on every bar.

One tick is one second of wall time and represents one minute of market time. This
module knows nothing about wall time: `tick()` advances the simulation by exactly one
minute of market time and appends exactly one `Bar` per instrument. The loop that
calls it once a second lives in `app.state`, so the engine is testable at whatever
speed a test wants to run it.

**The model.** Each tick draws one log return per factor,

    f = noise + drift + shock_delta

where `noise` is a Gaussian draw at that factor's per-minute volatility, `drift` is the
active scenario's per-tick addition for that factor, and `shock_delta` is the change in
the factor's shocked *level* since the previous tick — the full shock on the tick the
scenario is activated, and the decay of that shock thereafter. A scenario therefore
jumps a factor and then fades it, rather than jumping it once a tick forever.

Each instrument's log return is then

    r = Σ (beta_k · f_k) + σ · vol_multiplier · ε

and its price is **multiplied** by `exp(r)`. The multiplicative form is what keeps
prices strictly positive: `exp` of any finite number is strictly positive, so a price
that starts positive stays positive whatever the factors do. Nothing here clamps,
floors or takes `max(0, ...)` of a price — positivity is a consequence of the update,
not a repair applied after it.

**The attribution.** `Bar.contributions` holds `beta_k · f_k` per factor and
`Bar.residual` holds `σ · vol_multiplier · ε`. They are not recovered later from the
price, they are written at the tick, and the price is derived from them rather than the
other way round:

    log_return = sum(contributions.values()) + residual
    close      = open * exp(log_return)

so `sum(contributions.values()) + residual` reconciles with `log(close / previous_close)`
to the precision of one `exp`/`log` round trip — some 1e-19 on a return of 1e-3, far
inside the 1e-6 the outcome requires. T10 sums these stored numbers over a window and
never recomputes the model.

**`close` is not rounded.** `Instrument.decimals` is how a price is *displayed*;
rounding the stored close to two decimals would put an error of up to 5e-3 into every
log return and break the reconciliation above. Rounding happens at the edge, if at all.

**Reproducibility.** The engine is constructed with a seed and owns a single
`random.Random`. Two engines built with the same seed and ticked the same number of
times under the same scenario hold the same prices, so a rehearsal and the demo look
the same. The instruments are iterated in universe order on every tick, so the draws
land in the same places.
"""

import random
from math import exp

from app.buffer import FACTORS, Bar, RingBuffer
from app.instruments import Instrument, load_instruments
from app.scenarios import BASELINE_ID, Scenario, ScenarioId, load_scenarios

#: Per-tick — that is, per minute of market time — standard deviation of each factor's
#: log return, in factor order. A trading session is 390 ticks, so a figure of 0.0005
#: here is roughly a 1% standard deviation over a session. Oil is the most volatile of
#: the five and the dollar the least, which is what makes an oil shock read as an oil
#: shock on the macro strip.
FACTOR_VOLATILITY: dict[str, float] = {
    "market": 0.00050,
    "rates": 0.00060,
    "oil": 0.00090,
    "usd": 0.00035,
    "credit": 0.00055,
}

#: Per-tick standard deviation of an equity's idiosyncratic return — the part no factor
#: explains, stored as `Bar.residual`. Scaled by the active scenario's `vol_multiplier`,
#: which is the whole of what that multiplier does: it does not scale the factors.
IDIOSYNCRATIC_VOLATILITY = 0.00060

#: A macro driver carries no idiosyncratic term. It is not a company, it is the factor's
#: own index — exposure 1.0 to its factor and 0.0 to the other four — so a residual on it
#: would be a move in the factor that the factor itself did not make. Its stored residual
#: is therefore exactly 0.0, and its log return is exactly its own factor's return.
MACRO_DRIVER_VOLATILITY = 0.0

#: Synthetic per-tick volume. Each instrument is given a base rate at construction, drawn
#: once from the engine's own PRNG so that it is reproducible and costs the universe file
#: no extra field; each tick multiplies it by a jitter and by a term that grows with the
#: size of the move, so that a shock lifts turnover and `/movers`' most-active list is not
#: a constant ranking.
BASE_VOLUME_RANGE: tuple[float, float] = (20_000.0, 140_000.0)
VOLUME_JITTER_RANGE: tuple[float, float] = (0.60, 1.40)
VOLUME_MOVE_SENSITIVITY = 60.0

#: The high and low of a one-minute bar sit outside its open and close by a fraction of
#: a per-tick move. A wick is cosmetic — no figure in the contract is computed from it —
#: and it is always a fraction strictly below 1.0 of a positive price, so the low of a
#: positive bar is positive.
MAX_WICK_FRACTION = 0.00045


def baseline_scenario() -> Scenario:
    """The resting scenario, read from the library on disk.

    The engine rests here when no scenario is active, and `deactivate()` returns to it.
    """
    return load_scenarios()[ScenarioId(BASELINE_ID)]


class Engine:
    """The simulation: the universe, its prices, its history and the active scenario.

    Construct with a seed. `instruments` and `scenario` default to the universe and the
    baseline on disk, so a caller that wants the real thing passes neither, and a test
    that wants a particular scenario passes one.
    """

    def __init__(
        self,
        seed: int,
        instruments: dict[str, Instrument] | None = None,
        scenario: Scenario | None = None,
    ) -> None:
        self.seed = seed
        self.instruments: dict[str, Instrument] = (
            load_instruments() if instruments is None else dict(instruments)
        )
        self.baseline: Scenario = baseline_scenario()
        #: The scenario driving the factors, and the tick index it was activated at.
        #: `activated_at` is None while the engine rests at baseline; T9 stamps it
        #: through `activate()` and clears it through `deactivate()`.
        self.scenario: Scenario = self.baseline if scenario is None else scenario
        self.activated_at: int | None = None if scenario is None else 0
        #: The tick index the next appended bar will carry. The first bar is tick 0,
        #: which is what makes session start reachable on the first session.
        self.tick_index = 0
        #: The shock level currently baked into the prices, per factor. A tick moves this
        #: toward the active scenario's level and carries the difference as a return, so
        #: activation, decay, a switch between scenarios and a return to baseline are all
        #: the same operation.
        self._applied_shock: dict[str, float] = {factor: 0.0 for factor in FACTORS}
        self._random = random.Random(seed)
        self.prices: dict[str, float] = {
            symbol: instrument.start_price
            for symbol, instrument in self.instruments.items()
        }
        self.buffers: dict[str, RingBuffer] = {
            symbol: RingBuffer() for symbol in self.instruments
        }
        # Drawn before any tick, so the scenario a run is given cannot change them and
        # two engines on the same seed agree on them.
        self._base_volume: dict[str, float] = {
            symbol: self._random.uniform(*BASE_VOLUME_RANGE)
            for symbol in self.instruments
        }

    def activate(self, scenario: Scenario) -> None:
        """Make `scenario` the active one from the next tick onwards.

        The activation tick is the index of the next bar to be written, so every bar
        already in the buffers is untouched by the activation — bars are appended and
        never revisited — and the first bar written after it carries the full shock.
        """
        self.scenario = scenario
        self.activated_at = self.tick_index

    def deactivate(self) -> None:
        """Return to baseline. The bars written under the scenario stay as they are."""
        self.scenario = self.baseline
        self.activated_at = None

    def tick(self) -> None:
        """Advance the simulation one tick and append exactly one `Bar` per instrument.

        This is the whole of what a tick does. No timing, no sleeping, no scheduling and
        no eviction bookkeeping — the buffer caps itself and the loop lives in T5.
        """
        factor_returns = self._factor_returns()
        tick_index = self.tick_index
        for symbol, instrument in self.instruments.items():
            contributions = {
                factor: instrument.betas[factor] * factor_returns[factor]
                for factor in FACTORS
            }
            residual = self._draw_residual(instrument)
            # The stored attribution *is* the return: the price is derived from these
            # numbers, so they reconcile with it by construction rather than by
            # agreement between two separate calculations.
            log_return = sum(contributions.values()) + residual
            open_price = self.prices[symbol]
            close_price = open_price * exp(log_return)
            high, low = self._wicks(open_price, close_price)
            self.prices[symbol] = close_price
            self.buffers[symbol].append(
                Bar(
                    t=tick_index,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close_price,
                    volume=self._volume(symbol, log_return),
                    contributions=contributions,
                    residual=residual,
                )
            )
        self.tick_index = tick_index + 1

    def _factor_returns(self) -> dict[str, float]:
        """This tick's log return for each of the five factors, in factor order."""
        returns: dict[str, float] = {}
        for factor in FACTORS:
            shock = self.scenario.factors[factor]
            noise = self._random.gauss(0.0, FACTOR_VOLATILITY[factor])
            returns[factor] = noise + shock.drift + self._shock_delta(factor)
        return returns

    def _shock_delta(self, factor: str) -> float:
        """The change in a factor's shocked level between the last tick and this one.

        A shock is a jump in the factor's *level*, so what a tick's return carries is
        the difference between the level the factor should be at now and the level
        already in the prices: the whole shock on the activation tick, and the
        (opposite-signed) decay of it on every tick after. A persistent shock — one
        written with a null half-life — decays by nothing, so its delta is zero on every
        tick but the first.

        **The comparison is against what is applied, not against the active scenario's
        own previous level.** Those differ whenever the scenario changes, and taking the
        second reading leaves the outgoing scenario's level permanently baked into the
        prices: switch from an oil shock to a rally and the oil move is never unwound, so
        flipping between scenarios in a demo ratchets prices upward and makes every day
        change meaningless. Tracking the applied level means a switch unwinds what it
        replaces, and `deactivate()` unwinds the whole of it.
        """
        applied = self._applied_shock[factor]
        if self.activated_at is None:
            target = 0.0
        else:
            shock = self.scenario.factors[factor]
            elapsed = self.tick_index - self.activated_at
            target = shock.shock * shock.decay(elapsed) if elapsed >= 0 else applied
        self._applied_shock[factor] = target
        return target - applied

    def _draw_residual(self, instrument: Instrument) -> float:
        """The idiosyncratic part of one instrument's return on this tick.

        `σ · vol_multiplier · ε` — the scenario's multiplier scales this term and no
        other. Exactly 0.0 for a macro driver, which is its factor's index and has no
        idiosyncratic life of its own.
        """
        if instrument.is_macro_driver:
            return MACRO_DRIVER_VOLATILITY
        sigma = IDIOSYNCRATIC_VOLATILITY * self.scenario.vol_multiplier
        return self._random.gauss(0.0, sigma)

    def _wicks(self, open_price: float, close_price: float) -> tuple[float, float]:
        """A high at or above both ends of the bar and a low at or below both."""
        high = max(open_price, close_price) * (
            1.0 + self._random.uniform(0.0, MAX_WICK_FRACTION)
        )
        low = min(open_price, close_price) * (
            1.0 - self._random.uniform(0.0, MAX_WICK_FRACTION)
        )
        return high, low

    def _volume(self, symbol: str, log_return: float) -> float:
        """One tick's synthetic volume: a base rate, jittered and lifted by the move."""
        jitter = self._random.uniform(*VOLUME_JITTER_RANGE)
        excitement = 1.0 + VOLUME_MOVE_SENSITIVITY * abs(log_return)
        return self._base_volume[symbol] * jitter * excitement
