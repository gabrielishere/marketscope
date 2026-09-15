"""The Pydantic response models every route returns.

These models are the contract. T11 emits them as the OpenAPI schema and the frontend
generates its client from that emission, so a field added later is a contract change.

Every instrument is denominated in the same currency and there is no FX rate anywhere,
so ``PortfolioTotals`` is one set of figures rather than one per currency.

Nullable fields are declared without a default. They are therefore *required* and
always present in the payload, with ``null`` as a permitted value — the generated
client sees a key that is always there rather than one that may be absent.
"""

from pydantic import BaseModel, Field

# ── Market ──────────────────────────────────────────────────────────────────


class Quote(BaseModel):
    """One entry of the polled quote set: `GET /quotes?symbols=`."""

    symbol: str = Field(description="The instrument's ticker symbol.")
    last: float = Field(description="Latest close from the ring buffer.")
    day_change_pct: float = Field(
        description="(close_latest / close_at_session_start - 1) * 100."
    )
    sparkline: list[float] = Field(
        description=(
            "Recent closes, oldest first and the latest last, for the row sparkline. "
            "Prices, not returns; drawn on its own scale."
        )
    )


class Candle(BaseModel):
    """One aggregated bar of the chart series: `GET /candles/{symbol}?tf=`."""

    t: int = Field(description="Tick index of the bar's first constituent tick.")
    open: float
    high: float
    low: float
    close: float
    volume: float


class SymbolMatch(BaseModel):
    """One entry of the symbol list: `GET /symbols?q=`.

    With `q` omitted or empty this carries the static metadata the markets table
    loads once at load rather than on every poll.
    """

    symbol: str
    name: str
    sector: str
    currency: str = Field(
        description="Constant across the universe; the UI has a symbol to render."
    )
    decimals: int = Field(
        description="Fixed decimal places for this instrument's price, never inferred."
    )


# ── Portfolio ───────────────────────────────────────────────────────────────


class Position(BaseModel):
    """One paper holding: an entry of `GET /portfolio`."""

    symbol: str
    quantity: float = Field(description="Position size is a float, never an integer.")
    avg_entry: float = Field(description="Average entry price.")
    unrealised_pnl: float = Field(
        description="Unrealised profit and loss in the single currency."
    )


class PortfolioTotals(BaseModel):
    """One set of figures — there is no FX rate, so there is nothing to sum across."""

    value: float = Field(description="Total portfolio value.")
    cash: float = Field(description="Uninvested cash balance.")
    total_return: float = Field(description="Total return in currency.")
    total_return_pct: float = Field(description="Total return as a percentage.")
    day_change: float = Field(description="Today's change in currency.")
    day_change_pct: float = Field(
        description="Today's change as a percentage, per the day change % definition."
    )


class PortfolioResponse(BaseModel):
    """`GET /portfolio`."""

    positions: list[Position]
    totals: PortfolioTotals


# ── Movers and macro ────────────────────────────────────────────────────────


class Mover(BaseModel):
    """One ranked row of `GET /movers`."""

    symbol: str
    last: float
    day_change_pct: float
    session_volume: float = Field(
        description="Sum of volume from session start to the latest bar."
    )


class MoversResponse(BaseModel):
    """`GET /movers`. The API's ordering is the contract; the client re-sorts nothing."""

    gainers: list[Mover] = Field(description="Descending by day change %.")
    losers: list[Mover] = Field(description="Ascending by day change %.")
    most_active: list[Mover] = Field(description="Descending by session volume.")


class MacroDriver(BaseModel):
    """One tile of `GET /macro` — one instrument per factor, in factor order."""

    symbol: str
    name: str
    factor: str = Field(description="The factor this driver carries unit exposure to.")
    last: float
    day_change_pct: float


# ── Scenarios ───────────────────────────────────────────────────────────────


class ScenarioSummary(BaseModel):
    """One entry of the library: `GET /scenarios`."""

    id: str = Field(description="The scenario id, matching the ScenarioId enum's values.")
    name: str
    description: str


class ActiveScenario(BaseModel):
    """`GET /scenario` — the active scenario, its headlines and its activation tick."""

    id: str
    name: str
    headlines: list[str] = Field(description="Two or three canned headlines.")
    activated_at: int | None = Field(
        description=(
            "Tick index the active scenario was activated at; null at baseline. "
            "Always present."
        )
    )


# ── Impact and attribution ──────────────────────────────────────────────────


class FactorContribution(BaseModel):
    """One factor's share of a move since activation."""

    factor: str
    exposure: float = Field(
        description="The instrument's beta to this factor. Expanded detail only."
    )
    factor_move_pct: float = Field(
        description="The factor's own cumulative move since activation, as a percentage."
    )
    contribution: float = Field(
        description="Log-space contribution since activation: beta * factor move."
    )
    sentence: str = Field(
        description="One plain-language sentence, carrying no beta and no exposure value."
    )


class SymbolImpact(BaseModel):
    """`GET /impact/{symbol}` — the move since activation and what drove it."""

    symbol: str
    move_pct: float = Field(
        description="Headline move since activation: (close_now / close_at_activation - 1) * 100."
    )
    log_return: float = Field(
        description=(
            "log(close_now / close_at_activation). The contributions plus the residual "
            "reconcile with this to within 1e-6."
        )
    )
    contributions: list[FactorContribution] = Field(
        description="Ordered by descending absolute contribution."
    )
    residual: float = Field(description="The idiosyncratic term, in log space.")
    position_impact: float | None = Field(
        description=(
            "Impact on the holding in currency terms; null when the symbol is not held. "
            "Always present."
        )
    )


class PortfolioImpact(BaseModel):
    """`GET /impact/portfolio` — the same decomposition, by holding.

    Never resolved as an instrument lookup for a symbol named `portfolio`.
    """

    holdings: list[SymbolImpact] = Field(description="One breakdown per held position.")
    total_impact: float = Field(
        description="Total impact on the portfolio since activation, in currency."
    )
